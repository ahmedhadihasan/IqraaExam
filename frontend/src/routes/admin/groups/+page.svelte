<script>
    import { onMount } from 'svelte';
    import { questionGroupsAPI } from '$lib/api.js';
    import { showError, showNotification } from '$lib/stores.js';

    let groups = [];
    let loading = true;

    // Edit modal
    let showEditModal = false;
    let editingGroup = null;
    let submitting = false;

    onMount(async () => {
        await loadGroups();
    });

    async function loadGroups() {
        loading = true;
        try {
            groups = await questionGroupsAPI.getAll();
        } catch (error) {
            showError('نەتوانرا گرووپەکان بهێنرێت');
        } finally {
            loading = false;
        }
    }

    function openEditModal(group) {
        editingGroup = {
            ...group,
            marks_structure: { ...group.marks_structure }
        };
        showEditModal = true;
    }

    async function updateGroup() {
        if (!editingGroup.name || !editingGroup.code) {
            showError('تکایە ناو و کۆد پڕبکەوە');
            return;
        }

        submitting = true;
        try {
            await questionGroupsAPI.update(editingGroup.id, {
                name: editingGroup.name,
                code: editingGroup.code,
                marks_structure: editingGroup.marks_structure
            });

            showNotification('گرووپ بە سەرکەوتوویی نوێکرایەوە');
            showEditModal = false;
            editingGroup = null;
            await loadGroups();
        } catch (error) {
            showError('نەتوانرا گرووپ نوێبکرێتەوە');
        } finally {
            submitting = false;
        }
    }
</script>

<div class="groups-page">
    <h1>گرووپی پرسیارەکان</h1>
    <p class="subtitle">گرووپی پرسیارەکان و نمرەکانیان بۆ هەر پرسیارێک</p>

    <!-- Edit Group Modal -->
    {#if showEditModal && editingGroup}
        <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
        <div class="modal-overlay" on:click={() => showEditModal = false}>
            <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
            <div class="modal modal-lg" on:click|stopPropagation>
                <div class="modal-header">
                    <h2>دەستکاریکردنی گرووپ</h2>
                    <button class="modal-close" on:click={() => showEditModal = false}>✕</button>
                </div>
                <div class="modal-body">
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">ناوی گرووپ</label>
                            <input 
                                type="text" 
                                class="form-input" 
                                bind:value={editingGroup.name}
                            />
                        </div>
                        <div class="form-group">
                            <label class="form-label">کۆد</label>
                            <input 
                                type="text" 
                                class="form-input" 
                                bind:value={editingGroup.code}
                                maxlength="1"
                            />
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">نمرەکانی پرسیارەکان</label>
                        <div class="marks-edit-grid">
                            {#each Object.entries(editingGroup.marks_structure) as [q, marks]}
                                <div class="mark-edit-item">
                                    <label>{q.toUpperCase()}</label>
                                    <input 
                                        type="number" 
                                        class="form-input"
                                        bind:value={editingGroup.marks_structure[q]}
                                        min="0"
                                        max="100"
                                    />
                                </div>
                            {/each}
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" on:click={() => showEditModal = false}>
                        پاشگەزبوونەوە
                    </button>
                    <button 
                        class="btn btn-success" 
                        on:click={updateGroup}
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
        <div class="groups-grid">
            {#each groups as group}
                <div class="group-card">
                    <div class="group-header">
                        <div class="group-code">{group.code}</div>
                        <div class="group-info">
                            <h3>{group.name}</h3>
                            <span class="group-total">کۆی نمرە: {group.total_marks}</span>
                        </div>
                        <button 
                            class="btn-icon" 
                            on:click={() => openEditModal(group)}
                            title="دەستکاریکردن"
                        >
                            ✏️
                        </button>
                    </div>
                    <div class="group-body">
                        <div class="marks-grid">
                            {#each Object.entries(group.marks_structure) as [q, marks]}
                                <div class="mark-item">
                                    <span class="q-label">{q.toUpperCase()}</span>
                                    <span class="q-marks">{marks}</span>
                                </div>
                            {/each}
                            <div class="mark-item q10">
                                <span class="q-label">پ١٠</span>
                                <span class="q-marks">١٠</span>
                            </div>
                        </div>
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

    .groups-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 1.5rem;
    }

    .group-card {
        background: var(--surface);
        border-radius: 12px;
        border: 1px solid var(--border);
        overflow: hidden;
        box-shadow: var(--shadow);
    }

    .group-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem 1.25rem;
        background: var(--background);
        border-bottom: 1px solid var(--border);
    }

    .group-code {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: var(--primary);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        font-weight: 700;
        flex-shrink: 0;
    }

    .group-info {
        flex: 1;
    }

    .group-info h3 {
        margin: 0 0 0.25rem;
        font-size: 1rem;
    }

    .group-total {
        font-size: 0.875rem;
        color: var(--text-light);
    }

    .btn-icon {
        background: var(--bg-dark);
        border: 1px solid var(--border);
        padding: 0.5rem;
        border-radius: 6px;
        cursor: pointer;
        font-size: 1rem;
        transition: background 0.2s;
    }

    .btn-icon:hover {
        background: var(--primary);
    }

    .group-body {
        padding: 1.25rem;
    }

    .marks-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 0.5rem;
    }

    .mark-item {
        background: var(--background);
        border-radius: 8px;
        padding: 0.75rem;
        text-align: center;
    }

    .mark-item.q10 {
        background: var(--primary);
        color: white;
    }

    .q-label {
        display: block;
        font-size: 0.75rem;
        color: var(--text-light);
        margin-bottom: 0.25rem;
    }

    .mark-item.q10 .q-label {
        color: rgba(255,255,255,0.8);
    }

    .q-marks {
        font-size: 1.25rem;
        font-weight: 700;
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

    .modal-lg {
        max-width: 550px;
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

    .form-row {
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: 1rem;
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

    .marks-edit-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.75rem;
    }

    .mark-edit-item {
        text-align: center;
    }

    .mark-edit-item label {
        display: block;
        font-size: 0.75rem;
        color: var(--text-light);
        margin-bottom: 0.25rem;
    }

    .mark-edit-item input {
        text-align: center;
        padding: 0.5rem;
    }

    /* Responsive */
    @media (max-width: 600px) {
        .groups-grid {
            grid-template-columns: 1fr;
        }

        .marks-grid {
            grid-template-columns: repeat(3, 1fr);
        }

        .marks-edit-grid {
            grid-template-columns: repeat(2, 1fr);
        }

        .form-row {
            grid-template-columns: 1fr;
        }
    }
</style>
