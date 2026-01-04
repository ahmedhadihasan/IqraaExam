from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import ExamSession
from ..schemas import ExamSessionCreate, ExamSessionResponse, ExamSessionUpdate

router = APIRouter(prefix="/exam-sessions", tags=["Exam Sessions"])


@router.get("/", response_model=List[ExamSessionResponse])
def get_all_exam_sessions(
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get all exam sessions"""
    query = db.query(ExamSession)
    if active_only:
        query = query.filter(ExamSession.is_active == True)
    return query.order_by(ExamSession.date.desc()).all()


@router.post("/", response_model=ExamSessionResponse)
def create_exam_session(session: ExamSessionCreate, db: Session = Depends(get_db)):
    """Create a new exam session"""
    db_session = ExamSession(**session.model_dump())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


@router.get("/active", response_model=Optional[ExamSessionResponse])
def get_active_session(db: Session = Depends(get_db)):
    """Get the currently active exam session"""
    session = db.query(ExamSession).filter(ExamSession.is_active == True).first()
    return session


@router.get("/{session_id}", response_model=ExamSessionResponse)
def get_exam_session(session_id: int, db: Session = Depends(get_db)):
    """Get a specific exam session"""
    session = db.query(ExamSession).filter(ExamSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Exam session not found")
    return session


@router.put("/{session_id}", response_model=ExamSessionResponse)
def update_exam_session(session_id: int, session: ExamSessionUpdate, db: Session = Depends(get_db)):
    """Update an exam session"""
    db_session = db.query(ExamSession).filter(ExamSession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Exam session not found")
    
    update_data = session.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(db_session, key, value)
    
    db.commit()
    db.refresh(db_session)
    return db_session


@router.put("/{session_id}/activate", response_model=ExamSessionResponse)
def activate_session(session_id: int, db: Session = Depends(get_db)):
    """Set a session as active (deactivates all others)"""
    # Deactivate all sessions
    db.query(ExamSession).update({ExamSession.is_active: False})
    
    # Activate the specified session
    session = db.query(ExamSession).filter(ExamSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Exam session not found")
    
    session.is_active = True
    db.commit()
    db.refresh(session)
    return session


@router.delete("/{session_id}")
def delete_exam_session(session_id: int, db: Session = Depends(get_db)):
    """Delete an exam session"""
    session = db.query(ExamSession).filter(ExamSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Exam session not found")
    db.delete(session)
    db.commit()
    return {"message": "Exam session deleted successfully"}
