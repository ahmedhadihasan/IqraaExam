from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import engine, Base, get_db, SessionLocal
from .routers import teams, question_groups, students, exam_sessions, assignments, grades, reports
from .models import Grade, StudentAssignment, ExamSession, Team, Teacher, QuestionGroup
from datetime import datetime

# Create database tables
Base.metadata.create_all(bind=engine)

def seed_database():
    """Seed database with initial data if empty"""
    db = SessionLocal()
    try:
        # Only seed if no teams exist
        if db.query(Team).count() == 0:
            print("🌱 Seeding database...")
            
            # Create Teams
            teams_data = [
                Team(name="تیمی ١"),
                Team(name="تیمی ٢"),
                Team(name="تیمی ٣"),
                Team(name="تیمی ٤"),
            ]
            db.add_all(teams_data)
            db.commit()
            
            # Create Teachers (2 per team)
            teachers = [
                Teacher(name="مامۆستا ١", team_id=1, position=1),
                Teacher(name="مامۆستا ٢", team_id=1, position=2),
                Teacher(name="مامۆستا ٣", team_id=2, position=1),
                Teacher(name="مامۆستا ٤", team_id=2, position=2),
                Teacher(name="مامۆستا ٥", team_id=3, position=1),
                Teacher(name="مامۆستا ٦", team_id=3, position=2),
                Teacher(name="مامۆستا ٧", team_id=4, position=1),
                Teacher(name="مامۆستا ٨", team_id=4, position=2),
            ]
            db.add_all(teachers)
            db.commit()
            
            # Create Question Groups
            groups = [
                QuestionGroup(name="گروپی A", code="A", marks_structure={"q1": 4, "q2": 10, "q3": 8, "q4": 12, "q5": 16, "q6": 10, "q7": 8, "q8": 9, "q9": 13}, total_marks=90),
                QuestionGroup(name="گروپی B", code="B", marks_structure={"q1": 10, "q2": 8, "q3": 10, "q4": 14, "q5": 9, "q6": 12, "q7": 7, "q8": 10, "q9": 10}, total_marks=90),
                QuestionGroup(name="گروپی C", code="C", marks_structure={"q1": 10, "q2": 10, "q3": 9, "q4": 11, "q5": 10, "q6": 17, "q7": 6, "q8": 8, "q9": 9}, total_marks=90),
                QuestionGroup(name="گروپی D", code="D", marks_structure={"q1": 9, "q2": 9, "q3": 8, "q4": 10, "q5": 12, "q6": 14, "q7": 9, "q8": 9, "q9": 10}, total_marks=90),
            ]
            db.add_all(groups)
            db.commit()
            
            # Create active exam session
            session = ExamSession(name="دانیشتنی تاقیکردنەوە", date=datetime.now(), is_active=True, num_rooms=4, teachers_per_room=2)
            db.add(session)
            db.commit()
            
            print("✅ Database seeded successfully!")
        else:
            print("📦 Database already has data, skipping seed")
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

# Seed on startup
seed_database()

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
