<script>
    import { page } from '$app/stores';
    import { onMount } from 'svelte';
    import { teamsAPI, assignmentsAPI, gradesAPI } from '$lib/api.js';
    import { showNotification, showError } from '$lib/stores.js';

    // Get teacher ID from URL
    $: teacherId = $page.params.id;

    let teacher = null;
    let assignments = [];
    let loading = true;
    let selectedAssignment = null;
    let gradeForm = {};
    let existingGrade = null;
    let submitting = false;
    
    // Incomplete confirmation modal
    let showIncompleteModal = false;
    let incompleteAssignment = null;
    let markingIncomplete = false;

    onMount(async () => {
        await loadTeacher();
    });

    async function loadTeacher() {
        loading = true;
        try {
            teacher = await teamsAPI.getTeacher(teacherId);
            await loadAssignments();
        } catch (error) {
            showError('نەتوانرا زانیاری مامۆستا بهێنرێت');
        } finally {
            loading = false;
        }
    }

    async function loadAssignments() {
        if (!teacher) return;
        try {
            assignments = await assignmentsAPI.getByTeam(teacher.team_id);
        } catch (error) {
            showError('نەتوانرا قوتابیان بهێنرێت');
        }
    }

    async function selectStudent(assignment) {
        selectedAssignment = assignment;
        
        // Initialize form with max marks from question group
        const marks = assignment.question_group.marks_structure;
        gradeForm = {};
        for (let i = 1; i <= 9; i++) {
            gradeForm[`q${i}`] = { value: '', max: marks[`q${i}`] };
        }

        // Check for existing grade
        try {
            const grades = await gradesAPI.getByAssignment(assignment.id);
            existingGrade = grades.find(g => g.teacher_id === parseInt(teacherId));
            
            if (existingGrade) {
                // Pre-fill form
                for (let i = 1; i <= 9; i++) {
                    gradeForm[`q${i}`].value = existingGrade[`q${i}_mark`] ?? '';
                }
            } else {
                // Start grading timer (only for new grades)
                await gradesAPI.startGrading(assignment.id, teacherId);
            }
        } catch (e) {
            existingGrade = null;
            // Try to start grading anyway
            try {
                await gradesAPI.startGrading(assignment.id, teacherId);
            } catch (err) {
                // Ignore errors
            }
        }
    }

    function closeGrading() {
        selectedAssignment = null;
        gradeForm = {};
        existingGrade = null;
    }

    async function submitGrades() {
        // Validate all fields
        for (let i = 1; i <= 9; i++) {
            const val = parseFloat(gradeForm[`q${i}`].value);
            const max = gradeForm[`q${i}`].max;
            
            if (isNaN(val) || val < 0 || val > max) {
                showError(`پ${i} دەبێت لە نێوان ٠ و ${max} دا بێت`);
                return;
            }
        }

        submitting = true;
        try {
            const gradeData = {
                assignment_id: selectedAssignment.id,
                teacher_id: parseInt(teacherId)
            };

            for (let i = 1; i <= 9; i++) {
                gradeData[`q${i}_mark`] = parseFloat(gradeForm[`q${i}`].value);
            }

            await gradesAPI.createOrUpdate(gradeData);
            showNotification('نمرەکان بە سەرکەوتوویی پاشەکەوتکران!');
            closeGrading();
            await loadAssignments();
        } catch (error) {
            showError(error.message || 'نەتوانرا نمرەکان پاشەکەوت بکرێت');
        } finally {
            submitting = false;
        }
    }
    
    // Open incomplete confirmation modal
    function openIncompleteModal(assignment) {
        incompleteAssignment = assignment;
        showIncompleteModal = true;
    }
    
    function closeIncompleteModal() {
        showIncompleteModal = false;
        incompleteAssignment = null;
    }
    
    async function confirmMarkIncomplete() {
        if (!incompleteAssignment) return;
        
        markingIncomplete = true;
        try {
            await assignmentsAPI.markIncomplete(incompleteAssignment.id);
            showNotification('قوتابی وەک تەواونەکراو تۆمارکرا');
            closeIncompleteModal();
            closeGrading();
            await loadAssignments();
        } catch (error) {
            showError('نەتوانرا تۆمار بکرێت');
        } finally {
            markingIncomplete = false;
        }
    }

    // Calculate running total
    $: runningTotal = Object.values(gradeForm).reduce((sum, q) => {
        const val = parseFloat(q.value);
        return sum + (isNaN(val) ? 0 : val);
    }, 0);

    // Check grading status for this teacher
    function isGradedByMe(assignment) {
        if (teacher?.position === 1) return assignment.is_graded_teacher1;
        if (teacher?.position === 2) return assignment.is_graded_teacher2;
        return false;
    }
</script>

<div class="teacher-page">
    {#if loading}
        <div class="loading-full">
            <div class="spinner"></div>
            <p>چاوەڕێ بکە...</p>
        </div>
    {:else if teacher}
        <!-- Header -->
        <header class="teacher-header">
            <div class="header-right">
                <a href="/" class="back-btn">
                    <span class="back-arrow">→</span>
                    <span>گەڕانەوە</span>
                </a>
                <div class="teacher-info">
                    <h1>{teacher.name}</h1>
                    <span class="team-badge">{teacher.team.name} • مامۆستای {teacher.position}</span>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="teacher-main">
            {#if selectedAssignment}
                <!-- Grading Form -->
                <div class="grading-panel">
                    <div class="grading-header">
                        <button class="btn btn-outline" on:click={closeGrading}>
                            ← گەڕانەوە بۆ لیستەکە
                        </button>
                        <h2>نمرەدانی قوتابی</h2>
                    </div>

                    <div class="student-card">
                        <div class="student-details">
                            <h3>{selectedAssignment.student.name}</h3>
                            <div class="detail-row">
                                <span class="label">ساڵی لەدایکبوون:</span>
                                <span>{selectedAssignment.student.birth_year || '-'}</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">مامۆستای وانە:</span>
                                <span>{selectedAssignment.student.regular_teacher}</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">گرووپی پرسیار:</span>
                                <span class="badge badge-primary">
                                    گرووپ {selectedAssignment.question_group.code}
                                </span>
                            </div>
                        </div>
                    </div>

                    <form on:submit|preventDefault={submitGrades} class="grade-form">
                        <div class="questions-grid">
                            {#each Array(9) as _, i}
                                <div class="question-input">
                                    <label for="q{i+1}">
                                        <span class="q-number">پ{i + 1}</span>
                                        <span class="q-max">زۆرینە: {gradeForm[`q${i + 1}`]?.max}</span>
                                    </label>
                                    <input 
                                        id="q{i+1}"
                                        type="number" 
                                        class="form-input"
                                        bind:value={gradeForm[`q${i + 1}`].value}
                                        min="0"
                                        max={gradeForm[`q${i + 1}`]?.max}
                                        step="0.5"
                                        placeholder="٠"
                                        required
                                    />
                                </div>
                            {/each}
                        </div>

                        <div class="total-display">
                            <span>کۆی ڕۆیشتوو:</span>
                            <span class="total-value">{runningTotal.toFixed(1)} / {selectedAssignment.question_group.total_marks}</span>
                        </div>

                        <div class="form-actions">
                            <button type="submit" class="btn btn-success btn-lg" disabled={submitting}>
                                {submitting ? 'پاشەکەوتکردن...' : (existingGrade ? 'نوێکردنەوەی نمرەکان' : 'ناردنی نمرەکان')}
                            </button>
                            <button 
                                type="button" 
                                class="btn btn-danger-outline btn-lg"
                                on:click={() => openIncompleteModal(selectedAssignment)}
                            >
                                تاقیکردنەوەی تەواونەکرد
                            </button>
                        </div>
                    </form>
                </div>
            {:else}
                <!-- Student List -->
                <div class="students-panel">
                    <h2>قوتابیانی نمرەدان</h2>
                    <p class="subtitle">قوتابییەک هەڵبژێرە بۆ نمرەدان</p>

                    <div class="students-list">
                        {#each assignments as assignment}
                            {#if !assignment.exam_incomplete}
                                <button 
                                    class="student-row"
                                    class:graded={isGradedByMe(assignment)}
                                    on:click={() => selectStudent(assignment)}
                                >
                                    <div class="student-info">
                                        <strong>{assignment.student.name}</strong>
                                        <span class="student-meta">
                                            لەدایکبوون: {assignment.student.birth_year || '-'} • 
                                            گرووپ {assignment.question_group.code}
                                        </span>
                                    </div>
                                    <div class="student-status">
                                        {#if isGradedByMe(assignment)}
                                            <span class="badge badge-success">✓ نمرەدراو</span>
                                        {:else}
                                            <span class="badge badge-warning">چاوەڕوان</span>
                                        {/if}
                                    </div>
                                </button>
                            {:else}
                                <div class="student-row incomplete">
                                    <div class="student-info">
                                        <strong>{assignment.student.name}</strong>
                                        <span class="student-meta">
                                            لەدایکبوون: {assignment.student.birth_year || '-'} • 
                                            گرووپ {assignment.question_group.code}
                                        </span>
                                    </div>
                                    <div class="student-status">
                                        <span class="badge badge-danger">تەواونەکرد</span>
                                    </div>
                                </div>
                            {/if}
                        {:else}
                            <div class="empty-state">
                                <p>هێشتا هیچ قوتابییەک بۆ لیژنەکەت دابەش نەکراوە</p>
                            </div>
                        {/each}
                    </div>
                </div>
            {/if}
        </main>
    {:else}
        <div class="error-state">
            <h2>مامۆستا نەدۆزرایەوە</h2>
            <a href="/" class="btn btn-primary">گەڕانەوە بۆ سەرەتا</a>
        </div>
    {/if}
</div>

<!-- Incomplete Confirmation Modal -->
{#if showIncompleteModal}
    <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
    <div class="modal-overlay" on:click={closeIncompleteModal}>
        <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
        <div class="modal-content" on:click|stopPropagation>
            <h3>دڵنیای لە تەواونەکردن؟</h3>
            <p>ئایا دڵنیایت کە دەتەوێت ئەم قوتابییە وەک <strong>"تاقیکردنەوەی تەواونەکرد"</strong> تۆمار بکەیت؟</p>
            <p class="student-name-confirm">{incompleteAssignment?.student?.name}</p>
            <div class="modal-actions">
                <button class="btn btn-outline" on:click={closeIncompleteModal}>
                    نەخێر، گەڕانەوە
                </button>
                <button 
                    class="btn btn-danger" 
                    on:click={confirmMarkIncomplete}
                    disabled={markingIncomplete}
                >
                    {markingIncomplete ? 'تۆمارکردن...' : 'بەڵێ، تەواونەکرد'}
                </button>
            </div>
        </div>
    </div>
{/if}

<style>
    .teacher-page {
        min-height: 100vh;
        background: var(--background);
    }

    .loading-full {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        gap: 1rem;
        color: var(--text-light);
    }

    .teacher-header {
        background: var(--surface);
        padding: 1rem 2rem;
        border-bottom: 1px solid var(--border);
        box-shadow: var(--shadow);
    }

    .header-right {
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }

    .back-btn {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.625rem 1rem;
        background: #f0f0f0;
        border-radius: 8px;
        color: #333;
        text-decoration: none;
        font-size: 0.9rem;
        font-weight: 500;
        transition: all 0.15s ease;
        border: 1px solid #ddd;
    }

    .back-btn:hover {
        background: #e0e0e0;
        border-color: #ccc;
    }

    .back-arrow {
        font-size: 1.1rem;
    }

    .teacher-info h1 {
        font-size: 1.5rem;
        margin-bottom: 0.25rem;
    }

    .team-badge {
        color: var(--primary);
        font-size: 0.875rem;
    }

    .teacher-main {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem;
    }

    .students-panel h2 {
        margin-bottom: 0.25rem;
    }

    .subtitle {
        color: var(--text-light);
        margin-bottom: 1.5rem;
    }

    .students-list {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }

    .student-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 1.25rem;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.15s;
        text-align: right;
        width: 100%;
    }

    .student-row:hover {
        border-color: var(--primary);
        box-shadow: var(--shadow-md);
    }

    .student-row.graded {
        border-right: 4px solid var(--success);
    }

    .student-info strong {
        display: block;
        margin-bottom: 0.25rem;
    }

    .student-meta {
        font-size: 0.875rem;
        color: var(--text-light);
    }

    /* Grading Panel */
    .grading-panel {
        background: var(--surface);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: var(--shadow-md);
    }

    .grading-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }

    .grading-header h2 {
        flex: 1;
    }

    .student-card {
        background: var(--background);
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
    }

    .student-card h3 {
        margin-bottom: 0.75rem;
        color: var(--primary);
    }

    .detail-row {
        display: flex;
        gap: 0.5rem;
        font-size: 0.875rem;
        margin-bottom: 0.25rem;
    }

    .detail-row .label {
        color: var(--text-light);
    }

    .questions-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-bottom: 1.5rem;
    }

    @media (max-width: 640px) {
        .questions-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    .question-input {
        background: var(--background);
        padding: 1rem;
        border-radius: 8px;
    }

    .question-input label {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
    }

    .q-number {
        font-weight: 600;
        color: var(--primary);
    }

    .q-max {
        font-size: 0.75rem;
        color: var(--text-light);
    }

    .question-input input {
        text-align: center;
        font-size: 1.25rem;
        font-weight: 600;
        padding: 0.75rem;
    }

    .total-display {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 1.25rem;
        background: var(--primary);
        color: white;
        border-radius: 8px;
        margin-bottom: 1.5rem;
    }

    .total-value {
        font-size: 1.5rem;
        font-weight: 700;
    }

    .form-actions {
        text-align: center;
    }

    .btn-lg {
        padding: 1rem 3rem;
        font-size: 1rem;
    }

    .empty-state {
        text-align: center;
        padding: 3rem;
        color: var(--text-light);
        background: var(--surface);
        border-radius: 8px;
        border: 1px dashed var(--border);
    }

    .error-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        gap: 1rem;
    }

    /* Mobile Responsive Styles */
    @media (max-width: 768px) {
        .teacher-header {
            padding: 0.75rem 1rem;
        }

        .teacher-info h1 {
            font-size: 1.1rem;
        }

        .team-badge {
            font-size: 0.7rem;
        }

        .teacher-main {
            padding: 1rem;
        }

        .grading-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.75rem;
        }

        .student-card {
            padding: 1rem;
        }

        .student-card h3 {
            font-size: 1.1rem;
        }

        .student-meta {
            grid-template-columns: 1fr;
            gap: 0.5rem;
        }

        .questions-grid {
            grid-template-columns: 1fr 1fr;
            gap: 0.75rem;
        }

        .question-input {
            padding: 0.75rem;
        }

        .question-input input {
            font-size: 1rem;
            padding: 0.625rem;
        }

        .total-display {
            flex-direction: column;
            gap: 0.5rem;
            text-align: center;
        }

        .btn-lg {
            width: 100%;
            padding: 0.875rem 2rem;
        }

        .student-row {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.75rem;
        }
    }

    @media (max-width: 480px) {
        .questions-grid {
            grid-template-columns: 1fr;
        }

        .back-btn {
            padding: 0.5rem 0.75rem;
            font-size: 0.8rem;
        }

        .grading-header h2 {
            font-size: 1.1rem;
        }
    }

    /* Form Actions with multiple buttons */
    .form-actions {
        display: flex;
        gap: 1rem;
        justify-content: center;
        flex-wrap: wrap;
    }

    .btn-danger-outline {
        background: transparent;
        color: #dc3545;
        border: 2px solid #dc3545;
    }

    .btn-danger-outline:hover {
        background: #dc3545;
        color: white;
    }

    /* Incomplete student row */
    .student-row.incomplete {
        opacity: 0.6;
        cursor: not-allowed;
        border-right: 4px solid #dc3545;
    }

    .badge-danger {
        background: #dc3545;
        color: white;
    }

    /* Modal styles */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        padding: 1rem;
    }

    .modal-content {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        max-width: 400px;
        width: 100%;
        text-align: center;
    }

    .modal-content h3 {
        margin-bottom: 1rem;
        color: #dc3545;
    }

    .modal-content p {
        color: #666;
        margin-bottom: 0.5rem;
    }

    .student-name-confirm {
        font-size: 1.25rem;
        font-weight: 600;
        color: #333;
        margin: 1rem 0 1.5rem;
        padding: 0.75rem;
        background: #f8f9fa;
        border-radius: 8px;
    }

    .modal-actions {
        display: flex;
        gap: 1rem;
        justify-content: center;
    }

    .modal-actions .btn {
        flex: 1;
    }

    .btn-danger {
        background: #dc3545;
        color: white;
        border: none;
    }

    .btn-danger:hover {
        background: #c82333;
    }
</style>
