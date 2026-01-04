<script>
    import { onMount } from 'svelte';
    import { reportsAPI, examSessionsAPI } from '$lib/api.js';
    import { showError } from '$lib/stores.js';

    let results = [];
    let activeSession = null;
    let loading = true;

    onMount(async () => {
        try {
            [results, activeSession] = await Promise.all([
                reportsAPI.getStudentResults(),
                examSessionsAPI.getActive()
            ]);
        } catch (error) {
            console.error('Error loading results:', error);
            showError('نەتوانرا ئەنجامەکان بهێنرێت');
        } finally {
            loading = false;
        }
    });

    // Calculate teacher totals from marks object
    function calcTotal(marks) {
        if (!marks) return null;
        const values = Object.values(marks).filter(v => v !== null && v !== undefined);
        if (values.length === 0) return null;
        return values.reduce((a, b) => a + b, 0);
    }

    // Determine completion status
    function getStatus(r) {
        if (r.exam_incomplete) return 'incomplete';
        
        const t1Total = calcTotal(r.teacher1_marks);
        const t2Total = calcTotal(r.teacher2_marks);
        
        if (t1Total !== null && t2Total !== null && r.q10_mark !== null) {
            // Check if passed (>=80)
            if (r.final_total !== null && r.final_total >= 80) {
                return 'passed';
            } else {
                return 'failed';
            }
        } else if (t1Total !== null && t2Total !== null) {
            return 'waiting-q10';
        } else if (t1Total !== null || t2Total !== null) {
            return 'partial';
        }
        return 'pending';
    }
</script>

<div class="results-page">
    <div class="page-header">
        <h1>ئەنجامەکان</h1>
        <div class="header-actions">
            {#if activeSession}
                <span class="session-badge">📅 {activeSession.name}</span>
            {/if}
            <a href={reportsAPI.exportCSVDetailed()} class="btn btn-primary" download>
                📥 CSV تەواو
            </a>
            <a href={reportsAPI.exportCSVSummary()} class="btn btn-secondary" download>
                📄 CSV کورت
            </a>
        </div>
    </div>

    {#if loading}
        <div class="loading">
            <div class="spinner"></div>
        </div>
    {:else}
        <div class="results-summary mb-4">
            <div class="summary-card">
                <span class="summary-value">{results.length}</span>
                <span class="summary-label">کۆی قوتابیان</span>
            </div>
            <div class="summary-card passed">
                <span class="summary-value">{results.filter(r => getStatus(r) === 'passed').length}</span>
                <span class="summary-label">دەرچوو</span>
            </div>
            <div class="summary-card failed">
                <span class="summary-value">{results.filter(r => getStatus(r) === 'failed').length}</span>
                <span class="summary-label">دەرنەچوو</span>
            </div>
            <div class="summary-card incomplete">
                <span class="summary-value">{results.filter(r => getStatus(r) === 'incomplete').length}</span>
                <span class="summary-label">تەواونەکراو</span>
            </div>
            <div class="summary-card pending">
                <span class="summary-value">{results.filter(r => getStatus(r) === 'pending' || getStatus(r) === 'partial' || getStatus(r) === 'waiting-q10').length}</span>
                <span class="summary-label">چاوەڕوان</span>
            </div>
        </div>

        <div class="card">
            <div class="card-body table-responsive">
                <table class="table">
                    <thead>
                        <tr>
                            <th>قوتابی</th>
                            <th>لەدایکبوون</th>
                            <th>تیم</th>
                            <th>گرووپ</th>
                            <th>مامۆستا ١</th>
                            <th>مامۆستا ٢</th>
                            <th>ناوەند پ١-پ٩</th>
                            <th>پ١٠</th>
                            <th>کۆی گشتی</th>
                            <th>بارودۆخ</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each results as r}
                            {@const t1Total = calcTotal(r.teacher1_marks)}
                            {@const t2Total = calcTotal(r.teacher2_marks)}
                            {@const status = getStatus(r)}
                            <tr>
                                <td data-label="قوتابی"><strong>{r.student_name}</strong></td>
                                <td data-label="لەدایکبوون">{r.student_birth_year || '-'}</td>
                                <td data-label="تیم">{r.team_name}</td>
                                <td data-label="گرووپ">
                                    <span class="badge badge-primary">{r.question_group}</span>
                                </td>
                                <td data-label="مامۆستا ١" class="text-center">{t1Total ?? '-'}</td>
                                <td data-label="مامۆستا ٢" class="text-center">{t2Total ?? '-'}</td>
                                <td data-label="ناوەند" class="text-center font-bold">{r.total_average_q1_q9 ?? '-'}</td>
                                <td data-label="پ١٠" class="text-center">{r.q10_mark ?? '-'}</td>
                                <td data-label="کۆی گشتی" class="text-center">
                                    <span class="total-mark">{r.final_total ?? '-'}</span>
                                </td>
                                <td data-label="بارودۆخ">
                                    {#if status === 'incomplete'}
                                        <span class="badge badge-incomplete">تەواونەکرد</span>
                                    {:else if status === 'passed'}
                                        <span class="badge badge-passed">دەرچوو ✓</span>
                                    {:else if status === 'failed'}
                                        <span class="badge badge-failed">نەدەرچوو</span>
                                    {:else if status === 'waiting-q10'}
                                        <span class="badge badge-pending">چاوەڕوانی پ١٠</span>
                                    {:else if status === 'partial'}
                                        <span class="badge badge-pending">نیوەچڕ</span>
                                    {:else}
                                        <span class="badge badge-pending">چاوەڕوان</span>
                                    {/if}
                                </td>
                            </tr>
                        {:else}
                            <tr>
                                <td colspan="10" class="text-center text-light">هێشتا ئەنجامێک نییە</td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        </div>
    {/if}
</div>

<style>
    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        flex-wrap: wrap;
        gap: 1rem;
    }

    .header-actions {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .session-badge {
        background: rgba(37, 99, 235, 0.1);
        color: var(--primary);
        padding: 0.375rem 0.75rem;
        border-radius: 6px;
        font-size: 0.875rem;
    }

    .results-summary {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 1rem;
    }

    .summary-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
    }

    .summary-value {
        display: block;
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary);
    }

    .summary-label {
        font-size: 0.875rem;
        color: var(--text-light);
    }

    .table-responsive {
        overflow-x: auto;
    }

    .total-mark {
        font-size: 1.125rem;
        font-weight: 700;
        color: var(--primary);
    }

    .font-bold {
        font-weight: 600;
    }

    .text-center {
        text-align: center;
    }

    /* Pass/Fail Badge Colors */
    .badge-passed {
        background: #dcfce7;
        color: #16a34a;
        font-weight: 600;
    }

    .badge-failed {
        background: #fef9c3;
        color: #ca8a04;
        font-weight: 600;
    }

    .badge-incomplete {
        background: #fee2e2;
        color: #dc2626;
        font-weight: 600;
    }

    .badge-pending {
        background: #f3f4f6;
        color: #6b7280;
    }

    /* Summary card colors */
    .summary-card.passed {
        border-color: #16a34a;
    }
    .summary-card.passed .summary-value {
        color: #16a34a;
    }

    .summary-card.failed {
        border-color: #ca8a04;
    }
    .summary-card.failed .summary-value {
        color: #ca8a04;
    }

    .summary-card.incomplete {
        border-color: #dc2626;
    }
    .summary-card.incomplete .summary-value {
        color: #dc2626;
    }

    .summary-card.pending {
        border-color: #6b7280;
    }
    .summary-card.pending .summary-value {
        color: #6b7280;
    }

    @media (max-width: 768px) {
        .results-summary {
            grid-template-columns: repeat(2, 1fr);
        }

        .table thead {
            display: none;
        }

        .table tr {
            display: block;
            margin-bottom: 1rem;
            background: var(--surface);
            border-radius: 8px;
            padding: 1rem;
            border: 1px solid var(--border);
        }

        .table td {
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid var(--border);
        }

        .table td:last-child {
            border-bottom: none;
        }

        .table td::before {
            content: attr(data-label);
            font-weight: bold;
            color: var(--text-light);
        }
    }
</style>
