from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import QuestionGroup
from ..schemas import QuestionGroupCreate, QuestionGroupResponse

router = APIRouter(prefix="/question-groups", tags=["Question Groups"])


@router.get("/", response_model=List[QuestionGroupResponse])
def get_all_question_groups(db: Session = Depends(get_db)):
    """Get all question groups"""
    return db.query(QuestionGroup).order_by(QuestionGroup.code).all()


@router.post("/", response_model=QuestionGroupResponse)
def create_question_group(group: QuestionGroupCreate, db: Session = Depends(get_db)):
    """Create a new question group with marks structure"""
    # Validate marks structure has 9 questions
    required_keys = [f"q{i}" for i in range(1, 10)]
    for key in required_keys:
        if key not in group.marks_structure:
            raise HTTPException(
                status_code=400,
                detail=f"Missing {key} in marks_structure"
            )
    
    # Calculate total
    total = sum(group.marks_structure.values())
    
    db_group = QuestionGroup(
        name=group.name,
        code=group.code,
        marks_structure=group.marks_structure,
        total_marks=total
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group


@router.get("/{group_id}", response_model=QuestionGroupResponse)
def get_question_group(group_id: int, db: Session = Depends(get_db)):
    """Get a specific question group"""
    group = db.query(QuestionGroup).filter(QuestionGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Question group not found")
    return group


@router.put("/{group_id}", response_model=QuestionGroupResponse)
def update_question_group(group_id: int, group: QuestionGroupCreate, db: Session = Depends(get_db)):
    """Update a question group"""
    db_group = db.query(QuestionGroup).filter(QuestionGroup.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Question group not found")
    
    # Recalculate total
    total = sum(group.marks_structure.values())
    
    db_group.name = group.name
    db_group.code = group.code
    db_group.marks_structure = group.marks_structure
    db_group.total_marks = total
    
    db.commit()
    db.refresh(db_group)
    return db_group


@router.delete("/{group_id}")
def delete_question_group(group_id: int, db: Session = Depends(get_db)):
    """Delete a question group"""
    group = db.query(QuestionGroup).filter(QuestionGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Question group not found")
    db.delete(group)
    db.commit()
    return {"message": "Question group deleted successfully"}
