"""
Seed script to initialize the database with default data.
Run this after setting up the database to create:
- 4 Teams
- 8 Teachers (2 per team)
- 7 Question Groups (A-G) with sample mark structures
"""

from app.database import SessionLocal, engine, Base
from app.models import Team, Teacher, QuestionGroup, ExamSession
from datetime import datetime

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Check if data already exists
    if db.query(Team).count() > 0:
        print("Database already seeded. Skipping...")
    else:
        # Create Teams
        teams = [
            Team(name="Team 1"),
            Team(name="Team 2"),
            Team(name="Team 3"),
            Team(name="Team 4"),
        ]
        db.add_all(teams)
        db.commit()
        print("✓ Created 4 teams")

        # Create Teachers (2 per team)
        teachers = [
            Teacher(name="Teacher 1A", team_id=1, position=1),
            Teacher(name="Teacher 1B", team_id=1, position=2),
            Teacher(name="Teacher 2A", team_id=2, position=1),
            Teacher(name="Teacher 2B", team_id=2, position=2),
            Teacher(name="Teacher 3A", team_id=3, position=1),
            Teacher(name="Teacher 3B", team_id=3, position=2),
            Teacher(name="Teacher 4A", team_id=4, position=1),
            Teacher(name="Teacher 4B", team_id=4, position=2),
        ]
        db.add_all(teachers)
        db.commit()
        print("✓ Created 8 teachers")

        # Create Question Groups with different mark structures
        # Based on the official question weights from the CSV
        # Q10 is always 10 marks (graded by superadmin)
        question_groups = [
            QuestionGroup(
                name="Group A",
                code="A",
                marks_structure={
                    "q1": 4, "q2": 10, "q3": 8, "q4": 12,
                    "q5": 16, "q6": 10, "q7": 8, "q8": 9, "q9": 13
                },
                total_marks=90
            ),
            QuestionGroup(
                name="Group B",
                code="B",
                marks_structure={
                    "q1": 10, "q2": 8, "q3": 10, "q4": 14,
                    "q5": 9, "q6": 12, "q7": 7, "q8": 10, "q9": 10
                },
                total_marks=90
            ),
            QuestionGroup(
                name="Group C",
                code="C",
                marks_structure={
                    "q1": 10, "q2": 10, "q3": 9, "q4": 11,
                    "q5": 10, "q6": 17, "q7": 6, "q8": 8, "q9": 9
                },
                total_marks=90
            ),
            QuestionGroup(
                name="Group D",
                code="D",
                marks_structure={
                    "q1": 8, "q2": 8, "q3": 10, "q4": 24,
                    "q5": 4, "q6": 8, "q7": 8, "q8": 7, "q9": 13
                },
                total_marks=90
            ),
            QuestionGroup(
                name="Group E",
                code="E",
                marks_structure={
                    "q1": 8, "q2": 10, "q3": 10, "q4": 8,
                    "q5": 12, "q6": 5, "q7": 7, "q8": 19, "q9": 11
                },
                total_marks=90
            ),
            QuestionGroup(
                name="Group F",
                code="F",
                marks_structure={
                    "q1": 8, "q2": 7, "q3": 10, "q4": 23,
                    "q5": 8, "q6": 7, "q7": 13, "q8": 7, "q9": 7
                },
                total_marks=90
            ),
            QuestionGroup(
                name="Group G",
                code="G",
                marks_structure={
                    "q1": 8, "q2": 7, "q3": 10, "q4": 10,
                    "q5": 7, "q6": 9, "q7": 13, "q8": 5, "q9": 21
                },
                total_marks=90
            ),
        ]
        db.add_all(question_groups)
        db.commit()
        print("✓ Created 7 question groups (A-G)")

        # Create a default exam session
        session = ExamSession(
            name="January 2026 Exam",
            date=datetime(2026, 1, 1),
            is_active=True
        )
        db.add(session)
        db.commit()
        print("✓ Created default exam session")

        print("\n✅ Database seeded successfully!")

except Exception as e:
    print(f"Error seeding database: {e}")
    db.rollback()
finally:
    db.close()
