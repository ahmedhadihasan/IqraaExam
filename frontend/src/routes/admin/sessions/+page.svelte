<script>
    import { onMount } from 'svelte';
    import { examSessionsAPI } from '$lib/api.js';
    import { showNotification, showError } from '$lib/stores.js';

    let sessions = [];
    let loading = true;
    let showForm = false;
    let newSession = { 
        name: '', 
        date: new Date().toISOString().split('T')[0],
        num_rooms: 4,
        teachers_per_room: 2
    };
    let submitting = false;

    // Edit modal
    let showEditModal = false;
    let editingSession = null;

    onMount(loadSessions);

    async function loadSessions() {
        loading = true;
        try {
            sessions = await examSessionsAPI.getAll();
        } catch (error) {
            showError('نەتوانرا دانیشتنەکان بهێنرێت');
        } finally {
            loading = false;
        }
    }

    async function createSession() {
        if (!newSession.name) {
            showError('تکایە ناوی دانیشتن بنووسە');
            return;
        }

        if (newSession.teachers_per_room < 2 || newSession.teachers_per_room > 3) {
            showError('ژمارەی مامۆستا دەبێت ٢ یان ٣ بێت');
            return;
        }

        submitting = true;
        try {
            await examSessionsAPI.create({
                name: newSession.name,
                date: new Date(newSession.date).toISOString(),
                num_rooms: parseInt(newSession.num_rooms),
                teachers_per_room: parseInt(newSession.teachers_per_room)
            });
            showNotification('دانیشتن بە سەرکەوتوویی دروستکرا');
            newSession = { 
                name: '', 
                date: new Date().toISOString().split('T')[0],
                num_rooms: 4,
                teachers_per_room: 2
            };
            showForm = false;
            await loadSessions();
        } catch (error) {
            showError('نەتوانرا دانیشتن دروستبکرێت: ' + (error.message || ''));
        } finally {
            submitting = false;
        }
    }

    function openEditModal(session) {
        editingSession = { 
            ...session,
            date: session.date ? session.date.split('T')[0] : new Date().toISOString().split('T')[0],
            num_rooms: session.num_rooms || 4,
            teachers_per_room: session.teachers_per_room || 2
        };
        showEditModal = true;
    }

    async function updateSession() {
        if (!editingSession.name) {
            showError('تکایە ناوی دانیشتن بنووسە');
            return;
        }

        if (editingSession.teachers_per_room < 2 || editingSession.teachers_per_room > 3) {
            showError('ژمارەی مامۆستا دەبێت ٢ یان ٣ بێت');
            return;
        }

        submitting = true;
        try {
            await examSessionsAPI.update(editingSession.id, {
                name: editingSession.name,
                date: new Date(editingSession.date).toISOString(),
                num_rooms: parseInt(editingSession.num_rooms),
                teachers_per_room: parseInt(editingSession.teachers_per_room)
            });
            showNotification('دانیشتن بە سەرکەوتوویی نوێکرایەوە');
            showEditModal = false;
            editingSession = null;
            await loadSessions();
        } catch (error) {
            showError('نەتوانرا دانیشتن نوێبکرێتەوە');
        } finally {
            submitting = false;
        }
    }

    async function setActive(id) {
        try {
            await examSessionsAPI.activate(id);
            showNotification('دانیشتن چالاککرا - ئێستا قوتابیانی ئەم دانیشتنە پیشان دەدرێن');
            await loadSessions();
        } catch (error) {
            showError('نەتوانرا دانیشتنی چالاک بگۆڕدرێت');
        }
    }

    async function deactivateSession(id) {
        try {
            await examSessionsAPI.deactivate(id);
            showNotification('دانیشتن ناچالاککرا');
            await loadSessions();
        } catch (error) {
            showError('نەتوانرا دانیشتن ناچالاک بکرێت');
        }
    }

    async function deleteSession(id) {
        if (!confirm('ئایا دڵنیایت لە سڕینەوەی ئەم دانیشتنە?')) return;
        
        try {
            await examSessionsAPI.delete(id);
            showNotification('دانیشتن سڕایەوە');
            await loadSessions();
        } catch (error) {
            showError('نەتوانرا دانیشتن بسڕێتەوە');
        }
    }

    const kurdishMonths = [
        'کانوونی دووەم', 'شوبات', 'ئازار', 'نیسان', 'ئایار', 'حوزەیران',
        'تەممووز', 'ئاب', 'ئەیلوول', 'تشرینی یەکەم', 'تشرینی دووەم', 'کانوونی یەکەم'
    ];

    function formatDate(dateStr) {
        if (!dateStr) return '-';
        const date = new Date(dateStr);
        const day = date.getDate();
        const month = kurdishMonths[date.getMonth()];
        const year = date.getFullYear();
        return `${day} ${month} ${year}`;
    }

    function getTeacherRoles(teachersPerRoom) {
        if (teachersPerRoom === 2) {
            return '١ سەرۆک + ١ ئەندام';
        } else if (teachersPerRoom === 3) {
            return '١ سەرۆک + ٢ ئەندام';
        }
        return teachersPerRoom + ' مامۆستا';
    }
</script>

<div class="sessions-page">
    <div class="page-header">
        <h1>دانیشتنەکانی تاقیکردنەوە</h1>
        <button class="btn btn-primary" on:click={() => showForm = !showForm}>
            {showForm ? '✕ پاشگەزبوونەوە' : '+ دانیشتنی نوێ'}
        </button>
    </div>

    <!-- Edit Modal -->
    {#if showEditModal && editingSession}
        <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
        <div class="modal-overlay" on:click={() => showEditModal = false}>
            <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
            <div class="modal" on:click|stopPropagation>
                <div class="modal-header">
                    <h2>دەستکاریکردنی دانیشتن</h2>
                    <button class="modal-close" on:click={() => showEditModal = false}>✕</button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label class="form-label">ناوی دانیشتن</label>
                        <input 
                            type="text" 
                            class="form-input" 
                            bind:value={editingSession.name}
                        />
                    </div>
                    <div class="form-group">
                        <label class="form-label">بەروار</label>
                        <input 
                            type="date" 
                            class="form-input" 
                            bind:value={editingSession.date}
                        />
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">ژمارەی ژوورەکان</label>
                            <input 
                                type="number" 
                                class="form-input" 
                                bind:value={editingSession.num_rooms}
                                min="1"
                                max="10"
                            />
                        </div>
                        <div class="form-group">
                            <label class="form-label">مامۆستا لە هەر ژوورێک</label>
                            <select class="form-select" bind:value={editingSession.teachers_per_room}>
                                <option value={2}>٢ (١ سەرۆک + ١ ئەندام)</option>
                                <option value={3}>٣ (١ سەرۆک + ٢ ئەندام)</option>
                            </select>
                        </div>
                    </div>
                    <div class="info-box">
                        <strong>کۆی گشتی:</strong> {editingSession.num_rooms || 0} × {editingSession.teachers_per_room || 0} = {(editingSession.num_rooms || 0) * (editingSession.teachers_per_room || 0)} مامۆستا
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" on:click={() => showEditModal = false}>پاشگەزبوونەوە</button>
                    <button class="btn btn-success" on:click={updateSession} disabled={submitting}>
                        {submitting ? 'پاشەکەوتکردن...' : 'پاشەکەوتکردن'}
                    </button>
                </div>
            </div>
        </div>
    {/if}

    {#if showForm}
        <div class="card mb-4">
            <div class="card-header">دروستکردنی دانیشتنی نوێ</div>
            <div class="card-body">
                <form on:submit|preventDefault={createSession}>
                    <div class="form-grid-2">
                        <div class="form-group">
                            <label class="form-label">ناوی دانیشتن</label>
                            <input 
                                type="text" 
                                class="form-input" 
                                bind:value={newSession.name}
                                placeholder="نموونە: تاقیکردنەوەی مانگی کانوونی دووەم ٢٠٢٦"
                            />
                        </div>
                        <div class="form-group">
                            <label class="form-label">بەروار</label>
                            <input 
                                type="date" 
                                class="form-input" 
                                bind:value={newSession.date}
                            />
                        </div>
                    </div>
                    <div class="form-grid-2">
                        <div class="form-group">
                            <label class="form-label">ژمارەی ژوورەکان (تیمەکان)</label>
                            <input 
                                type="number" 
                                class="form-input" 
                                bind:value={newSession.num_rooms}
                                min="1"
                                max="10"
                            />
                            <small class="form-hint">هەر ژوورێک تیمێکی جیاوازی هەیە</small>
                        </div>
                        <div class="form-group">
                            <label class="form-label">ژمارەی مامۆستا لە هەر ژوورێک</label>
                            <select class="form-select" bind:value={newSession.teachers_per_room}>
                                <option value={2}>٢ مامۆستا (١ سەرۆک + ١ ئەندام)</option>
                                <option value={3}>٣ مامۆستا (١ سەرۆک + ٢ ئەندام)</option>
                            </select>
                            <small class="form-hint">سەرۆک لیژنە نمرەکان پێکدەهێنێت</small>
                        </div>
                    </div>
                    <div class="info-box">
                        <strong>کۆی گشتی:</strong> {newSession.num_rooms} ژوور × {newSession.teachers_per_room} مامۆستا = <strong>{newSession.num_rooms * newSession.teachers_per_room}</strong> مامۆستا
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="btn btn-success" disabled={submitting}>
                            {submitting ? 'دروستکردن...' : 'دروستکردنی دانیشتن'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    {/if}

    {#if loading}
        <div class="loading">
            <div class="spinner"></div>
        </div>
    {:else}
        <div class="sessions-grid">
            {#each sessions as session}
                <div class="session-card" class:active={session.is_active}>
                    <div class="session-header">
                        <h3>{session.name}</h3>
                        {#if session.is_active}
                            <span class="active-badge">چالاک</span>
                        {/if}
                    </div>
                    <div class="session-body">
                        <div class="session-info">
                            <div class="info-item">
                                <span class="info-label">📅 بەروار:</span>
                                <span class="info-value">{formatDate(session.date)}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">🚪 ژوورەکان:</span>
                                <span class="info-value">{session.num_rooms || 4}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">👥 مامۆستاکان:</span>
                                <span class="info-value">{getTeacherRoles(session.teachers_per_room || 2)}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">📊 کۆی مامۆستا:</span>
                                <span class="info-value">{(session.num_rooms || 4) * (session.teachers_per_room || 2)}</span>
                            </div>
                        </div>
                    </div>
                    <div class="session-footer">
                        <div class="footer-actions">
                            <button class="btn btn-outline btn-sm" on:click={() => openEditModal(session)}>
                                ✏️ دەستکاری
                            </button>
                            {#if session.is_active}
                                <button class="btn btn-warning btn-sm" on:click={() => deactivateSession(session.id)}>
                                    ⏸️ ناچالاککردن
                                </button>
                                <span class="current-label">دانیشتنی ئێستا</span>
                            {:else}
                                <button class="btn btn-success btn-sm" on:click={() => setActive(session.id)}>
                                    ▶️ چالاککردن
                                </button>
                                <button class="btn btn-danger btn-sm" on:click={() => deleteSession(session.id)}>
                                    🗑️
                                </button>
                            {/if}
                        </div>
                    </div>
                </div>
            {:else}
                <div class="empty-state">
                    <p>هیچ دانیشتنێک نییە</p>
                    <p class="text-light">کرتە بکە لە "دانیشتنی نوێ" بۆ دروستکردن</p>
                </div>
            {/each}
        </div>
    {/if}
</div>

<style>
    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }

    /* Modal Styles */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }

    .modal {
        background: var(--surface);
        border-radius: 12px;
        width: 90%;
        max-width: 500px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        overflow: hidden;
    }

    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 1.5rem;
        background: var(--background);
        border-bottom: 1px solid var(--border);
    }

    .modal-header h3 {
        margin: 0;
    }

    .modal-close {
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        color: var(--text-light);
        padding: 0;
        line-height: 1;
    }

    .modal-close:hover {
        color: var(--danger);
    }

    .modal-body {
        padding: 1.5rem;
    }

    .modal-footer {
        display: flex;
        justify-content: flex-end;
        gap: 0.75rem;
        padding: 1rem 1.5rem;
        border-top: 1px solid var(--border);
    }

    /* Create Form Card */
    .create-card {
        background: var(--surface);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid var(--border);
        margin-bottom: 2rem;
    }

    .create-card h3 {
        margin-top: 0;
        margin-bottom: 1rem;
        color: var(--primary);
    }

    /* Form Styles */
    .form-row {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-bottom: 1rem;
    }

    .form-grid-2 {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
    }

    @media (max-width: 600px) {
        .form-grid-2 {
            grid-template-columns: 1fr;
        }
    }

    .form-group {
        margin-bottom: 1rem;
    }

    .form-label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }

    .form-input, .form-select {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid var(--border);
        border-radius: 8px;
        font-size: 1rem;
        background: var(--background);
    }

    .form-input:focus, .form-select:focus {
        outline: none;
        border-color: var(--primary);
    }

    .form-hint {
        display: block;
        font-size: 0.75rem;
        color: var(--text-light);
        margin-top: 0.25rem;
    }

    .form-actions {
        display: flex;
        justify-content: flex-end;
        gap: 0.75rem;
    }

    .info-box {
        background: var(--background);
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-top: 1rem;
        font-size: 0.875rem;
        color: var(--text-light);
        border-right: 3px solid var(--primary);
    }

    /* Sessions Grid */
    .sessions-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 1.5rem;
    }

    .session-card {
        background: var(--surface);
        border-radius: 12px;
        border: 1px solid var(--border);
        overflow: hidden;
        box-shadow: var(--shadow);
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .session-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }

    .session-card.active {
        border-color: var(--success);
        border-width: 2px;
    }

    .session-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 1.25rem;
        background: var(--background);
        border-bottom: 1px solid var(--border);
    }

    .session-header h3 {
        margin: 0;
        font-size: 1rem;
    }

    .active-badge {
        background: var(--success);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
    }

    .session-body {
        padding: 1rem 1.25rem;
    }

    .session-info {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .info-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0;
        border-bottom: 1px dashed var(--border);
    }

    .info-item:last-child {
        border-bottom: none;
    }

    .info-label {
        color: var(--text-light);
        font-size: 0.875rem;
    }

    .info-value {
        font-weight: 500;
        color: var(--text);
    }

    .session-footer {
        padding: 1rem 1.25rem;
        border-top: 1px solid var(--border);
        background: var(--background);
    }

    .footer-actions {
        display: flex;
        gap: 0.5rem;
        align-items: center;
        flex-wrap: wrap;
    }

    .current-label {
        color: var(--success);
        font-size: 0.875rem;
        font-weight: 500;
    }

    .btn-sm {
        padding: 0.375rem 0.75rem;
        font-size: 0.75rem;
    }

    .btn-warning {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
        border: none;
    }

    .btn-warning:hover {
        background: linear-gradient(135deg, #d97706, #b45309);
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
    }

    .empty-state {
        grid-column: 1 / -1;
        text-align: center;
        padding: 3rem;
        color: var(--text-light);
        background: var(--surface);
        border-radius: 8px;
        border: 1px dashed var(--border);
    }

    .loading {
        display: flex;
        justify-content: center;
        padding: 3rem;
    }

    .spinner {
        width: 40px;
        height: 40px;
        border: 3px solid var(--border);
        border-top-color: var(--primary);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }
</style>
