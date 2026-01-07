<script>
    import { onMount } from 'svelte';
    import { assignmentsAPI, gradesAPI } from '$lib/api.js';
    import { showNotification, showError } from '$lib/stores.js';

    let assignments = [];
    let loading = true;
    let savingId = null;

    // Q10 marks input
    let q10Marks = {};

    onMount(loadAssignments);

    async function loadAssignments() {
        loading = true;
        try {
            const all = await assignmentsAPI.getAll();
            // Filter to show only those graded by both teachers but Q10 not yet set
            let filtered = all.filter(a => 
                a.is_graded_teacher1 && a.is_graded_teacher2
            );
            
            // Sort: ungraded (q10 is null) first, then graded ones at the bottom
            filtered.sort((a, b) => {
                const aHasQ10 = a.q10_mark !== null && a.q10_mark !== undefined;
                const bHasQ10 = b.q10_mark !== null && b.q10_mark !== undefined;
                if (aHasQ10 === bHasQ10) return 0;
                return aHasQ10 ? 1 : -1;  // ungraded (no Q10) comes first
            });
            
            assignments = filtered;
            
            // Pre-fill existing Q10 marks
            assignments.forEach(a => {
                q10Marks[a.id] = a.q10_mark !== null ? a.q10_mark : '';
            });
        } catch (error) {
            showError('نەتوانرا دابەشکردنەکان بهێنرێت');
        } finally {
            loading = false;
        }
    }

    async function saveQ10(assignment) {
        const mark = parseFloat(q10Marks[assignment.id]);
        
        if (isNaN(mark) || mark < 0 || mark > 10) {
            showError('نمرەی پرسیاری ١٠ دەبێت لە نێوان ٠ و ١٠ دا بێت');
            return;
        }

        savingId = assignment.id;
        try {
            await assignmentsAPI.updateQ10(assignment.id, mark);
            const isUpdate = assignment.q10_mark !== null && assignment.q10_mark !== undefined;
            showNotification(isUpdate ? 'نمرەی پرسیاری ١٠ نوێکرایەوە!' : 'نمرەی پرسیاری ١٠ پاشەکەوتکرا!');
            await loadAssignments();
        } catch (error) {
            showError('نەتوانرا نمرەی پرسیاری ١٠ پاشەکەوت بکرێت');
        } finally {
            savingId = null;
        }
    }
    
    function hasQ10(assignment) {
        return assignment.q10_mark !== null && assignment.q10_mark !== undefined;
    }
</script>

<div class="q10-page">
    <h1>نمرەدانی پرسیاری ١٠</h1>
    <p class="subtitle">نمرەی کۆتایی پ١٠ (لە ١٠) زیادبکە بۆ قوتابیانی کە هەردوو مامۆستا نمرەیان داوە</p>

    {#if loading}
        <div class="loading">
            <div class="spinner"></div>
        </div>
    {:else if assignments.length === 0}
        <div class="empty-state">
            <div class="empty-icon">📝</div>
            <h3>هیچ قوتابییەک ئامادە نییە بۆ پرسیاری ١٠</h3>
            <p>قوتابیان لێرە دەردەکەون دوای ئەوەی هەردوو مامۆستا نمرەیان بدەن</p>
        </div>
    {:else}
        <div class="card">
            <div class="card-body">
                <table class="table">
                    <thead>
                        <tr>
                            <th>قوتابی</th>
                            <th>لیژنە</th>
                            <th>گرووپ</th>
                            <th>بارودۆخ</th>
                            <th>نمرەی پرسیاری ١٠</th>
                            <th>کردار</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each assignments as assignment}
                            <tr class:graded={hasQ10(assignment)}>
                                <td>
                                    <div class="student-info">
                                        <strong>{assignment.student.name}</strong>
                                        <span class="text-light">لەدایکبوون: {assignment.student.birth_year || '-'}</span>
                                    </div>
                                </td>
                                <td>{assignment.team.name}</td>
                                <td>
                                    <span class="badge badge-primary">
                                        گرووپ {assignment.question_group.code}
                                    </span>
                                </td>
                                <td>
                                    {#if assignment.is_completed}
                                        <span class="badge badge-success">تەواوبوو</span>
                                    {:else if hasQ10(assignment)}
                                        <span class="badge badge-info">پرسیاری ١٠ زیادکرا</span>
                                    {:else}
                                        <span class="badge badge-warning">ئامادەی پرسیاری ١٠</span>
                                    {/if}
                                </td>
                                <td>
                                    <div class="q10-input-group">
                                        <input 
                                            type="number" 
                                            class="form-input q10-input"
                                            bind:value={q10Marks[assignment.id]}
                                            min="0"
                                            max="10"
                                            step="0.5"
                                            placeholder="٠-١٠"
                                        />
                                        <span class="q10-max">/ ١٠</span>
                                    </div>
                                </td>
                                <td>
                                    <button 
                                        class="btn {hasQ10(assignment) ? 'btn-secondary' : 'btn-success'} btn-sm"
                                        on:click={() => saveQ10(assignment)}
                                        disabled={savingId === assignment.id}
                                    >
                                        {#if savingId === assignment.id}
                                            پاشەکەوتکردن...
                                        {:else if hasQ10(assignment)}
                                            نوێکردنەوە
                                        {:else}
                                            پاشەکەوتکردن
                                        {/if}
                                    </button>
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        </div>
    {/if}
</div>

<style>
    .subtitle {
        color: var(--text-light);
        margin-bottom: 2rem;
    }

    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        background: var(--surface);
        border-radius: 12px;
        border: 1px solid var(--border);
    }

    .empty-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }

    .empty-state h3 {
        margin-bottom: 0.5rem;
    }

    .empty-state p {
        color: var(--text-light);
    }

    .student-info {
        display: flex;
        flex-direction: column;
    }

    .student-info span {
        font-size: 0.75rem;
    }

    .q10-input-group {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .q10-input {
        width: 80px;
        text-align: center;
    }

    .q10-max {
        color: var(--text-light);
        font-size: 0.875rem;
    }

    .btn-sm {
        padding: 0.375rem 0.75rem;
        font-size: 0.75rem;
    }
    
    tr.graded {
        background-color: #f0fdf4;
    }
    
    .badge-info {
        background-color: #3b82f6;
        color: white;
    }
</style>
