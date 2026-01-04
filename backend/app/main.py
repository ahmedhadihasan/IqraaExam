from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from .routers import teams, question_groups, students, exam_sessions, assignments, grades, reports
from .models import Grade, StudentAssignment, ExamSession

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Iqraa Exam Grading System",
    description="API for managing exam grading with multiple teachers and question groups",
    version="1.0.0"
)

# CORS middleware for Svelte frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(teams.router)
app.include_router(question_groups.router)
app.include_router(students.router)
app.include_router(exam_sessions.router)
app.include_router(assignments.router)
app.include_router(grades.router)
app.include_router(reports.router)


@app.get("/")
def root():
    return {
        "message": "Iqraa Exam Grading System API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.delete("/reset-all-grades")
def reset_all_grades(db: Session = Depends(get_db)):
    """
    Delete all grades and assignments but keep students, teachers, teams, and question groups.
    This resets the system for a new exam session.
    """
    # Delete all grades first (foreign key constraint)
    db.query(Grade).delete()
    
    # Delete all assignments
    db.query(StudentAssignment).delete()
    
    # Deactivate all sessions
    db.query(ExamSession).update({"is_active": False})
    
    db.commit()
    
    return {
        "message": "هەموو نمرەکان و دابەشکردنەکان سڕانەوە",
        "success": True
    }


@app.delete("/reset-everything")
def reset_everything(db: Session = Depends(get_db)):
    """
    Delete everything except teams, teachers, and question groups.
    This includes students, grades, assignments, and sessions.
    """
    from .models import Student
    
    # Delete in order of dependencies
    db.query(Grade).delete()
    db.query(StudentAssignment).delete()
    db.query(ExamSession).delete()
    db.query(Student).delete()
    
    db.commit()
    
    return {
        "message": "هەموو شتەکان سڕانەوە (قوتابیان، نمرەکان، دانیشتنەکان)",
        "success": True
    }
