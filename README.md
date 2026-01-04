# Iqraa Exam Grading System

A comprehensive exam grading system built with **Svelte** (frontend), **Python FastAPI** (backend), and **PostgreSQL** (database).

## Features

- **Superadmin Dashboard**
  - Manage students, teachers, teams, and question groups
  - Assign students to teams and question groups
  - Add Question 10 marks (final assessment)
  - View all results and statistics
  - Export data to CSV

- **Teacher Interface**
  - Link-based access (no login required)
  - Grade assigned students (Q1-Q9)
  - Real-time form validation
  - See grading status

- **Question Groups**
  - 7 configurable question groups (A-G)
  - Each group has 9 questions with different mark distributions
  - Total of 90 marks for Q1-Q9, plus 10 marks for Q10 = 100 total

- **Real-time Grading**
  - Both teachers in a team grade independently
  - System calculates average of both teachers' marks
  - Superadmin adds final Q10 mark

## Tech Stack

- **Frontend**: SvelteKit
- **Backend**: Python FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy

## Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+

### 1. Database Setup

```bash
# Create PostgreSQL database
createdb iqraa_exam

# Or using psql
psql -U postgres
CREATE DATABASE iqraa_exam;
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your database credentials

# Run database seed (creates initial data)
python seed.py

# Start the server
uvicorn app.main:app --reload --port 8000
```

The API will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at: http://localhost:5173

## Project Structure

```
Iqraa/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app entry
│   │   ├── database.py      # Database connection
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   └── routers/
│   │       ├── teams.py
│   │       ├── students.py
│   │       ├── question_groups.py
│   │       ├── exam_sessions.py
│   │       ├── assignments.py
│   │       ├── grades.py
│   │       └── reports.py
│   ├── seed.py              # Database seeder
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/
    ├── src/
    │   ├── lib/
    │   │   ├── api.js       # API client
    │   │   └── stores.js    # Svelte stores
    │   ├── routes/
    │   │   ├── +layout.svelte
    │   │   ├── +page.svelte          # Home (role selection)
    │   │   ├── admin/
    │   │   │   ├── +layout.svelte    # Admin layout
    │   │   │   ├── +page.svelte      # Dashboard
    │   │   │   ├── students/
    │   │   │   ├── assign/
    │   │   │   ├── q10/
    │   │   │   ├── results/
    │   │   │   ├── teachers/
    │   │   │   ├── groups/
    │   │   │   └── sessions/
    │   │   └── teacher/
    │   │       └── [id]/+page.svelte  # Teacher grading
    │   ├── app.css
    │   └── app.html
    ├── package.json
    └── svelte.config.js
```

## Workflow

1. **Student arrives** → Superadmin adds student to system
2. **Assignment** → Superadmin assigns student to a Team + Question Group
3. **Grading** → Student goes to team room, both teachers grade Q1-Q9
4. **Final Mark** → Superadmin adds Q10 mark
5. **Results** → View final scores (average of both teachers + Q10)

## API Endpoints

### Teams & Teachers
- `GET /teams/` - List all teams
- `GET /teams/teachers/all` - List all teachers
- `POST /teams/teachers` - Create teacher

### Students
- `GET /students/` - List all students
- `POST /students/` - Create student
- `POST /students/bulk` - Create multiple students

### Question Groups
- `GET /question-groups/` - List all groups
- `POST /question-groups/` - Create group
- `PUT /question-groups/{id}` - Update group

### Assignments
- `GET /assignments/` - List all assignments
- `GET /assignments/team/{team_id}` - Get team assignments
- `POST /assignments/` - Create assignment
- `PUT /assignments/{id}/q10` - Add Q10 mark

### Grades
- `POST /grades/` - Create or update grade
- `GET /grades/assignment/{id}` - Get grades for assignment

### Reports
- `GET /reports/summary` - Get summary statistics
- `GET /reports/teacher-stats` - Get teacher statistics
- `GET /reports/student-results` - Get all student results
- `GET /reports/export/csv` - Download CSV

## Default Data

The seed script creates:
- 4 Teams (Team 1-4)
- 8 Teachers (2 per team)
- 7 Question Groups (A-G) with sample mark structures
- 1 Default exam session (January 2026)

## Environment Variables

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/iqraa_exam
SECRET_KEY=your-secret-key-here
```

## License

MIT
