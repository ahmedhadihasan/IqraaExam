// API configuration - Use environment variable or production URL
export const API_BASE_URL = import.meta.env.VITE_API_URL || 
    (typeof window !== 'undefined' && window.location.hostname !== 'localhost' 
        ? 'https://iqraa-api-eczd.onrender.com' 
        : 'http://localhost:8000');

/**
 * Generic fetch wrapper with error handling
 */
async function fetchAPI(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const response = await fetch(url, { ...defaultOptions, ...options });
    
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
        throw new Error(error.detail || 'Request failed');
    }
    
    // Handle empty responses (like DELETE)
    const text = await response.text();
    return text ? JSON.parse(text) : null;
}

// ========== Teams API ==========
export const teamsAPI = {
    getAll: () => fetchAPI('/teams/'),
    get: (id) => fetchAPI(`/teams/${id}`),
    create: (data) => fetchAPI('/teams/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => fetchAPI(`/teams/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => fetchAPI(`/teams/${id}`, { method: 'DELETE' }),
    
    // Teachers
    getAllTeachers: () => fetchAPI('/teams/teachers/all'),
    getTeamTeachers: (teamId) => fetchAPI(`/teams/${teamId}/teachers`),
    createTeacher: (data) => fetchAPI('/teams/teachers', { method: 'POST', body: JSON.stringify(data) }),
    getTeacher: (id) => fetchAPI(`/teams/teachers/${id}`),
    updateTeacher: (id, data) => fetchAPI(`/teams/teachers/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    deleteTeacher: (id) => fetchAPI(`/teams/teachers/${id}`, { method: 'DELETE' }),
};

// ========== Question Groups API ==========
export const questionGroupsAPI = {
    getAll: () => fetchAPI('/question-groups/'),
    get: (id) => fetchAPI(`/question-groups/${id}`),
    create: (data) => fetchAPI('/question-groups/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => fetchAPI(`/question-groups/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => fetchAPI(`/question-groups/${id}`, { method: 'DELETE' }),
};

// ========== Students API ==========
export const studentsAPI = {
    getAll: (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return fetchAPI(`/students/${queryString ? '?' + queryString : ''}`);
    },
    get: (id) => fetchAPI(`/students/${id}`),
    create: (data) => fetchAPI('/students/', { method: 'POST', body: JSON.stringify(data) }),
    createBulk: (data) => fetchAPI('/students/bulk', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => fetchAPI(`/students/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => fetchAPI(`/students/${id}`, { method: 'DELETE' }),
    deleteAll: () => fetchAPI('/students/', { method: 'DELETE' }),
    importCSV: async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch(`${API_BASE_URL}/students/import-csv`, {
            method: 'POST',
            body: formData
        });
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
            throw new Error(error.detail || 'Import failed');
        }
        return response.json();
    },
};

// ========== Exam Sessions API ==========
export const examSessionsAPI = {
    getAll: (activeOnly = false) => fetchAPI(`/exam-sessions/?active_only=${activeOnly}`),
    getActive: () => fetchAPI('/exam-sessions/active'),
    get: (id) => fetchAPI(`/exam-sessions/${id}`),
    create: (data) => fetchAPI('/exam-sessions/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => fetchAPI(`/exam-sessions/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    activate: (id) => fetchAPI(`/exam-sessions/${id}/activate`, { method: 'PUT' }),
    deactivate: (id) => fetchAPI(`/exam-sessions/${id}/deactivate`, { method: 'PUT' }),
    delete: (id) => fetchAPI(`/exam-sessions/${id}`, { method: 'DELETE' }),
};

// ========== Assignments API ==========
export const assignmentsAPI = {
    getAll: (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return fetchAPI(`/assignments/${queryString ? '?' + queryString : ''}`);
    },
    getByTeam: (teamId, pendingOnly = false) => 
        fetchAPI(`/assignments/team/${teamId}?pending_only=${pendingOnly}`),
    get: (id) => fetchAPI(`/assignments/${id}`),
    create: (data) => fetchAPI('/assignments/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, teamId = null, questionGroupId = null) => {
        const params = new URLSearchParams();
        if (teamId) params.append('team_id', teamId);
        if (questionGroupId) params.append('question_group_id', questionGroupId);
        return fetchAPI(`/assignments/${id}?${params.toString()}`, { method: 'PUT' });
    },
    updateQ10: (id, q10Mark) => fetchAPI(`/assignments/${id}/q10`, { 
        method: 'PUT', 
        body: JSON.stringify({ q10_mark: q10Mark }) 
    }),
    syncQ10: () => fetchAPI('/assignments/sync-q10', { method: 'POST' }),
    markIncomplete: (id) => fetchAPI(`/assignments/${id}/incomplete`, { method: 'PUT' }),
    markComplete: (id) => fetchAPI(`/assignments/${id}/complete`, { method: 'PUT' }),
    delete: (id) => fetchAPI(`/assignments/${id}`, { method: 'DELETE' }),
};

// ========== Grades API ==========
export const gradesAPI = {
    getByAssignment: (assignmentId) => fetchAPI(`/grades/assignment/${assignmentId}`),
    getByTeacher: (teacherId) => fetchAPI(`/grades/teacher/${teacherId}`),
    get: (id) => fetchAPI(`/grades/${id}`),
    createOrUpdate: (data) => fetchAPI('/grades/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => fetchAPI(`/grades/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => fetchAPI(`/grades/${id}`, { method: 'DELETE' }),
    startGrading: (assignmentId, teacherId) => fetchAPI(`/grades/start-grading?assignment_id=${assignmentId}&teacher_id=${teacherId}`, { method: 'POST' }),
};

// ========== Reports API ==========
export const reportsAPI = {
    getTeacherStats: (examSessionId = null) => {
        const param = examSessionId ? `?exam_session_id=${examSessionId}` : '';
        return fetchAPI(`/reports/teacher-stats${param}`);
    },
    getStudentResults: (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return fetchAPI(`/reports/student-results${queryString ? '?' + queryString : ''}`);
    },
    getSummary: (examSessionId = null) => {
        const param = examSessionId ? `?exam_session_id=${examSessionId}` : '';
        return fetchAPI(`/reports/summary${param}`);
    },
    exportCSVDetailed: (examSessionId = null) => {
        const param = examSessionId ? `?exam_session_id=${examSessionId}` : '';
        return `${API_BASE_URL}/reports/export/csv${param}`;
    },
    exportCSVSummary: (examSessionId = null) => {
        const param = examSessionId ? `?exam_session_id=${examSessionId}` : '';
        return `${API_BASE_URL}/reports/export/csv-summary${param}`;
    },
};
