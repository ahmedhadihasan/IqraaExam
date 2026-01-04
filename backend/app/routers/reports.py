from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from io import StringIO
import csv
from ..database import get_db
from ..models import (
    Grade, StudentAssignment, Teacher, Student, 
    Team, QuestionGroup, ExamSession
)
from ..schemas import TeacherStats, StudentResult, ExportData

router = APIRouter(prefix="/reports", tags=["Reports & Export"])


@router.get("/teacher-stats", response_model=List[TeacherStats])
def get_teacher_statistics(
    exam_session_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get statistics for each teacher - grading count and average time."""
    teachers = db.query(Teacher).options(joinedload(Teacher.team)).all()
    
    stats = []
    for teacher in teachers:
        # Get grades for this teacher
        query = db.query(Grade).filter(Grade.teacher_id == teacher.id)
        
        if exam_session_id:
            query = query.join(StudentAssignment).filter(
                StudentAssignment.exam_session_id == exam_session_id
            )
        
        grades = query.all()
        
        # Calculate average grading time
        grading_times = []
        for g in grades:
            if g.grading_started_at and g.grading_finished_at:
                duration = (g.grading_finished_at - g.grading_started_at).total_seconds() / 60
                if duration > 0 and duration < 120:  # Ignore unrealistic times (>2 hours)
                    grading_times.append(duration)
        
        avg_time = round(sum(grading_times) / len(grading_times), 1) if grading_times else None
        
        stats.append(TeacherStats(
            teacher_id=teacher.id,
            teacher_name=teacher.name,
            team_name=teacher.team.name,
            total_students_graded=len([g for g in grades if g.total_q1_q9 is not None]),
            average_grading_minutes=avg_time
        ))
    
    return stats


@router.get("/student-results", response_model=List[StudentResult])
def get_student_results(
    team_id: Optional[int] = None,
    question_group_id: Optional[int] = None,
    exam_session_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all student results with averaged marks"""
    query = db.query(StudentAssignment).options(
        joinedload(StudentAssignment.student),
        joinedload(StudentAssignment.team),
        joinedload(StudentAssignment.question_group),
        joinedload(StudentAssignment.grades)
    )
    
    if team_id:
        query = query.filter(StudentAssignment.team_id == team_id)
    if question_group_id:
        query = query.filter(StudentAssignment.question_group_id == question_group_id)
    if exam_session_id:
        query = query.filter(StudentAssignment.exam_session_id == exam_session_id)
    
    assignments = query.all()
    
    results = []
    for assignment in assignments:
        # Skip if student or team or question_group is None (deleted)
        if not assignment.student or not assignment.team or not assignment.question_group:
            continue
            
        # Get grades from both teachers
        grades = assignment.grades
        teacher1_grade = None
        teacher2_grade = None
        
        for grade in grades:
            teacher = db.query(Teacher).filter(Teacher.id == grade.teacher_id).first()
            if teacher:
                if teacher.position == 1:
                    teacher1_grade = grade
                else:
                    teacher2_grade = grade
        
        # Build marks dictionaries
        teacher1_marks = {}
        teacher2_marks = {}
        average_marks = {}
        
        for i in range(1, 10):
            q_key = f"q{i}"
            t1_mark = getattr(teacher1_grade, f'q{i}_mark', None) if teacher1_grade else None
            t2_mark = getattr(teacher2_grade, f'q{i}_mark', None) if teacher2_grade else None
            
            teacher1_marks[q_key] = t1_mark
            teacher2_marks[q_key] = t2_mark
            
            # Calculate average
            if t1_mark is not None and t2_mark is not None:
                average_marks[q_key] = (t1_mark + t2_mark) / 2
            elif t1_mark is not None:
                average_marks[q_key] = t1_mark
            elif t2_mark is not None:
                average_marks[q_key] = t2_mark
            else:
                average_marks[q_key] = None
        
        # Calculate total average for Q1-Q9
        total_avg = sum([v for v in average_marks.values() if v is not None])
        
        # Calculate final total
        final_total = None
        if total_avg > 0 and assignment.q10_mark is not None:
            final_total = total_avg + assignment.q10_mark
        
        results.append(StudentResult(
            student_id=assignment.student.id,
            student_name=assignment.student.name,
            student_birth_year=assignment.student.birth_year,
            regular_teacher=assignment.student.regular_teacher,
            team_name=assignment.team.name,
            question_group=f"گرووپ {assignment.question_group.code}",
            teacher1_marks=teacher1_marks,
            teacher2_marks=teacher2_marks,
            average_marks=average_marks,
            total_average_q1_q9=round(total_avg, 2) if total_avg > 0 else None,
            q10_mark=assignment.q10_mark,
            final_total=round(final_total, 2) if final_total else None,
            exam_incomplete=assignment.exam_incomplete or False
        ))
    
    return results


@router.get("/export/csv")
def export_to_csv_detailed(
    exam_session_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Export DETAILED results to CSV - includes all marks from both teachers"""
    # Get all results
    query = db.query(StudentAssignment).options(
        joinedload(StudentAssignment.student),
        joinedload(StudentAssignment.team),
        joinedload(StudentAssignment.question_group),
        joinedload(StudentAssignment.grades)
    )
    
    if exam_session_id:
        query = query.filter(StudentAssignment.exam_session_id == exam_session_id)
    
    assignments = query.all()
    
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Header row (Kurdish headers)
    header = [
        'ناوی قوتابی', 'ساڵی لەدایکبوون', 'مامۆستای بابەت', 'تیم', 'گرووپی پرسیار', 'بارودۆخ',
        'م١ پ١', 'م١ پ٢', 'م١ پ٣', 'م١ پ٤', 'م١ پ٥', 'م١ پ٦', 'م١ پ٧', 'م١ پ٨', 'م١ پ٩',
        'م٢ پ١', 'م٢ پ٢', 'م٢ پ٣', 'م٢ پ٤', 'م٢ پ٥', 'م٢ پ٦', 'م٢ پ٧', 'م٢ پ٨', 'م٢ پ٩',
        'ناوەند پ١', 'ناوەند پ٢', 'ناوەند پ٣', 'ناوەند پ٤', 'ناوەند پ٥', 'ناوەند پ٦', 'ناوەند پ٧', 'ناوەند پ٨', 'ناوەند پ٩',
        'کۆی پ١-پ٩', 'پ١٠', 'کۆی گشتی'
    ]
    writer.writerow(header)
    
    for assignment in assignments:
        # Get grades
        grades = assignment.grades
        teacher1_grade = None
        teacher2_grade = None
        
        for grade in grades:
            teacher = db.query(Teacher).filter(Teacher.id == grade.teacher_id).first()
            if teacher:
                if teacher.position == 1:
                    teacher1_grade = grade
                else:
                    teacher2_grade = grade
        
        # Determine status
        if assignment.exam_incomplete:
            status = 'تەواونەکرد'
        elif assignment.is_completed:
            status = 'تەواوبوو'
        else:
            status = 'چاوەڕوان'
        
        # Build row
        row = [
            assignment.student.name,
            assignment.student.birth_year or '',
            assignment.student.regular_teacher or '',
            assignment.team.name,
            f"گرووپ {assignment.question_group.code}",
            status
        ]
        
        # Teacher 1 marks
        for i in range(1, 10):
            mark = getattr(teacher1_grade, f'q{i}_mark', None) if teacher1_grade else None
            row.append(mark if mark is not None else '')
        
        # Teacher 2 marks
        for i in range(1, 10):
            mark = getattr(teacher2_grade, f'q{i}_mark', None) if teacher2_grade else None
            row.append(mark if mark is not None else '')
        
        # Average marks
        avg_marks = []
        for i in range(1, 10):
            t1_mark = getattr(teacher1_grade, f'q{i}_mark', None) if teacher1_grade else None
            t2_mark = getattr(teacher2_grade, f'q{i}_mark', None) if teacher2_grade else None
            
            if t1_mark is not None and t2_mark is not None:
                avg = (t1_mark + t2_mark) / 2
            elif t1_mark is not None:
                avg = t1_mark
            elif t2_mark is not None:
                avg = t2_mark
            else:
                avg = None
            
            avg_marks.append(avg)
            row.append(round(avg, 2) if avg is not None else '')
        
        # Total average Q1-Q9
        total_avg = sum([a for a in avg_marks if a is not None])
        row.append(round(total_avg, 2) if total_avg > 0 else '')
        
        # Q10
        row.append(assignment.q10_mark if assignment.q10_mark is not None else '')
        
        # Final total
        if total_avg > 0 and assignment.q10_mark is not None:
            final_total = total_avg + assignment.q10_mark
            row.append(round(final_total, 2))
        else:
            row.append('')
        
        writer.writerow(row)
    
    output.seek(0)
    
    # Generate filename with date
    from datetime import datetime
    date_str = datetime.now().strftime('%Y-%m-%d')
    filename = f"exam_results_detailed_{date_str}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/export/csv-summary")
def export_to_csv_summary(
    exam_session_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Export SUMMARY results to CSV - student info and total mark only"""
    from datetime import datetime as dt
    
    query = db.query(StudentAssignment).options(
        joinedload(StudentAssignment.student),
        joinedload(StudentAssignment.team),
        joinedload(StudentAssignment.question_group),
        joinedload(StudentAssignment.grades)
    )
    
    if exam_session_id:
        query = query.filter(StudentAssignment.exam_session_id == exam_session_id)
    
    assignments = query.all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Simple header (Kurdish)
    header = ['ناوی قوتابی', 'ساڵی لەدایکبوون', 'مامۆستای بابەت', 'تیم', 'گرووپ', 'کۆی گشتی', 'بارودۆخ', 'دەرچوو/نەدەرچوو']
    writer.writerow(header)
    
    for assignment in assignments:
        if not assignment.student:
            continue
            
        # Calculate final total
        grades = assignment.grades
        teacher1_grade = None
        teacher2_grade = None
        
        for grade in grades:
            teacher = db.query(Teacher).filter(Teacher.id == grade.teacher_id).first()
            if teacher:
                if teacher.position == 1:
                    teacher1_grade = grade
                else:
                    teacher2_grade = grade
        
        # Calculate average Q1-Q9
        avg_marks = []
        for i in range(1, 10):
            t1_mark = getattr(teacher1_grade, f'q{i}_mark', None) if teacher1_grade else None
            t2_mark = getattr(teacher2_grade, f'q{i}_mark', None) if teacher2_grade else None
            
            if t1_mark is not None and t2_mark is not None:
                avg_marks.append((t1_mark + t2_mark) / 2)
            elif t1_mark is not None:
                avg_marks.append(t1_mark)
            elif t2_mark is not None:
                avg_marks.append(t2_mark)
        
        total_avg = sum(avg_marks) if avg_marks else 0
        
        # Final total
        final_total = None
        if total_avg > 0 and assignment.q10_mark is not None:
            final_total = total_avg + assignment.q10_mark
        
        # Status and pass/fail
        if assignment.exam_incomplete:
            status = 'تەواونەکرد'
            pass_fail = 'نەدەرچوو'
        elif final_total is not None:
            status = 'تەواوبوو'
            pass_fail = 'دەرچوو' if final_total >= 80 else 'نەدەرچوو'
        else:
            status = 'چاوەڕوان'
            pass_fail = '-'
        
        row = [
            assignment.student.name,
            assignment.student.birth_year or '',
            assignment.student.regular_teacher or '',
            assignment.team.name,
            f"گرووپ {assignment.question_group.code}",
            round(final_total, 2) if final_total else '',
            status,
            pass_fail
        ]
        writer.writerow(row)
    
    output.seek(0)
    
    date_str = dt.now().strftime('%Y-%m-%d')
    filename = f"exam_results_summary_{date_str}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/summary")
def get_summary(
    exam_session_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get overall summary statistics"""
    query = db.query(StudentAssignment)
    
    if exam_session_id:
        query = query.filter(StudentAssignment.exam_session_id == exam_session_id)
    
    assignments = query.all()
    
    total_students = len(assignments)
    completed = len([a for a in assignments if a.is_completed])
    pending_teacher1 = len([a for a in assignments if not a.is_graded_teacher1])
    pending_teacher2 = len([a for a in assignments if not a.is_graded_teacher2])
    pending_q10 = len([a for a in assignments if a.q10_mark is None])
    
    # Team breakdown
    teams = db.query(Team).all()
    team_stats = []
    for team in teams:
        team_assignments = [a for a in assignments if a.team_id == team.id]
        team_stats.append({
            "team_id": team.id,
            "team_name": team.name,
            "total": len(team_assignments),
            "completed": len([a for a in team_assignments if a.is_completed])
        })
    
    return {
        "total_students": total_students,
        "completed": completed,
        "pending": total_students - completed,
        "pending_teacher1_grading": pending_teacher1,
        "pending_teacher2_grading": pending_teacher2,
        "pending_q10": pending_q10,
        "team_breakdown": team_stats
    }
