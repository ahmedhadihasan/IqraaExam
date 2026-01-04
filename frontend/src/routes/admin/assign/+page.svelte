<script>
    import { onMount } from 'svelte';
    import { studentsAPI, teamsAPI, questionGroupsAPI, assignmentsAPI, examSessionsAPI } from '$lib/api.js';
    import { showNotification, showError } from '$lib/stores.js';

    let students = [];
    let teams = [];
    let questionGroups = [];
    let assignments = [];
    let activeSession = null;
    let loading = true;
    let submitting = false;

    // Form
    let selectedStudent = '';
    let selectedTeam = '';
    let selectedGroup = '';

    // Edit modal
    let showEditModal = false;
    let editingAssignment = null;
    let editTeam = '';
    let editGroup = '';

    // Get IDs of already assigned students
    $: assignedStudentIds = new Set(assignments.map(a => a.student_id));
    
    // Filter out already assigned students
    $: availableStudents = students.filter(s => !assignedStudentIds.has(s.id));

    onMount(async () => {
        await loadData();
    });

    async function loadData() {
        loading = true;
        try {
            [students, teams, questionGroups, activeSession] = await Promise.all([
                studentsAPI.getAll(),
                teamsAPI.getAll(),
                questionGroupsAPI.getAll(),
                examSessionsAPI.getActive()
            ]);
            
            // Load assignments for current session
            if (activeSession) {
                assignments = await assignmentsAPI.getAll({ exam_session_id: activeSession.id });
            } else {
                assignments = await assignmentsAPI.getAll();
            }
            
            // Sort assignments by most recent first
            assignments = assignments.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        } catch (error) {
            showError('نەتوانرا داتا بهێنرێت');
        } finally {
            loading = false;
        }
    }

    async function assignStudent() {
        if (!selectedStudent || !selectedTeam || !selectedGroup) {
            showError('تکایە هەموو خانەکان هەڵبژێرە');
            return;
        }

        submitting = true;
        try {
            const newAssignment = await assignmentsAPI.create({
                student_id: parseInt(selectedStudent),
                team_id: parseInt(selectedTeam),
                question_group_id: parseInt(selectedGroup),
                exam_session_id: activeSession?.id || null
            });
            
            showNotification('قوتابی بە سەرکەوتوویی دابەشکرا!');
            
            // Add to beginning of assignments list
            assignments = [newAssignment, ...assignments];
            
            // Reset form
            selectedStudent = '';
            selectedTeam = '';
            selectedGroup = '';
        } catch (error) {
            showError(error.message || 'نەتوانرا قوتابی دابەش بکرێت');
        } finally {
            submitting = false;
        }
    }

    function openEditModal(assignment) {
        editingAssignment = assignment;
        editTeam = String(assignment.team_id);
        editGroup = String(assignment.question_group_id);
        showEditModal = true;
    }

    async function saveEdit() {
        if (!editTeam || !editGroup) return;
        
        submitting = true;
        try {
            const updated = await assignmentsAPI.update(
                editingAssignment.id,
                parseInt(editTeam),
                parseInt(editGroup)
            );
            
            // Update in list
            assignments = assignments.map(a => 
                a.id === editingAssignment.id ? updated : a
            );
            
            showNotification('دابەشکردن نوێکرایەوە!');
            showEditModal = false;
            editingAssignment = null;
        } catch (error) {
            showError(error.message || 'نەتوانرا نوێبکرێتەوە');
        } finally {
            submitting = false;
        }
    }

    async function deleteAssignment(assignment) {
        if (!confirm(`دڵنیای لە سڕینەوەی دابەشکردنی ${assignment.student?.name}?`)) return;
        
        try {
            await assignmentsAPI.delete(assignment.id);
            assignments = assignments.filter(a => a.id !== assignment.id);
            showNotification('دابەشکردن سڕایەوە');
        } catch (error) {
            showError('نەتوانرا بسڕدرێتەوە');
        }
    }

    async function markIncomplete(assignment) {
        if (!confirm(`دڵنیای لە تۆمارکردنی "${assignment.student?.name}" وەک تاقیکردنەوەی تەواونەکرد?`)) return;
        
        try {
            const updated = await assignmentsAPI.markIncomplete(assignment.id);
            assignments = assignments.map(a => a.id === assignment.id ? updated : a);
            showNotification('قوتابی وەک تەواونەکراو تۆمارکرا');
        } catch (error) {
            showError('نەتوانرا تۆمار بکرێت');
        }
    }

    async function undoIncomplete(assignment) {
        try {
            const updated = await assignmentsAPI.markComplete(assignment.id);
            assignments = assignments.map(a => a.id === assignment.id ? updated : a);
            showNotification('بارودۆخی قوتابی گەڕێندرایەوە');
        } catch (error) {
            showError('نەتوانرا گەڕێندرێتەوە');
        }
    }

    // Get selected entities for preview
    $: selectedStudentObj = students.find(s => s.id === parseInt(selectedStudent));
    $: selectedTeamObj = teams.find(t => t.id === parseInt(selectedTeam));
    $: selectedGroupObj = questionGroups.find(g => g.id === parseInt(selectedGroup));
</script>

<div class="assign-page">
    <div class="page-header">
        <h1>دابەشکردنی قوتابیان</h1>
        {#if activeSession}
            <span class="session-badge">📅 {activeSession.name}</span>
        {/if}
    </div>

    {#if loading}
        <div class="loading">
            <div class="spinner"></div>
        </div>
    {:else}
        <div class="assign-layout">
            <!-- Left side: Form and Preview -->
            <div class="form-section">
                <!-- Assignment Form -->
                <div class="card">
                    <div class="card-header">
                        دابەشکردنی نوێ
                        <span class="available-count">({availableStudents.length} قوتابی بەردەستە)</span>
                    </div>
                    <div class="card-body">
                        <form on:submit|preventDefault={assignStudent}>
                            <div class="form-group">
                                <label class="form-label">قوتابی هەڵبژێرە</label>
                                <select class="form-select" bind:value={selectedStudent}>
                                    <option value="">-- قوتابی هەڵبژێرە --</option>
                                    {#each availableStudents as student}
                                        <option value={student.id}>
                                            {student.name} (تەمەن: {student.age})
                                        </option>
                                    {/each}
                                </select>
                                {#if availableStudents.length === 0}
                                    <p class="form-hint success">✓ هەموو قوتابیان دابەشکراون!</p>
                                {/if}
                            </div>

                            <div class="form-group">
                                <label class="form-label">دابەشکردن بۆ تیم</label>
                                <div class="team-buttons">
                                    {#each teams as team}
                                        <button 
                                            type="button"
                                            class="team-btn"
                                            class:selected={selectedTeam === String(team.id)}
                                            on:click={() => selectedTeam = String(team.id)}
                                        >
                                            {team.name}
                                        </button>
                                    {/each}
                                </div>
                            </div>

                            <div class="form-group">
                                <label class="form-label">گرووپی پرسیار</label>
                                <div class="group-buttons">
                                    {#each questionGroups as group}
                                        <button 
                                            type="button"
                                            class="group-btn"
                                            class:selected={selectedGroup === String(group.id)}
                                            on:click={() => selectedGroup = String(group.id)}
                                        >
                                            <span class="group-code">{group.code}</span>
                                            <span class="group-name">{group.name}</span>
                                        </button>
                                    {/each}
                                </div>
                            </div>

                            <button 
                                type="submit" 
                                class="btn btn-primary btn-block" 
                                disabled={submitting || availableStudents.length === 0}
                            >
                                {submitting ? 'دابەشکردن...' : 'دابەشکردنی قوتابی'}
                            </button>
                        </form>
                    </div>
                </div>

                <!-- Preview Card -->
                {#if selectedStudentObj || selectedTeamObj || selectedGroupObj}
                    <div class="card preview-card">
                        <div class="card-header">پێشبینینی دابەشکردن</div>
                        <div class="card-body">
                            {#if selectedStudentObj}
                                <div class="preview-item">
                                    <span class="preview-label">قوتابی:</span>
                                    <span class="preview-value">{selectedStudentObj.name}</span>
                                </div>
                                <div class="preview-item">
                                    <span class="preview-label">تەمەن:</span>
                                    <span class="preview-value">{selectedStudentObj.age}</span>
                                </div>
                                <div class="preview-item">
                                    <span class="preview-label">مامۆستای ڕێکوپێک:</span>
                                    <span class="preview-value">{selectedStudentObj.regular_teacher}</span>
                                </div>
                            {/if}
                            
                            {#if selectedTeamObj}
                                <div class="preview-item highlight">
                                    <span class="preview-label">← دابەشکرا بۆ:</span>
                                    <span class="preview-value">{selectedTeamObj.name}</span>
                                </div>
                            {/if}
                            
                            {#if selectedGroupObj}
                                <div class="preview-item highlight">
                                    <span class="preview-label">← گرووپی پرسیار:</span>
                                    <span class="preview-value">گرووپ {selectedGroupObj.code}</span>
                                </div>
                            {/if}
                        </div>
                    </div>
                {/if}
            </div>

            <!-- Right side: Recent Assignments -->
            <div class="assignments-section">
                <div class="card">
                    <div class="card-header">
                        دابەشکردنە کوتاییەکان
                        <span class="count-badge">{assignments.length}</span>
                    </div>
                    <div class="card-body assignments-list">
                        {#if assignments.length === 0}
                            <p class="empty-text">هێشتا هیچ دابەشکردنێک نییە</p>
                        {:else}
                            {#each assignments as assignment}
                                <div class="assignment-card" class:incomplete={assignment.exam_incomplete}>
                                    <div class="assignment-info">
                                        <div class="student-name">{assignment.student?.name}</div>
                                        <div class="assignment-details">
                                            <span class="badge team-badge">{assignment.team?.name}</span>
                                            <span class="badge group-badge">گرووپ {assignment.question_group?.code}</span>
                                            {#if assignment.exam_incomplete}
                                                <span class="badge incomplete-badge">✗ تەواونەکرد</span>
                                            {:else if assignment.is_completed}
                                                <span class="badge completed-badge">✓ تەواوبوو</span>
                                            {:else if assignment.is_graded_teacher1 || assignment.is_graded_teacher2}
                                                <span class="badge progress-badge">⏳ لە کارەکەدایە</span>
                                            {/if}
                                        </div>
                                    </div>
                                    <div class="assignment-actions">
                                        {#if assignment.exam_incomplete}
                                            <button 
                                                class="btn-icon undo" 
                                                on:click={() => undoIncomplete(assignment)}
                                                title="گەڕانەوە"
                                            >
                                                ↩️
                                            </button>
                                        {:else}
                                            <button 
                                                class="btn-icon incomplete" 
                                                on:click={() => markIncomplete(assignment)}
                                                title="تەواونەکرد"
                                            >
                                                ✗
                                            </button>
                                        {/if}
                                        <button 
                                            class="btn-icon edit" 
                                            on:click={() => openEditModal(assignment)}
                                            title="دەستکاری"
                                        >
                                            ✏️
                                        </button>
                                        <button 
                                            class="btn-icon delete" 
                                            on:click={() => deleteAssignment(assignment)}
                                            title="سڕینەوە"
                                        >
                                            🗑️
                                        </button>
                                    </div>
                                </div>
                            {/each}
                        {/if}
                    </div>
                </div>
            </div>
        </div>
    {/if}
</div>

<!-- Edit Modal -->
{#if showEditModal && editingAssignment}
    <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-noninteractive-element-interactions -->
    <div class="modal-overlay" on:click={() => showEditModal = false} role="dialog" aria-modal="true">
        <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-noninteractive-element-interactions -->
        <div class="modal" on:click|stopPropagation role="document">
            <div class="modal-header">
                دەستکاری دابەشکردنی {editingAssignment.student?.name}
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label class="form-label">تیم</label>
                    <div class="team-buttons">
                        {#each teams as team}
                            <button 
                                type="button"
                                class="team-btn"
                                class:selected={editTeam === String(team.id)}
                                on:click={() => editTeam = String(team.id)}
                            >
                                {team.name}
                            </button>
                        {/each}
                    </div>
                </div>

                <div class="form-group">
                    <label class="form-label">گرووپی پرسیار</label>
                    <div class="group-buttons">
                        {#each questionGroups as group}
                            <button 
                                type="button"
                                class="group-btn"
                                class:selected={editGroup === String(group.id)}
                                on:click={() => editGroup = String(group.id)}
                            >
                                <span class="group-code">{group.code}</span>
                            </button>
                        {/each}
                    </div>
                </div>

                {#if editingAssignment.is_graded_teacher1 || editingAssignment.is_graded_teacher2}
                    <div class="warning-box">
                        ⚠️ ئاگاداری: ئەگەر تیمەکە بگۆڕی، نمرەکانی پێشوو دەسڕێتەوە!
                    </div>
                {/if}
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" on:click={() => showEditModal = false}>
                    پاشگەزبوونەوە
                </button>
                <button class="btn btn-primary" on:click={saveEdit} disabled={submitting}>
                    {submitting ? 'چاوەڕوان بە...' : 'پاشەکەوتکردن'}
                </button>
            </div>
        </div>
    </div>
{/if}

<style>
    .page-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 2rem;
    }

    .session-badge {
        background: var(--primary);
        color: white;
        padding: 0.375rem 0.75rem;
        border-radius: 6px;
        font-size: 0.875rem;
    }

    .assign-layout {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        align-items: start;
    }

    @media (max-width: 1200px) {
        .assign-layout {
            grid-template-columns: 1fr;
        }
    }

    .form-section {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }

    .available-count {
        font-size: 0.75rem;
        font-weight: normal;
        opacity: 0.7;
    }

    .form-hint {
        font-size: 0.75rem;
        margin-top: 0.5rem;
    }

    .form-hint.success {
        color: var(--success);
    }

    .team-buttons, .group-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
    }

    .team-btn, .group-btn {
        padding: 0.75rem 1.5rem;
        border: 2px solid var(--border);
        background: var(--surface);
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.15s;
        font-size: 0.875rem;
    }

    .team-btn:hover, .group-btn:hover {
        border-color: var(--primary);
    }

    .team-btn.selected, .group-btn.selected {
        background: var(--primary);
        color: white;
        border-color: var(--primary);
    }

    .group-btn {
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 60px;
    }

    .group-code {
        font-size: 1.25rem;
        font-weight: 700;
    }

    .group-name {
        font-size: 0.7rem;
        opacity: 0.8;
    }

    .btn-block {
        width: 100%;
        margin-top: 1rem;
    }

    .preview-card {
        background: #f0f9ff;
        border-color: var(--primary);
    }

    .preview-item {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid var(--border);
    }

    .preview-item.highlight {
        background: rgba(37, 99, 235, 0.1);
        margin: 0.5rem -1.25rem;
        padding: 0.75rem 1.25rem;
        border: none;
    }

    .preview-label {
        color: var(--text-light);
    }

    .preview-value {
        font-weight: 500;
    }

    /* Assignments List */
    .count-badge {
        background: var(--primary);
        color: white;
        padding: 0.125rem 0.5rem;
        border-radius: 12px;
        font-size: 0.75rem;
        margin-right: auto;
    }

    .assignments-list {
        max-height: 600px;
        overflow-y: auto;
        padding: 0.5rem;
    }

    .assignment-card {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 1rem;
        background: var(--background);
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border: 1px solid var(--border);
    }

    .assignment-card:hover {
        border-color: var(--primary);
    }

    .student-name {
        font-weight: 600;
        margin-bottom: 0.25rem;
    }

    .assignment-details {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }

    .badge {
        padding: 0.125rem 0.5rem;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 500;
    }

    .team-badge {
        background: #dbeafe;
        color: #1d4ed8;
    }

    .group-badge {
        background: #fef3c7;
        color: #b45309;
    }

    .completed-badge {
        background: #d1fae5;
        color: #047857;
    }

    .progress-badge {
        background: #fef3c7;
        color: #d97706;
    }

    .assignment-actions {
        display: flex;
        gap: 0.5rem;
    }

    .btn-icon {
        width: 32px;
        height: 32px;
        border: none;
        background: transparent;
        border-radius: 4px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.15s;
    }

    .btn-icon.edit:hover {
        background: #dbeafe;
    }

    .btn-icon.delete:hover {
        background: #fee2e2;
    }

    .btn-icon.incomplete {
        color: #dc3545;
        font-weight: bold;
    }

    .btn-icon.incomplete:hover {
        background: #fee2e2;
    }

    .btn-icon.undo:hover {
        background: #d1fae5;
    }

    .incomplete-badge {
        background: #fee2e2;
        color: #dc3545;
    }

    .assignment-card.incomplete {
        opacity: 0.6;
        border-right: 4px solid #dc3545;
    }

    .empty-text {
        text-align: center;
        color: var(--text-light);
        padding: 2rem;
    }

    /* Warning Box */
    .warning-box {
        background: #fef3c7;
        border: 1px solid #f59e0b;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        color: #92400e;
        font-size: 0.875rem;
        margin-top: 1rem;
    }
</style>
