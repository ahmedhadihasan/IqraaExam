from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


# ========== Team Schemas ==========
class TeamBase(BaseModel):
    name: str

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseModel):
    name: Optional[str] = None

class TeamResponse(TeamBase):
    id: int
    created_at: datetime
    teachers: List["TeacherResponse"] = []
    
    class Config:
        from_attributes = True


# ========== Teacher Schemas ==========
class TeacherBase(BaseModel):
    name: str
    team_id: int
    position: int  # 1 or 2

class TeacherCreate(TeacherBase):
    pass

class TeacherUpdate(BaseModel):
    name: Optional[str] = None
    team_id: Optional[int] = None
    position: Optional[int] = None

class TeacherResponse(TeacherBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class TeacherWithTeam(TeacherResponse):
    team: TeamResponse


# ========== Question Group Schemas ==========
class QuestionGroupBase(BaseModel):
    name: str
    code: str
    marks_structure: Dict[str, int]  # {"q1": 12, "q2": 7, ...}
    total_marks: int = 90

class QuestionGroupCreate(QuestionGroupBase):
    pass

class QuestionGroupUpdate(BaseModel):
    name: Optional[str] = None
    marks_structure: Optional[Dict[str, int]] = None
    total_marks: Optional[int] = None

class QuestionGroupResponse(QuestionGroupBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== Exam Session Schemas ==========
class ExamSessionBase(BaseModel):
    name: str
    date: datetime
    num_rooms: int = 4  # Number of rooms/teams
    teachers_per_room: int = 2  # 2 or 3 teachers per room

class ExamSessionCreate(ExamSessionBase):
    pass

class ExamSessionUpdate(BaseModel):
    name: Optional[str] = None
    date: Optional[datetime] = None
    num_rooms: Optional[int] = None
    teachers_per_room: Optional[int] = None

class ExamSessionResponse(ExamSessionBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== Student Schemas ==========
class StudentBase(BaseModel):
    name: str  # ناوی سییانی - required
    phone: Optional[str] = None  # ژمارەی تەلەفۆن
    birth_year: Optional[int] = None  # ساڵی لەدایکبوون
    regular_teacher: Optional[str] = None  # مامۆستای بابەت
    q10_mark: Optional[float] = None  # نمرەی پرسیاری ڡڠ
    is_second_term: Optional[bool] = False  # قوتابی وەرزی دووەم
    previous_question_group: Optional[str] = None  # گرووپی پرسیاری پێشووی

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    birth_year: Optional[int] = None
    phone: Optional[str] = None
    regular_teacher: Optional[str] = None
    q10_mark: Optional[float] = None
    is_second_term: Optional[bool] = None
    previous_question_group: Optional[str] = None

class StudentResponse(BaseModel):
    id: int
    name: str
    phone: Optional[str] = None
    birth_year: Optional[int] = None
    regular_teacher: Optional[str] = None
    q10_mark: Optional[float] = None
    is_second_term: Optional[bool] = False
    previous_question_group: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# CSV Import
class StudentCSVRow(BaseModel):
    name: str  # ناوی سییانی - required
    phone: Optional[str] = None  # ژمارەی تەلەفۆن
    birth_year: Optional[int] = None  # ساڵی لەدایکبوون
    regular_teacher: Optional[str] = None  # مامۆستای بابەت
    q10_mark: Optional[float] = None  # نمرەی پرسیاری ڡڠ
    is_second_term: Optional[bool] = False  # قوتابی وەرزی دووەم
    previous_question_group: Optional[str] = None  # گرووپی پرسیاری پێشووی


# ========== Student Assignment Schemas ==========
class StudentAssignmentBase(BaseModel):
    student_id: int
    team_id: int
    question_group_id: int
    exam_session_id: Optional[int] = None

class StudentAssignmentCreate(StudentAssignmentBase):
    pass

class StudentAssignmentUpdate(BaseModel):
    q10_mark: Optional[float] = None

class StudentAssignmentResponse(StudentAssignmentBase):
    id: int
    q10_mark: Optional[float]
    is_graded_teacher1: bool
    is_graded_teacher2: bool
    is_completed: bool
    exam_incomplete: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True

class StudentAssignmentFull(StudentAssignmentResponse):
    student: StudentResponse
    team: TeamResponse
    question_group: QuestionGroupResponse
    exam_session: Optional[ExamSessionResponse]


# ========== Grade Schemas ==========
class GradeBase(BaseModel):
    assignment_id: int
    teacher_id: int

class GradeCreate(GradeBase):
    q1_mark: Optional[float] = None
    q2_mark: Optional[float] = None
    q3_mark: Optional[float] = None
    q4_mark: Optional[float] = None
    q5_mark: Optional[float] = None
    q6_mark: Optional[float] = None
    q7_mark: Optional[float] = None
    q8_mark: Optional[float] = None
    q9_mark: Optional[float] = None

class GradeUpdate(BaseModel):
    q1_mark: Optional[float] = None
    q2_mark: Optional[float] = None
    q3_mark: Optional[float] = None
    q4_mark: Optional[float] = None
    q5_mark: Optional[float] = None
    q6_mark: Optional[float] = None
    q7_mark: Optional[float] = None
    q8_mark: Optional[float] = None
    q9_mark: Optional[float] = None

class GradeResponse(GradeBase):
    id: int
    q1_mark: Optional[float]
    q2_mark: Optional[float]
    q3_mark: Optional[float]
    q4_mark: Optional[float]
    q5_mark: Optional[float]
    q6_mark: Optional[float]
    q7_mark: Optional[float]
    q8_mark: Optional[float]
    q9_mark: Optional[float]
    total_q1_q9: Optional[float]
    grading_started_at: Optional[datetime] = None
    grading_finished_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ========== Dashboard/Report Schemas ==========
class TeacherStats(BaseModel):
    teacher_id: int
    teacher_name: str
    team_name: str
    total_students_graded: int
    average_grading_minutes: Optional[float] = None  # Average time to grade each student

class StudentResult(BaseModel):
    student_id: int
    student_name: str
    student_birth_year: Optional[int] = None
    regular_teacher: Optional[str] = None
    team_name: str
    question_group: str
    teacher1_marks: Dict[str, Optional[float]]
    teacher2_marks: Dict[str, Optional[float]]
    teacher3_marks: Optional[Dict[str, Optional[float]]] = None
    average_marks: Dict[str, Optional[float]]
    total_average_q1_q9: Optional[float]
    q10_mark: Optional[float]
    final_total: Optional[float]
    exam_incomplete: bool = False

class ExportData(BaseModel):
    student_name: str
    student_birth_year: Optional[int] = None
    regular_teacher: Optional[str] = None
    team: str
    question_group: str
    t1_q1: Optional[float]
    t1_q2: Optional[float]
    t1_q3: Optional[float]
    t1_q4: Optional[float]
    t1_q5: Optional[float]
    t1_q6: Optional[float]
    t1_q7: Optional[float]
    t1_q8: Optional[float]
    t1_q9: Optional[float]
    t2_q1: Optional[float]
    t2_q2: Optional[float]
    t2_q3: Optional[float]
    t2_q4: Optional[float]
    t2_q5: Optional[float]
    t2_q6: Optional[float]
    t2_q7: Optional[float]
    t2_q8: Optional[float]
    t2_q9: Optional[float]
    avg_q1: Optional[float]
    avg_q2: Optional[float]
    avg_q3: Optional[float]
    avg_q4: Optional[float]
    avg_q5: Optional[float]
    avg_q6: Optional[float]
    avg_q7: Optional[float]
    avg_q8: Optional[float]
    avg_q9: Optional[float]
    total_avg_q1_q9: Optional[float]
    q10: Optional[float]
    final_total: Optional[float]


# Rebuild models to resolve forward references
TeamResponse.model_rebuild()
