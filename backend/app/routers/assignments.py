from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
import json
import os
from ..database import get_db
from ..models import StudentAssignment, Student, Team, QuestionGroup, Grade, Teacher
from ..schemas import (
    StudentAssignmentCreate, StudentAssignmentResponse, 
    StudentAssignmentFull, StudentAssignmentUpdate
)

router = APIRouter(prefix="/assignments", tags=["Student Assignments"])

# Backup directory
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backups")

def create_backup(db: Session, assignment_id: int = None):
    """Create a backup of all completed student results"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Get all assignments with grades
    assignments = db.query(StudentAssignment).options(
        joinedload(StudentAssignment.student),
        joinedload(StudentAssignment.team),
        joinedload(StudentAssignment.question_group),
        joinedload(StudentAssignment.grades)
    ).all()
    
    backup_data = {
        "backup_time": datetime.now().isoformat(),
        "total_students": len(assignments),
        "students": []
    }
    
    for a in assignments:
        if not a.student:
            continue
            
        student_data = {
            "id": a.id,
            "student_name": a.student.name,
            "student_birth_year": a.student.birth_year,
            "regular_teacher": a.student.regular_teacher,
            "team": a.team.name if a.team else None,
            "question_group": a.question_group.code if a.question_group else None,
            "q10_mark": a.q10_mark,
            "is_completed": a.is_completed,
            "exam_incomplete": a.exam_incomplete,
            "grades": []
        }
        
        for g in a.grades:
            teacher = db.query(Teacher).filter(Teacher.id == g.teacher_id).first()
            grade_data = {
                "teacher_id": g.teacher_id,
                "teacher_name": teacher.name if teacher else None,
                "teacher_position": teacher.position if teacher else None,
                "marks": {f"q{i}": getattr(g, f"q{i}_mark") for i in range(1, 10)},
                "total": g.total_q1_q9
            }
            student_data["grades"].append(grade_data)
        
        backup_data["students"].append(student_data)
    
    # Save with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"backup_{timestamp}.json")
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=2)
    
    # Also save a "latest" version
    latest_file = os.path.join(BACKUP_DIR, "backup_latest.json")
    with open(latest_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=2)
    
    return backup_file


@router.get("/", response_model=List[StudentAssignmentFull])
def get_all_assignments(
    team_id: Optional[int] = None,
    question_group_id: Optional[int] = None,
    exam_session_id: Optional[int] = None,
    is_completed: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all student assignments with optional filters"""
    query = db.query(StudentAssignment).options(
        joinedload(StudentAssignment.student),
        joinedload(StudentAssignment.team),
        joinedload(StudentAssignment.question_group),
        joinedload(StudentAssignment.exam_session)
    )
    
    if team_id:
        query = query.filter(StudentAssignment.team_id == team_id)
    if question_group_id:
        query = query.filter(StudentAssignment.question_group_id == question_group_id)
    if exam_session_id:
        query = query.filter(StudentAssignment.exam_session_id == exam_session_id)
    if is_completed is not None:
        query = query.filter(StudentAssignment.is_completed == is_completed)
    
    return query.all()


@router.post("/backup")
def manual_backup(db: Session = Depends(get_db)):
    """Manually trigger a backup of all student data"""
    try:
        backup_file = create_backup(db)
        return {
            "success": True,
            "message": "پاشەکەوت سەرکەوتوو بوو",
            "backup_file": backup_file,
            "backup_time": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")


@router.get("/backups")
def list_backups():
    """List all available backups"""
    if not os.path.exists(BACKUP_DIR):
        return {"backups": []}
    
    backups = []
    for f in os.listdir(BACKUP_DIR):
        if f.endswith('.json'):
            file_path = os.path.join(BACKUP_DIR, f)
            file_stat = os.stat(file_path)
            backups.append({
                "filename": f,
                "size_kb": round(file_stat.st_size / 1024, 2),
                "created_at": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
            })
    
    backups.sort(key=lambda x: x['created_at'], reverse=True)
    return {"backups": backups}


@router.post("/", response_model=StudentAssignmentFull)
def create_assignment(assignment: StudentAssignmentCreate, db: Session = Depends(get_db)):
    """Assign a student to a team and question group"""
    # Verify student exists
    student = db.query(Student).filter(Student.id == assignment.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Verify team exists
    team = db.query(Team).filter(Team.id == assignment.team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Verify question group exists
    qg = db.query(QuestionGroup).filter(QuestionGroup.id == assignment.question_group_id).first()
    if not qg:
        raise HTTPException(status_code=404, detail="Question group not found")
    
    # Check for duplicate assignment in same session
    existing = db.query(StudentAssignment).filter(
        StudentAssignment.student_id == assignment.student_id,
        StudentAssignment.exam_session_id == assignment.exam_session_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Student already assigned in this exam session"
        )
    
    db_assignment = StudentAssignment(**assignment.model_dump())
    
    # Copy student's Q10 mark if available
    if student.q10_mark is not None:
        db_assignment.q10_mark = student.q10_mark
        db_assignment.is_completed = True  # Mark as completed if Q10 is set
    
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    
    # Reload with relationships
    return db.query(StudentAssignment).options(
        joinedload(StudentAssignment.student),
        joinedload(StudentAssignment.team),
        joinedload(StudentAssignment.question_group),
        joinedload(StudentAssignment.exam_session)
    ).filter(StudentAssignment.id == db_assignment.id).first()


@router.get("/team/{team_id}", response_model=List[StudentAssignmentFull])
def get_team_assignments(
    team_id: int,
    pending_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get all assignments for a specific team (for teacher view)"""
    query = db.query(StudentAssignment).options(
        joinedload(StudentAssignment.student),
        joinedload(StudentAssignment.team),
        joinedload(StudentAssignment.question_group),
        joinedload(StudentAssignment.exam_session)
    ).filter(StudentAssignment.team_id == team_id)
    
    if pending_only:
        query = query.filter(StudentAssignment.is_completed == False)
    
    return query.all()


@router.get("/{assignment_id}", response_model=StudentAssignmentFull)
def get_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """Get a specific assignment"""
    assignment = db.query(StudentAssignment).options(
        joinedload(StudentAssignment.student),
        joinedload(StudentAssignment.team),
        joinedload(StudentAssignment.question_group),
        joinedload(StudentAssignment.exam_session)
    ).filter(StudentAssignment.id == assignment_id).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment


@router.put("/{assignment_id}/q10", response_model=StudentAssignmentFull)
def update_q10_mark(
    assignment_id: int,
    update: StudentAssignmentUpdate,
    db: Session = Depends(get_db)
):
    """Update Question 10 mark (superadmin only) - AUTO BACKUP ENABLED"""
    assignment = db.query(StudentAssignment).filter(
        StudentAssignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    if update.q10_mark is not None:
        if update.q10_mark < 0 or update.q10_mark > 10:
            raise HTTPException(
                status_code=400,
                detail="Q10 mark must be between 0 and 10"
            )
        assignment.q10_mark = update.q10_mark
        
        # Check if both teachers have graded
        if assignment.is_graded_teacher1 and assignment.is_graded_teacher2:
            assignment.is_completed = True
    
    db.commit()
    db.refresh(assignment)
    
    # AUTO BACKUP: Save backup every time Q10 is marked
    try:
        create_backup(db, assignment_id)
    except Exception as e:
        print(f"Backup error (non-critical): {e}")
    
    return db.query(StudentAssignment).options(
        joinedload(StudentAssignment.student),
        joinedload(StudentAssignment.team),
        joinedload(StudentAssignment.question_group),
        joinedload(StudentAssignment.exam_session)
    ).filter(StudentAssignment.id == assignment_id).first()


@router.put("/{assignment_id}", response_model=StudentAssignmentFull)
def update_assignment(
    assignment_id: int,
    team_id: Optional[int] = None,
    question_group_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Update assignment team or question group"""
    assignment = db.query(StudentAssignment).filter(
        StudentAssignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    if team_id is not None:
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        assignment.team_id = team_id
        # Reset grading status when team changes
        assignment.is_graded_teacher1 = False
        assignment.is_graded_teacher2 = False
        assignment.is_completed = False
        # Delete existing grades since teachers changed
        db.query(Grade).filter(Grade.assignment_id == assignment_id).delete()
    
    if question_group_id is not None:
        qg = db.query(QuestionGroup).filter(QuestionGroup.id == question_group_id).first()
        if not qg:
            raise HTTPException(status_code=404, detail="Question group not found")
        assignment.question_group_id = question_group_id
    
    db.commit()
    db.refresh(assignment)
    
    return db.query(StudentAssignment).options(
        joinedload(StudentAssignment.student),
        joinedload(StudentAssignment.team),
        joinedload(StudentAssignment.question_group),
        joinedload(StudentAssignment.exam_session)
    ).filter(StudentAssignment.id == assignment_id).first()


@router.delete("/{assignment_id}")
def delete_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """Delete an assignment"""
    assignment = db.query(StudentAssignment).filter(
        StudentAssignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Delete associated grades first
    db.query(Grade).filter(Grade.assignment_id == assignment_id).delete()
    
    db.delete(assignment)
    db.commit()
    return {"message": "Assignment deleted successfully"}


@router.put("/{assignment_id}/incomplete", response_model=StudentAssignmentFull)
def mark_exam_incomplete(
    assignment_id: int,
    db: Session = Depends(get_db)
):
    """Mark a student's exam as incomplete (stopped during examination)"""
    assignment = db.query(StudentAssignment).filter(
        StudentAssignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    assignment.exam_incomplete = True
    db.commit()
    db.refresh(assignment)
    
    return db.query(StudentAssignment).options(
        joinedload(StudentAssignment.student),
        joinedload(StudentAssignment.team),
        joinedload(StudentAssignment.question_group),
        joinedload(StudentAssignment.exam_session)
    ).filter(StudentAssignment.id == assignment_id).first()


@router.put("/{assignment_id}/complete", response_model=StudentAssignmentFull)
def mark_exam_complete(
    assignment_id: int,
    db: Session = Depends(get_db)
):
    """Undo incomplete status - mark student's exam as active again"""
    assignment = db.query(StudentAssignment).filter(
        StudentAssignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    assignment.exam_incomplete = False
    db.commit()
    db.refresh(assignment)
    
    return db.query(StudentAssignment).options(
        joinedload(StudentAssignment.student),
        joinedload(StudentAssignment.team),
        joinedload(StudentAssignment.question_group),
        joinedload(StudentAssignment.exam_session)
    ).filter(StudentAssignment.id == assignment_id).first()


@router.post("/sync-q10")
def sync_q10_from_students(db: Session = Depends(get_db)):
    """
    Sync Q10 marks from students to their assignments.
    Only syncs if assignment doesn't already have a Q10 mark and student has one (0-10).
    """
    # Get all assignments with their students
    assignments = db.query(StudentAssignment).options(
        joinedload(StudentAssignment.student)
    ).filter(StudentAssignment.q10_mark == None).all()
    
    synced_count = 0
    for assignment in assignments:
        if assignment.student and assignment.student.q10_mark is not None:
            # Validate Q10 is within range
            if 0 <= assignment.student.q10_mark <= 10:
                assignment.q10_mark = assignment.student.q10_mark
                # Mark as completed if both teachers have graded
                if assignment.is_graded_teacher1 and assignment.is_graded_teacher2:
                    assignment.is_completed = True
                synced_count += 1
    
    db.commit()
    
    return {
        "success": True,
        "synced_count": synced_count,
        "message": f"{synced_count} نمرەی Q10 هاوکاتکرا"
    }
