from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from ..database import get_db
from ..models import Grade, StudentAssignment, Teacher, QuestionGroup
from ..schemas import GradeCreate, GradeUpdate, GradeResponse

router = APIRouter(prefix="/grades", tags=["Grades"])


@router.get("/assignment/{assignment_id}", response_model=List[GradeResponse])
def get_assignment_grades(assignment_id: int, db: Session = Depends(get_db)):
    """Get all grades for a specific assignment"""
    grades = db.query(Grade).filter(Grade.assignment_id == assignment_id).all()
    return grades


@router.get("/teacher/{teacher_id}", response_model=List[GradeResponse])
def get_teacher_grades(teacher_id: int, db: Session = Depends(get_db)):
    """Get all grades given by a specific teacher"""
    grades = db.query(Grade).filter(Grade.teacher_id == teacher_id).all()
    return grades


@router.post("/start-grading")
def start_grading(assignment_id: int, teacher_id: int, db: Session = Depends(get_db)):
    """Mark when a teacher starts grading a student (for time tracking)"""
    # Check if grade already exists
    existing_grade = db.query(Grade).filter(
        Grade.assignment_id == assignment_id,
        Grade.teacher_id == teacher_id
    ).first()
    
    if existing_grade:
        # Only update start time if not already set
        if not existing_grade.grading_started_at:
            existing_grade.grading_started_at = datetime.utcnow()
            db.commit()
        return {"message": "Grading already started", "started_at": existing_grade.grading_started_at}
    
    # Create a new grade entry with just the start time
    new_grade = Grade(
        assignment_id=assignment_id,
        teacher_id=teacher_id,
        grading_started_at=datetime.utcnow()
    )
    db.add(new_grade)
    db.commit()
    db.refresh(new_grade)
    
    return {"message": "Grading started", "started_at": new_grade.grading_started_at}


@router.post("/", response_model=GradeResponse)
def create_or_update_grade(grade_data: GradeCreate, db: Session = Depends(get_db)):
    """Create or update a grade for an assignment by a teacher"""
    # Verify assignment exists
    assignment = db.query(StudentAssignment).options(
        joinedload(StudentAssignment.question_group)
    ).filter(StudentAssignment.id == grade_data.assignment_id).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Verify teacher exists and is in the correct team
    teacher = db.query(Teacher).filter(Teacher.id == grade_data.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    if teacher.team_id != assignment.team_id:
        raise HTTPException(
            status_code=403,
            detail="Teacher is not in the assigned team for this student"
        )
    
    # Get question group marks structure for validation
    marks_structure = assignment.question_group.marks_structure
    
    # Validate marks against max marks
    grade_dict = grade_data.model_dump()
    for i in range(1, 10):
        mark_key = f"q{i}_mark"
        max_key = f"q{i}"
        if grade_dict.get(mark_key) is not None:
            if grade_dict[mark_key] < 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Q{i} mark cannot be negative"
                )
            if grade_dict[mark_key] > marks_structure.get(max_key, 0):
                raise HTTPException(
                    status_code=400,
                    detail=f"Q{i} mark cannot exceed {marks_structure.get(max_key, 0)}"
                )
    
    # Check if grade already exists for this assignment/teacher
    existing_grade = db.query(Grade).filter(
        Grade.assignment_id == grade_data.assignment_id,
        Grade.teacher_id == grade_data.teacher_id
    ).first()
    
    if existing_grade:
        # Update existing grade
        for key, value in grade_dict.items():
            if key not in ['assignment_id', 'teacher_id'] and value is not None:
                setattr(existing_grade, key, value)
        
        # Calculate total
        total = sum([
            getattr(existing_grade, f'q{i}_mark') or 0
            for i in range(1, 10)
        ])
        existing_grade.total_q1_q9 = total
        existing_grade.grading_finished_at = datetime.utcnow()
        
        db.commit()
        db.refresh(existing_grade)
        db_grade = existing_grade
    else:
        # Create new grade
        db_grade = Grade(**grade_dict)
        
        # Calculate total
        total = sum([
            getattr(db_grade, f'q{i}_mark') or 0
            for i in range(1, 10)
        ])
        db_grade.total_q1_q9 = total
        db_grade.grading_started_at = datetime.utcnow()
        db_grade.grading_finished_at = datetime.utcnow()
        
        db.add(db_grade)
        db.commit()
        db.refresh(db_grade)
    
    # Update assignment grading status
    if teacher.position == 1:
        assignment.is_graded_teacher1 = True
    else:
        assignment.is_graded_teacher2 = True
    
    # Check if both teachers have graded and Q10 is set
    if assignment.is_graded_teacher1 and assignment.is_graded_teacher2 and assignment.q10_mark is not None:
        assignment.is_completed = True
    
    db.commit()
    
    return db_grade


@router.put("/{grade_id}", response_model=GradeResponse)
def update_grade(grade_id: int, grade_data: GradeUpdate, db: Session = Depends(get_db)):
    """Update an existing grade"""
    db_grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not db_grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    
    # Get assignment for validation
    assignment = db.query(StudentAssignment).options(
        joinedload(StudentAssignment.question_group)
    ).filter(StudentAssignment.id == db_grade.assignment_id).first()
    
    marks_structure = assignment.question_group.marks_structure
    
    # Update and validate
    for key, value in grade_data.model_dump().items():
        if value is not None:
            # Validate against max marks
            q_num = key.replace('_mark', '').replace('q', '')
            max_key = f"q{q_num}"
            if value < 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Q{q_num} mark cannot be negative"
                )
            if value > marks_structure.get(max_key, 0):
                raise HTTPException(
                    status_code=400,
                    detail=f"Q{q_num} mark cannot exceed {marks_structure.get(max_key, 0)}"
                )
            setattr(db_grade, key, value)
    
    # Recalculate total
    total = sum([
        getattr(db_grade, f'q{i}_mark') or 0
        for i in range(1, 10)
    ])
    db_grade.total_q1_q9 = total
    
    db.commit()
    db.refresh(db_grade)
    return db_grade


@router.get("/{grade_id}", response_model=GradeResponse)
def get_grade(grade_id: int, db: Session = Depends(get_db)):
    """Get a specific grade"""
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    return grade


@router.delete("/{grade_id}")
def delete_grade(grade_id: int, db: Session = Depends(get_db)):
    """Delete a grade"""
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    db.delete(grade)
    db.commit()
    return {"message": "Grade deleted successfully"}
