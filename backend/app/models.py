from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Team(Base):
    """Teams (1-4) that teachers belong to"""
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # Team 1, Team 2, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    teachers = relationship("Teacher", back_populates="team")
    student_assignments = relationship("StudentAssignment", back_populates="team")


class Teacher(Base):
    """Teachers - 8 total, 2 per team"""
    __tablename__ = "teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    position = Column(Integer, nullable=False)  # 1 or 2 (Teacher 1 or Teacher 2 in team)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    team = relationship("Team", back_populates="teachers")
    grades = relationship("Grade", back_populates="teacher")


class QuestionGroup(Base):
    """Question Groups (A-G) with their mark structure"""
    __tablename__ = "question_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)  # Group A, Group B, etc.
    code = Column(String(1), unique=True, nullable=False)  # A, B, C, D, E, F, G
    # JSON structure: {"q1": 12, "q2": 7, "q3": 10, ...}
    marks_structure = Column(JSON, nullable=False)
    total_marks = Column(Integer, nullable=False, default=90)  # Q1-Q9 total (Q10 is always 10)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    student_assignments = relationship("StudentAssignment", back_populates="question_group")


class ExamSession(Base):
    """Exam Sessions (optional) - for organizing monthly exams"""
    __tablename__ = "exam_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # January 2026 Exam
    date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    num_rooms = Column(Integer, default=4)  # Number of rooms/teams (default 4)
    teachers_per_room = Column(Integer, default=2)  # 2 or 3 teachers per room
    created_at = Column(DateTime, default=datetime.utcnow)
    
    student_assignments = relationship("StudentAssignment", back_populates="exam_session")


class Student(Base):
    """Students master list"""
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # ناوی سییانی
    phone = Column(String(20), nullable=True)  # ژمارەی تەلەفۆن
    birth_year = Column(Integer, nullable=True)  # ساڵی لەدایکبوون
    regular_teacher = Column(String(100), nullable=True)  # مامۆستای بابەت
    q10_mark = Column(Float, nullable=True)  # نمرەی پرسیاری ڡڠ (imported from CSV or set manually)
    
    # Second term / retake tracking
    is_second_term = Column(Boolean, default=False)  # قوتابی وەرزی دووەم - retaking the exam
    previous_question_group = Column(String(10), nullable=True)  # گرووپی پرسیاری پێشووی - previous group code (A-G)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    assignments = relationship("StudentAssignment", back_populates="student")


class StudentAssignment(Base):
    """Assignment of student to team and question group for a specific exam"""
    __tablename__ = "student_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    question_group_id = Column(Integer, ForeignKey("question_groups.id"), nullable=False)
    exam_session_id = Column(Integer, ForeignKey("exam_sessions.id"), nullable=True)
    
    # Question 10 mark (only by superadmin)
    q10_mark = Column(Float, nullable=True)
    
    # Status tracking
    is_graded_teacher1 = Column(Boolean, default=False)
    is_graded_teacher2 = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False)  # Q10 added
    exam_incomplete = Column(Boolean, default=False)  # Student failed/stopped during exam
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    student = relationship("Student", back_populates="assignments")
    team = relationship("Team", back_populates="student_assignments")
    question_group = relationship("QuestionGroup", back_populates="student_assignments")
    exam_session = relationship("ExamSession", back_populates="student_assignments")
    grades = relationship("Grade", back_populates="assignment")


class Grade(Base):
    """Individual grades from each teacher"""
    __tablename__ = "grades"
    
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("student_assignments.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    
    # Marks for Q1-Q9
    q1_mark = Column(Float, nullable=True)
    q2_mark = Column(Float, nullable=True)
    q3_mark = Column(Float, nullable=True)
    q4_mark = Column(Float, nullable=True)
    q5_mark = Column(Float, nullable=True)
    q6_mark = Column(Float, nullable=True)
    q7_mark = Column(Float, nullable=True)
    q8_mark = Column(Float, nullable=True)
    q9_mark = Column(Float, nullable=True)
    
    total_q1_q9 = Column(Float, nullable=True)  # Sum of Q1-Q9
    
    # Time tracking
    grading_started_at = Column(DateTime, nullable=True)  # When teacher started grading
    grading_finished_at = Column(DateTime, nullable=True)  # When teacher submitted
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    assignment = relationship("StudentAssignment", back_populates="grades")
    teacher = relationship("Teacher", back_populates="grades")
