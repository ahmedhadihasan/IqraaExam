from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Team, Teacher, ExamSession
from ..schemas import (
    TeamCreate, TeamResponse,
    TeacherCreate, TeacherResponse, TeacherWithTeam
)

router = APIRouter(prefix="/teams", tags=["Teams & Teachers"])


# ========== Team Endpoints ==========
@router.get("/", response_model=List[TeamResponse])
def get_all_teams(db: Session = Depends(get_db)):
    """Get all teams"""
    return db.query(Team).all()


@router.get("/for-active-session", response_model=List[TeamResponse])
def get_teams_for_active_session(db: Session = Depends(get_db)):
    """Get teams based on the active session's num_rooms setting"""
    # Get active session
    active_session = db.query(ExamSession).filter(ExamSession.is_active == True).first()
    
    if active_session:
        num_rooms = active_session.num_rooms or 4
        # Get only the first N teams based on num_rooms
        teams = db.query(Team).order_by(Team.id).limit(num_rooms).all()
        return teams
    else:
        # No active session, return all teams
        return db.query(Team).all()


@router.post("/", response_model=TeamResponse)
def create_team(team: TeamCreate, db: Session = Depends(get_db)):
    """Create a new team"""
    db_team = Team(**team.model_dump())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(team_id: int, db: Session = Depends(get_db)):
    """Get a specific team"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.put("/{team_id}", response_model=TeamResponse)
def update_team(team_id: int, team: TeamCreate, db: Session = Depends(get_db)):
    """Update a team"""
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    for key, value in team.model_dump().items():
        setattr(db_team, key, value)
    
    db.commit()
    db.refresh(db_team)
    return db_team


@router.delete("/{team_id}")
def delete_team(team_id: int, db: Session = Depends(get_db)):
    """Delete a team"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    db.delete(team)
    db.commit()
    return {"message": "Team deleted successfully"}


# ========== Teacher Endpoints ==========
@router.get("/teachers/all", response_model=List[TeacherWithTeam])
def get_all_teachers(db: Session = Depends(get_db)):
    """Get all teachers with their team info"""
    teachers = db.query(Teacher).all()
    return teachers


@router.get("/teachers/for-active-session", response_model=List[TeacherWithTeam])
def get_teachers_for_active_session(db: Session = Depends(get_db)):
    """Get teachers filtered by active session's num_rooms and teachers_per_room"""
    active_session = db.query(ExamSession).filter(ExamSession.is_active == True).first()
    
    if active_session:
        num_rooms = active_session.num_rooms or 4
        teachers_per_room = active_session.teachers_per_room or 2
        
        # Get team IDs for the active session (first N teams)
        team_ids = [t.id for t in db.query(Team).order_by(Team.id).limit(num_rooms).all()]
        
        # Get teachers for those teams, filtered by position
        teachers = db.query(Teacher).filter(
            Teacher.team_id.in_(team_ids),
            Teacher.position <= teachers_per_room
        ).all()
        return teachers
    else:
        # No active session, return all teachers
        return db.query(Teacher).all()


@router.get("/{team_id}/teachers", response_model=List[TeacherResponse])
def get_team_teachers(team_id: int, db: Session = Depends(get_db)):
    """Get all teachers in a specific team"""
    teachers = db.query(Teacher).filter(Teacher.team_id == team_id).all()
    return teachers


@router.post("/teachers", response_model=TeacherResponse)
def create_teacher(teacher: TeacherCreate, db: Session = Depends(get_db)):
    """Create a new teacher"""
    # Verify team exists
    team = db.query(Team).filter(Team.id == teacher.team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check if position is valid (1, 2, or 3 for 3-teacher sessions)
    if teacher.position not in [1, 2, 3]:
        raise HTTPException(status_code=400, detail="Position must be 1, 2, or 3")
    
    # Check if position is already taken in this team
    existing = db.query(Teacher).filter(
        Teacher.team_id == teacher.team_id,
        Teacher.position == teacher.position
    ).first()
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Position {teacher.position} is already taken in this team"
        )
    
    db_teacher = Teacher(**teacher.model_dump())
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher


@router.get("/teachers/{teacher_id}", response_model=TeacherWithTeam)
def get_teacher(teacher_id: int, db: Session = Depends(get_db)):
    """Get a specific teacher"""
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher


@router.put("/teachers/{teacher_id}", response_model=TeacherResponse)
def update_teacher(teacher_id: int, teacher: TeacherCreate, db: Session = Depends(get_db)):
    """Update a teacher"""
    db_teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    for key, value in teacher.model_dump().items():
        setattr(db_teacher, key, value)
    
    db.commit()
    db.refresh(db_teacher)
    return db_teacher


@router.delete("/teachers/{teacher_id}")
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    """Delete a teacher"""
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    db.delete(teacher)
    db.commit()
    return {"message": "Teacher deleted successfully"}
