<script>
    import { onMount } from 'svelte';
    import { reportsAPI, examSessionsAPI, assignmentsAPI } from '$lib/api.js';

    const API_BASE = 'http://localhost:8000';

    let summary = null;
    let teacherStats = [];
    let activeSession = null;
    let loading = true;
    let syncingQ10 = false;

    // Reset modals
    let showResetGradesModal = false;
    let showResetEverythingModal = false;
    let resetConfirmText = '';
    let resetting = false;
    let loadError = null;

    onMount(async () => {
        console.log('Dashboard: Starting to load data...');
        try {
            [summary, teacherStats, activeSession] = await Promise.all([
                reportsAPI.getSummary(),
                reportsAPI.getTeacherStats(),
                examSessionsAPI.getActive()
            ]);
            console.log('Dashboard: Data loaded successfully', { summary, teacherStats, activeSession });
        } catch (error) {
            console.error('Failed to load dashboard:', error);
            loadError = error.message || 'هەڵەیەک ڕوویدا';
        } finally {
            loading = false;
            console.log('Dashboard: Loading complete, loading =', loading);
        }
    });

    async function syncQ10FromStudents() {
        syncingQ10 = true;
        try {
            const result = await assignmentsAPI.syncQ10();
            alert(`${result.message}`);
            window.location.reload();
        } catch (error) {
            alert('هەڵە لە هاوکاتکردنی Q10: ' + (error.message || 'نەزانراو'));
        } finally {
            syncingQ10 = false;
        }
    }

    async function resetAllGrades() {
        if (resetConfirmText !== 'سڕینەوە') {
            alert('تکایە بنووسە: سڕینەوە');
            return;
        }
        resetting = true;
        try {
            const res = await fetch(`${API_BASE}/reset-all-grades`, { method: 'DELETE' });
            if (res.ok) {
                alert('هەموو نمرەکان سڕانەوە!');
                showResetGradesModal = false;
                resetConfirmText = '';
                window.location.reload();
            } else {
                alert('هەڵەیەک ڕوویدا');
            }
        } catch (err) {
            alert('هەڵەی پەیوەندی');
        } finally {
            resetting = false;
        }
    }

    async function resetEverything() {
        if (resetConfirmText !== 'سڕینەوەی هەموو شت') {
            alert('تکایە بنووسە: سڕینەوەی هەموو شت');
            return;
        }
        resetting = true;
        try {
            const res = await fetch(`${API_BASE}/reset-everything`, { method: 'DELETE' });
            if (res.ok) {
                alert('هەموو داتاکان سڕانەوە!');
                showResetEverythingModal = false;
                resetConfirmText = '';
                window.location.reload();
            } else {
                alert('هەڵەیەک ڕوویدا');
            }
        } catch (err) {
            alert('هەڵەی پەیوەندی');
        } finally {
            resetting = false;
        }
    }
</script>

<div class="dashboard">
    <div class="page-header">
        <h1>داشبۆرد</h1>
        {#if activeSession}
            <span class="session-badge">📅 {activeSession.name}</span>
        {/if}
    </div>

    {#if loading}
        <div class="loading">
            <div class="spinner"></div>
            <p style="margin-top: 1rem; color: var(--text-light);">چاوەڕوان بە...</p>
        </div>
    {:else if loadError}
        <div class="error-box">
            <p>⚠️ {loadError}</p>
            <button class="btn btn-primary" on:click={() => window.location.reload()}>
                هەوڵدانەوە
            </button>
        </div>
    {:else}
        <!-- Summary Cards -->
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; margin-bottom: 1.5rem;">
            <div style="background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; display: flex; align-items: center; gap: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <div style="font-size: 2rem;">👨‍🎓</div>
                <div>
                    <div style="font-size: 1.75rem; font-weight: 700;">{summary?.total_students || 0}</div>
                    <div style="color: #64748b; font-size: 0.875rem;">کۆی قوتابیان</div>
                </div>
            </div>
            
            <div style="background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; border-right: 4px solid #10b981; display: flex; align-items: center; gap: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <div style="font-size: 2rem;">✅</div>
                <div>
                    <div style="font-size: 1.75rem; font-weight: 700;">{summary?.completed || 0}</div>
                    <div style="color: #64748b; font-size: 0.875rem;">تەواوبوو</div>
                </div>
            </div>
            
            <div style="background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; border-right: 4px solid #f59e0b; display: flex; align-items: center; gap: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <div style="font-size: 2rem;">⏳</div>
                <div>
                    <div style="font-size: 1.75rem; font-weight: 700;">{summary?.pending || 0}</div>
                    <div style="color: #64748b; font-size: 0.875rem;">چاوەڕوان</div>
                </div>
            </div>
            
            <div style="background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; border-right: 4px solid #ef4444; display: flex; align-items: center; gap: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <div style="font-size: 2rem;">📝</div>
                <div>
                    <div style="font-size: 1.75rem; font-weight: 700;">{summary?.pending_q10 || 0}</div>
                    <div style="color: #64748b; font-size: 0.875rem;">چاوەڕوانی پرسیاری ١٠</div>
                </div>
            </div>
        </div>

        <!-- Team Breakdown -->
        <div style="background: white; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <div style="padding: 1rem 1.5rem; border-bottom: 1px solid #e2e8f0; font-weight: 600;">پێشکەوتنی تیمەکان</div>
            <div style="padding: 1.5rem;">
                <div style="display: flex; flex-direction: column; gap: 1rem;">
                    {#each summary?.team_breakdown || [] as team}
                        <div style="display: grid; grid-template-columns: 100px 1fr 60px; align-items: center; gap: 1rem;">
                            <div style="font-weight: 500;">{team.team_name}</div>
                            <div style="height: 8px; background: #f1f5f9; border-radius: 4px; overflow: hidden;">
                                <div style="height: 100%; background: #10b981; border-radius: 4px; width: {team.total > 0 ? (team.completed / team.total * 100) : 0}%;"></div>
                            </div>
                            <div style="font-size: 0.875rem; color: #64748b;">{team.completed}/{team.total}</div>
                        </div>
                    {/each}
                </div>
            </div>
        </div>

        <!-- Teacher Statistics -->
        <div style="background: white; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <div style="padding: 1rem 1.5rem; border-bottom: 1px solid #e2e8f0; font-weight: 600;">ئاماری مامۆستاکان</div>
            <div style="padding: 1.5rem;">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="border-bottom: 2px solid #e2e8f0;">
                            <th style="padding: 0.75rem; text-align: right;">مامۆستا</th>
                            <th style="padding: 0.75rem; text-align: right;">لیژنە</th>
                            <th style="padding: 0.75rem; text-align: right;">قوتابیانی نمرەدراو</th>
                            <th style="padding: 0.75rem; text-align: right;">ناوەندی کات (خولەک)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each teacherStats as stat}
                            <tr style="border-bottom: 1px solid #e2e8f0;">
                                <td style="padding: 0.75rem;">{stat.teacher_name}</td>
                                <td style="padding: 0.75rem;">{stat.team_name}</td>
                                <td style="padding: 0.75rem;">{stat.total_students_graded}</td>
                                <td style="padding: 0.75rem;">{stat.average_grading_minutes ? stat.average_grading_minutes + ' خولەک' : '-'}</td>
                            </tr>
                        {:else}
                            <tr>
                                <td colspan="4" style="padding: 2rem; text-align: center; color: #64748b;">هێشتا داتای نمرەدان نییە</td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Quick Actions -->
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-top: 1.5rem;">
            <a href="/admin/assign" style="display: flex; flex-direction: column; align-items: center; padding: 1.5rem; background: white; border-radius: 12px; border: 1px solid #e2e8f0; text-decoration: none; color: inherit; transition: all 0.15s; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <span style="font-size: 2rem; margin-bottom: 0.5rem;">📋</span>
                <span>دابەشکردنی قوتابیان</span>
            </a>
            <a href="/admin/q10" style="display: flex; flex-direction: column; align-items: center; padding: 1.5rem; background: white; border-radius: 12px; border: 1px solid #e2e8f0; text-decoration: none; color: inherit; transition: all 0.15s; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <span style="font-size: 2rem; margin-bottom: 0.5rem;">✏️</span>
                <span>نمرەدانی پرسیاری ١٠</span>
            </a>
            <a href="/admin/results" style="display: flex; flex-direction: column; align-items: center; padding: 1.5rem; background: white; border-radius: 12px; border: 1px solid #e2e8f0; text-decoration: none; color: inherit; transition: all 0.15s; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <span style="font-size: 2rem; margin-bottom: 0.5rem;">📥</span>
                <span>ئەنجامەکان</span>
            </a>
            <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
            <div 
                on:click={syncQ10FromStudents}
                style="display: flex; flex-direction: column; align-items: center; padding: 1.5rem; background: {syncingQ10 ? '#e2e8f0' : 'linear-gradient(135deg, #10b981, #059669)'}; border-radius: 12px; border: 1px solid #10b981; cursor: {syncingQ10 ? 'not-allowed' : 'pointer'}; color: white; transition: all 0.15s; box-shadow: 0 1px 3px rgba(0,0,0,0.1);"
            >
                <span style="font-size: 2rem; margin-bottom: 0.5rem;">{syncingQ10 ? '⏳' : '🔄'}</span>
                <span>{syncingQ10 ? 'هاوکاتکردن...' : 'هاوکاتکردنی Q10'}</span>
            </div>
        </div>

        <!-- Danger Zone -->
        <div style="margin-top: 1.5rem;">
            <div style="background: white; border-radius: 12px; border: 1px solid #fca5a5; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <div style="padding: 1rem 1.5rem; border-bottom: 1px solid #fca5a5; font-weight: 600; background: linear-gradient(135deg, #dc3545, #a71d2a); color: white; border-radius: 12px 12px 0 0;">
                    ⚠️ ناوچەی مەترسیدار - سڕینەوەی داتا
                </div>
                <div style="padding: 1.5rem;">
                    <div style="display: flex; flex-direction: column; gap: 1.5rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; background: rgba(220,53,69,0.05); border-radius: 8px; border: 1px solid rgba(220,53,69,0.2); flex-wrap: wrap; gap: 1rem;">
                            <div style="flex: 1;">
                                <strong style="display: block; color: #dc3545; margin-bottom: 0.25rem;">سڕینەوەی نمرەکان</strong>
                                <p style="margin: 0; font-size: 0.875rem; color: #64748b;">هەموو نمرەکان و دابەشکردنەکان دەسڕێتەوە، بەڵام قوتابیان و مامۆستاکان دەمێنن</p>
                            </div>
                            <button class="btn btn-warning" on:click={() => { showResetGradesModal = true; resetConfirmText = ''; }}>
                                🗑️ سڕینەوەی نمرەکان
                            </button>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; background: rgba(220,53,69,0.05); border-radius: 8px; border: 1px solid rgba(220,53,69,0.2); flex-wrap: wrap; gap: 1rem;">
                            <div style="flex: 1;">
                                <strong style="display: block; color: #dc3545; margin-bottom: 0.25rem;">سڕینەوەی هەموو شت</strong>
                                <p style="margin: 0; font-size: 0.875rem; color: #64748b;">هەموو قوتابیان، نمرەکان، و دابەشکردنەکان دەسڕێتەوە (تیمەکان و مامۆستاکان دەمێنن)</p>
                            </div>
                            <button class="btn btn-danger" on:click={() => { showResetEverythingModal = true; resetConfirmText = ''; }}>
                                💥 سڕینەوەی هەموو شت
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    {/if}
</div>

<!-- Reset Grades Modal -->
{#if showResetGradesModal}
    <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
    <div class="modal-overlay" on:click={() => showResetGradesModal = false}>
        <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
        <div class="modal" on:click|stopPropagation>
            <div class="modal-header danger-modal-header">
                ⚠️ سڕینەوەی هەموو نمرەکان
            </div>
            <div class="modal-body">
                <p class="warning-text">
                    ئەم کردارە هەموو نمرەکان و دابەشکردنەکان دەسڕێتەوە!
                </p>
                <p>بۆ دڵنیابوون، تکایە بنووسە: <strong>سڕینەوە</strong></p>
                <input 
                    type="text" 
                    class="form-control" 
                    bind:value={resetConfirmText}
                    placeholder="سڕینەوە"
                />
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" on:click={() => showResetGradesModal = false}>
                    پاشگەزبوونەوە
                </button>
                <button 
                    class="btn btn-danger" 
                    on:click={resetAllGrades}
                    disabled={resetting || resetConfirmText !== 'سڕینەوە'}
                >
                    {resetting ? 'چاوەڕوان بە...' : '🗑️ بەڵێ، بیسڕەوە'}
                </button>
            </div>
        </div>
    </div>
{/if}

<!-- Reset Everything Modal -->
{#if showResetEverythingModal}
    <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
    <div class="modal-overlay" on:click={() => showResetEverythingModal = false}>
        <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
        <div class="modal" on:click|stopPropagation>
            <div class="modal-header danger-modal-header">
                💥 سڕینەوەی هەموو شت
            </div>
            <div class="modal-body">
                <p class="warning-text critical">
                    ئاگاداری! ئەم کردارە هەموو قوتابیان، نمرەکان، و دابەشکردنەکان دەسڕێتەوە!
                </p>
                <p>بۆ دڵنیابوون، تکایە بنووسە: <strong>سڕینەوەی هەموو شت</strong></p>
                <input 
                    type="text" 
                    class="form-control" 
                    bind:value={resetConfirmText}
                    placeholder="سڕینەوەی هەموو شت"
                />
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" on:click={() => showResetEverythingModal = false}>
                    پاشگەزبوونەوە
                </button>
                <button 
                    class="btn btn-danger" 
                    on:click={resetEverything}
                    disabled={resetting || resetConfirmText !== 'سڕینەوەی هەموو شت'}
                >
                    {resetting ? 'چاوەڕوان بە...' : '💥 بەڵێ، هەموو شت بسڕەوە'}
                </button>
            </div>
        </div>
    </div>
{/if}

<style>
    .loading {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 300px;
        flex-direction: column;
    }

    .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid var(--border);
        border-top-color: var(--primary);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    .error-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3rem;
        background: #fee2e2;
        border: 1px solid #fca5a5;
        border-radius: 12px;
        color: #dc2626;
        text-align: center;
        gap: 1rem;
    }

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

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
    }

    @media (max-width: 1024px) {
        .stats-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    @media (max-width: 640px) {
        .stats-grid {
            grid-template-columns: 1fr;
        }
    }

    .stat-card {
        background: var(--surface);
        border-radius: 12px;
        padding: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        border: 1px solid var(--border);
        box-shadow: var(--shadow);
    }

    .stat-card.success { border-right: 4px solid var(--success); }
    .stat-card.warning { border-right: 4px solid var(--warning); }
    .stat-card.danger { border-right: 4px solid var(--danger); }

    .stat-icon {
        font-size: 2rem;
    }

    .stat-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--text);
    }

    .stat-label {
        font-size: 0.875rem;
        color: var(--text-light);
    }

    .team-progress {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .team-item {
        display: grid;
        grid-template-columns: 100px 1fr 60px;
        align-items: center;
        gap: 1rem;
    }

    .team-name {
        font-weight: 500;
    }

    .team-bar {
        height: 8px;
        background: var(--background);
        border-radius: 4px;
        overflow: hidden;
    }

    .team-progress-fill {
        height: 100%;
        background: var(--success);
        border-radius: 4px;
        transition: width 0.3s ease;
    }

    .team-count {
        font-size: 0.875rem;
        color: var(--text-light);
        text-align: left;
    }

    .quick-actions {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
    }

    @media (max-width: 768px) {
        .quick-actions {
            grid-template-columns: 1fr;
        }
    }

    .action-card {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1rem 1.5rem;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        color: var(--text);
        text-decoration: none;
        transition: all 0.15s;
    }

    .action-card:hover {
        background: var(--primary);
        color: white;
        text-decoration: none;
    }

    .action-icon {
        font-size: 1.25rem;
    }

    /* Danger Zone Styles */
    .danger-zone {
        margin-top: 3rem;
    }

    .danger-card {
        border: 2px solid var(--danger);
    }

    .danger-header {
        background: linear-gradient(135deg, #dc3545 0%, #a71d2a 100%);
        color: white;
        font-weight: 600;
    }

    .danger-actions {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }

    .danger-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem;
        background: rgba(220, 53, 69, 0.05);
        border-radius: 8px;
        border: 1px solid rgba(220, 53, 69, 0.2);
    }

    .danger-info {
        flex: 1;
    }

    .danger-info strong {
        display: block;
        margin-bottom: 0.25rem;
        color: var(--danger);
    }

    .danger-info p {
        margin: 0;
        font-size: 0.875rem;
        color: var(--text-light);
    }

    .danger-item .btn {
        margin-right: 1rem;
        white-space: nowrap;
    }

    @media (max-width: 768px) {
        .danger-item {
            flex-direction: column;
            gap: 1rem;
            text-align: center;
        }

        .danger-item .btn {
            margin-right: 0;
            width: 100%;
        }
    }

    /* Modal Danger Header */
    .danger-modal-header {
        background: linear-gradient(135deg, #dc3545 0%, #a71d2a 100%);
        color: white;
    }

    .warning-text {
        background: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 8px;
        padding: 1rem;
        color: #856404;
        text-align: center;
        margin-bottom: 1rem;
    }

    .warning-text.critical {
        background: #f8d7da;
        border-color: #dc3545;
        color: #721c24;
    }
</style>
