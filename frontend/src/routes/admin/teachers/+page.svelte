<script>
    import { onMount } from 'svelte';
    import { teamsAPI } from '$lib/api.js';
    import { showNotification, showError } from '$lib/stores.js';

    let teams = [];
    let loading = true;

    // Edit modals
    let showTeamModal = false;
    let showTeacherModal = false;
    let editingTeam = null;
    let editingTeacher = null;
    let submitting = false;

    onMount(loadTeams);

    async function loadTeams() {
        loading = true;
        try {
            teams = await teamsAPI.getAll();
        } catch (error) {
            showError('نەتوانرا تیمەکان بهێنرێت');
        } finally {
            loading = false;
        }
    }

    function openEditTeam(team) {
        editingTeam = { ...team };
        showTeamModal = true;
    }

    function openEditTeacher(teacher) {
        editingTeacher = { ...teacher };
        showTeacherModal = true;
    }

    async function updateTeam() {
        if (!editingTeam.name) {
            showError('تکایە ناوی تیم بنووسە');
            return;
        }

        submitting = true;
        try {
            await teamsAPI.update(editingTeam.id, { name: editingTeam.name });
            showNotification('تیم بە سەرکەوتوویی نوێکرایەوە');
            showTeamModal = false;
            editingTeam = null;
            await loadTeams();
        } catch (error) {
            showError('نەتوانرا تیم نوێبکرێتەوە');
        } finally {
            submitting = false;
        }
    }

    async function updateTeacher() {
        if (!editingTeacher.name) {
            showError('تکایە ناوی مامۆستا بنووسە');
            return;
        }

        submitting = true;
        try {
            await teamsAPI.updateTeacher(editingTeacher.id, {
                name: editingTeacher.name,
                team_id: editingTeacher.team_id,
                position: editingTeacher.position
            });

            showNotification('مامۆستا بە سەرکەوتوویی نوێکرایەوە');
            showTeacherModal = false;
            editingTeacher = null;
            await loadTeams();
        } catch (error) {
            showError('نەتوانرا مامۆستا نوێبکرێتەوە');
        } finally {
            submitting = false;
        }
    }
</script>

<div class="teachers-page">
    <h1>مامۆستاکان</h1>
    <p class="subtitle">بەڕێوەبردنی تیمەکان و مامۆستاکانیان</p>

    <!-- Edit Team Modal -->
    {#if showTeamModal && editingTeam}
        <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
        <div class="modal-overlay" on:click={() => showTeamModal = false}>
            <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
            <div class="modal" on:click|stopPropagation>
                <div class="modal-header">
                    <h2>دەستکاریکردنی تیم</h2>
                    <button class="modal-close" on:click={() => showTeamModal = false}>✕</button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label class="form-label">ناوی تیم</label>
                        <input 
                            type="text" 
                            class="form-input" 
                            bind:value={editingTeam.name}
                        />
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" on:click={() => showTeamModal = false}>
                        پاشگەزبوونەوە
                    </button>
                    <button 
                        class="btn btn-success" 
                        on:click={updateTeam}
                        disabled={submitting}
                    >
                        {submitting ? 'پاشەکەوتکردن...' : 'پاشەکەوتکردن'}
                    </button>
                </div>
            </div>
        </div>
    {/if}

    <!-- Edit Teacher Modal -->
    {#if showTeacherModal && editingTeacher}
        <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
        <div class="modal-overlay" on:click={() => showTeacherModal = false}>
            <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
            <div class="modal" on:click|stopPropagation>
                <div class="modal-header">
                    <h2>دەستکاریکردنی مامۆستا</h2>
                    <button class="modal-close" on:click={() => showTeacherModal = false}>✕</button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label class="form-label">ناوی مامۆستا</label>
                        <input 
                            type="text" 
                            class="form-input" 
                            bind:value={editingTeacher.name}
                        />
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" on:click={() => showTeacherModal = false}>
                        پاشگەزبوونەوە
                    </button>
                    <button 
                        class="btn btn-success" 
                        on:click={updateTeacher}
                        disabled={submitting}
                    >
                        {submitting ? 'پاشەکەوتکردن...' : 'پاشەکەوتکردن'}
                    </button>
                </div>
            </div>
        </div>
    {/if}

    {#if loading}
        <div class="loading">
            <div class="spinner"></div>
        </div>
    {:else}
        <div class="teams-grid">
            {#each teams as team}
                <div class="team-card">
                    <div class="team-header">
                        <h2>{team.name}</h2>
                        <button class="btn-icon" on:click={() => openEditTeam(team)} title="دەستکاریکردن">
                            ✏️
                        </button>
                    </div>
                    <div class="team-body">
                        {#each team.teachers as teacher}
                            <div class="teacher-row">
                                <div class="teacher-info">
                                    <span class="teacher-position">مامۆستای {teacher.position}</span>
                                    <span class="teacher-name">{teacher.name}</span>
                                </div>
                                <button 
                                    class="btn btn-secondary btn-sm"
                                    on:click={() => openEditTeacher(teacher)}
                                    title="دەستکاریکردن"
                                >
                                    ✏️
                                </button>
                            </div>
                        {:else}
                            <p class="no-teachers">هیچ مامۆستایەک نییە</p>
                        {/each}
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</div>

<style>
    .subtitle {
        color: var(--text-light);
        margin-bottom: 2rem;
    }

    .teams-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 1.5rem;
    }

    .team-card {
        background: var(--surface);
        border-radius: 12px;
        border: 1px solid var(--border);
        overflow: hidden;
        box-shadow: var(--shadow);
    }

    .team-header {
        background: var(--primary);
        color: white;
        padding: 1rem 1.25rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .team-header h2 {
        font-size: 1.125rem;
        margin: 0;
    }

    .btn-icon {
        background: rgba(255,255,255,0.2);
        border: none;
        padding: 0.5rem;
        border-radius: 6px;
        cursor: pointer;
        font-size: 1rem;
        transition: background 0.2s;
    }

    .btn-icon:hover {
        background: rgba(255,255,255,0.3);
    }

    .team-body {
        padding: 1rem 1.25rem;
    }

    .teacher-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 0;
        border-bottom: 1px solid var(--border);
    }

    .teacher-row:last-child {
        border-bottom: none;
    }

    .teacher-info {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }

    .teacher-position {
        font-size: 0.75rem;
        color: var(--text-light);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .teacher-name {
        font-weight: 500;
    }

    .no-teachers {
        color: var(--text-light);
        font-size: 0.875rem;
        text-align: center;
        padding: 1rem;
    }

    .btn-sm {
        padding: 0.375rem 0.75rem;
        font-size: 0.75rem;
    }

    /* Modal Styles */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        padding: 1rem;
    }

    .modal {
        background: var(--card-bg);
        border-radius: 12px;
        max-width: 400px;
        width: 100%;
        max-height: 90vh;
        overflow-y: auto;
    }

    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 1.5rem;
        border-bottom: 1px solid var(--border-color);
    }

    .modal-header h2 {
        margin: 0;
        font-size: 1.25rem;
    }

    .modal-close {
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        color: var(--text-light);
    }

    .modal-body {
        padding: 1.5rem;
    }

    .modal-footer {
        display: flex;
        justify-content: flex-end;
        gap: 0.75rem;
        padding: 1rem 1.5rem;
        border-top: 1px solid var(--border-color);
    }

    .form-group {
        margin-bottom: 1rem;
    }

    .form-label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }

    .form-input {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid var(--border);
        border-radius: 8px;
        background: var(--bg-dark);
        color: var(--text);
        font-size: 1rem;
    }

    /* Responsive */
    @media (max-width: 600px) {
        .teams-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
