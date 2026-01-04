from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import csv
import io
from ..database import get_db
from ..models import Student
from ..schemas import StudentCreate, StudentResponse, StudentUpdate

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/", response_model=List[StudentResponse])
def get_all_students(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all students with optional search and pagination"""
    query = db.query(Student)
    
    if search:
        query = query.filter(Student.name.ilike(f"%{search}%"))
    
    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=StudentResponse)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """Create a new student"""
    db_student = Student(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@router.post("/bulk", response_model=List[StudentResponse])
def create_students_bulk(students: List[StudentCreate], db: Session = Depends(get_db)):
    """Create multiple students at once"""
    db_students = [Student(**s.model_dump()) for s in students]
    db.add_all(db_students)
    db.commit()
    for s in db_students:
        db.refresh(s)
    return db_students


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    """Get a specific student"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student: StudentCreate, db: Session = Depends(get_db)):
    """Update a student"""
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    for key, value in student.model_dump().items():
        setattr(db_student, key, value)
    
    db.commit()
    db.refresh(db_student)
    return db_student


@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """Delete a student"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}


@router.post("/import-csv")
async def import_students_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Import students from CSV file
    Expected columns (Kurdish):
    - ناوی سییانی (name) - REQUIRED
    - ژمارەی تەلەفۆن (phone) - optional
    - ساڵی لەدایکبوون (birth_year) - optional
    - مامۆستای بابەت (regular_teacher) - optional
    - نمرەی پرسیاری ١٠ (q10_mark) - optional
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="فایلەکە دەبێت CSV بێت")
    
    content = await file.read()
    
    # Try different encodings
    for encoding in ['utf-8', 'utf-8-sig', 'cp1256', 'iso-8859-1']:
        try:
            decoded = content.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise HTTPException(status_code=400, detail="ناتوانرێت فایلەکە بخوێنرێتەوە")
    
    csv_reader = csv.DictReader(io.StringIO(decoded))
    
    # Column mapping (Kurdish to English)
    column_map = {
        'ناوی سییانی': 'name',
        'ژمارەی تەلەفۆن': 'phone',
        'ساڵی لەدایکبوون': 'birth_year',
        'تەمەن': 'birth_year',  # Also accept old column name
        'مامۆستای بابەت': 'regular_teacher',
        'نمرەی پرسیاری ١٠': 'q10_mark',
        # Also allow English column names
        'name': 'name',
        'phone': 'phone',
        'birth_year': 'birth_year',
        'age': 'birth_year',
        'regular_teacher': 'regular_teacher',
        'q10_mark': 'q10_mark',
        'q10': 'q10_mark'
    }
    
    students_created = []
    errors = []
    
    for row_num, row in enumerate(csv_reader, start=2):
        try:
            student_data = {}
            for csv_col, value in row.items():
                if csv_col and csv_col.strip() in column_map:
                    db_field = column_map[csv_col.strip()]
                    if db_field == 'birth_year' and value and value.strip():
                        try:
                            student_data[db_field] = int(value.strip())
                        except ValueError:
                            pass  # Invalid birth year, skip
                    elif db_field == 'q10_mark' and value and value.strip():
                        try:
                            q10_val = float(value.strip())
                            # Validate Q10 must be between 0 and 10
                            if 0 <= q10_val <= 10:
                                student_data[db_field] = q10_val
                        except ValueError:
                            pass  # Invalid Q10, skip
                    else:
                        clean_value = value.strip() if value else None
                        if clean_value:  # Only set if not empty
                            student_data[db_field] = clean_value
            
            # Only name is required
            if not student_data.get('name'):
                errors.append(f"ڕیزی {row_num}: ناو بەتاڵە")
                continue  # Skip this row but continue with others
            
            db_student = Student(**student_data)
            db.add(db_student)
            db.commit()
            db.refresh(db_student)
            students_created.append({
                "id": db_student.id,
                "name": db_student.name
            })
        except Exception as e:
            db.rollback()  # Rollback only this row
            errors.append(f"ڕیزی {row_num}: {str(e)}")
            continue  # Continue with next rows
    
    return {
        "message": f"{len(students_created)} قوتابی زیادکرا",
        "students_created": students_created,
        "errors": errors
    }
    
    return {
        "message": f"{len(students_created)} قوتابی زیادکرا",
        "students_created": students_created,
        "errors": errors
    }


@router.delete("/")
def delete_all_students(db: Session = Depends(get_db)):
    """Delete all students"""
    db.query(Student).delete()
    db.commit()
    return {"message": "هەموو قوتابییەکان سڕانەوە"}
