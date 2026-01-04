<script>
    import { onMount } from 'svelte';
    import { studentsAPI } from '$lib/api.js';
    import { showNotification, showError } from '$lib/stores.js';

    let students = [];
    let loading = true;
    let searchQuery = '';
    
    // New student form
    let showForm = false;
    let newStudent = { name: '', birth_year: '', regular_teacher: '', phone: '', q10_mark: '' };
    let submitting = false;

    // Edit student modal
    let showEditModal = false;
    let editingStudent = null;

    // CSV Import
    let showCsvModal = false;
    let csvFile = null;
    let importing = false;
    let importResult = null;

    onMount(loadStudents);

    async function loadStudents() {
        loading = true;
        try {
            students = await studentsAPI.getAll();
        } catch (error) {
            showError('نەتوانرا قوتابیان بهێنرێت');
        } finally {
            loading = false;
        }
    }

    async function addStudent() {
        if (!newStudent.name) {
            showError('تکایە ناوی قوتابی بنووسە');
            return;
        }

        // Validate Q10 mark (must be 0-10)
        let q10Value = null;
        if (newStudent.q10_mark !== '' && newStudent.q10_mark !== null) {
            q10Value = parseFloat(newStudent.q10_mark);
            if (isNaN(q10Value) || q10Value < 0 || q10Value > 10) {
                showError('نمرەی پرسیاری دەیەم دەبێت لە نێوان ٠ تا ١٠ بێت');
                return;
            }
        }

        submitting = true;
        try {
            const studentData = {
                name: newStudent.name,
                birth_year: newStudent.birth_year ? parseInt(newStudent.birth_year) : null,
                regular_teacher: newStudent.regular_teacher || null,
                phone: newStudent.phone || null,
                q10_mark: q10Value
            };
            await studentsAPI.create(studentData);
            showNotification('قوتابی بە سەرکەوتوویی زیادکرا');
            newStudent = { name: '', birth_year: '', regular_teacher: '', phone: '', q10_mark: '' };
            showForm = false;
            await loadStudents();
        } catch (error) {
            showError('نەتوانرا قوتابی زیادبکرێت');
        } finally {
            submitting = false;
        }
    }

    function openEditModal(student) {
        editingStudent = { ...student };
        showEditModal = true;
    }

    async function updateStudent() {
        if (!editingStudent.name) {
            showError('تکایە ناوی قوتابی بنووسە');
            return;
        }

        // Validate Q10 mark (must be 0-10)
        let q10Value = null;
        if (editingStudent.q10_mark !== '' && editingStudent.q10_mark !== null && editingStudent.q10_mark !== undefined) {
            q10Value = parseFloat(editingStudent.q10_mark);
            if (isNaN(q10Value) || q10Value < 0 || q10Value > 10) {
                showError('نمرەی پرسیاری دەیەم دەبێت لە نێوان ٠ تا ١٠ بێت');
                return;
            }
        }

        submitting = true;
        try {
            await studentsAPI.update(editingStudent.id, {
                name: editingStudent.name,
                birth_year: editingStudent.birth_year ? parseInt(editingStudent.birth_year) : null,
                regular_teacher: editingStudent.regular_teacher || null,
                phone: editingStudent.phone || null,
                q10_mark: q10Value
            });
            showNotification('قوتابی بە سەرکەوتوویی نوێکرایەوە');
            showEditModal = false;
            editingStudent = null;
            await loadStudents();
        } catch (error) {
            showError('نەتوانرا قوتابی نوێبکرێتەوە');
        } finally {
            submitting = false;
        }
    }

    async function deleteStudent(id) {
        if (!confirm('ئایا دڵنیایت لە سڕینەوەی ئەم قوتابییە؟')) return;
        
        try {
            await studentsAPI.delete(id);
            showNotification('قوتابی سڕایەوە');
            await loadStudents();
        } catch (error) {
            showError('نەتوانرا قوتابی بسڕێتەوە');
        }
    }

    function handleFileSelect(event) {
        csvFile = event.target.files[0];
    }

    async function importCsv() {
        if (!csvFile) {
            showError('تکایە فایلی CSV هەڵبژێرە');
            return;
        }

        importing = true;
        importResult = null;

        try {
            const result = await studentsAPI.importCSV(csvFile);
            importResult = result;
            showNotification(result.message);
            await loadStudents();
        } catch (error) {
            showError(error.message || 'نەتوانرا فایل بخوێنرێتەوە');
        } finally {
            importing = false;
        }
    }

    function downloadTemplate() {
        const headers = 'ناوی سییانی,ژمارەی تەلەفۆن,ساڵی لەدایکبوون,مامۆستای بابەت,نمرەی پرسیاری ۱۰\n';
        const example = 'ئەحمەد محمد کەریم,07701234567,2010,مامۆستا علی,8.5\n';
        const content = headers + example;
        
        const blob = new Blob(['\ufeff' + content], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'template_students.csv';
        a.click();
        URL.revokeObjectURL(url);
    }

    async function deleteAllStudents() {
        if (!confirm('ئایا دڵنیایت لە سڕینەوەی هەموو قوتابییەکان؟ ئەم کردارە ناگەڕێتەوە!')) return;
        if (!confirm('دڵنیابوونەوە: هەموو قوتابییەکان دەسڕێنەوە!')) return;

        try {
            await studentsAPI.deleteAll();
            showNotification('هەموو قوتابییەکان سڕانەوە');
            await loadStudents();
        } catch (error) {
            showError('نەتوانرا قوتابییەکان بسڕێنەوە');
        }
    }

    $: filteredStudents = students.filter(s => 
        s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (s.regular_teacher && s.regular_teacher.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (s.phone && s.phone.includes(searchQuery))
    );
</script>

<div class="students-page">
    <div class="page-header">
        <h1>قوتابیان</h1>
        <div class="header-buttons">
            <button class="btn btn-secondary" on:click={() => showCsvModal = true}>
                📁 هاوردەکردنی CSV
            </button>
            <button class="btn btn-primary" on:click={() => showForm = !showForm}>
                {showForm ? '✕ پاشگەزبوونەوە' : '+ زیادکردنی قوتابی'}
            </button>
        </div>
    </div>

    <!-- CSV Import Modal -->
    {#if showCsvModal}
        <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
        <div class="modal-overlay" on:click={() => showCsvModal = false}>
            <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
            <div class="modal" on:click|stopPropagation>
                <div class="modal-header">
                    <h2>هاوردەکردنی قوتابیان لە CSV</h2>
                    <button class="modal-close" on:click={() => showCsvModal = false}>✕</button>
                </div>
                <div class="modal-body">
                    <div class="csv-info">
                        <p>ستوونەکانی فایلی CSV:</p>
                        <ul>
                            <li><strong>ناوی سییانی</strong> - ناوی تەواوی قوتابی <span class="required">(پێویست)</span></li>
                            <li><strong>ژمارەی تەلەفۆن</strong> - ژمارەی مۆبایل (ئارەزوومەندانە)</li>
                            <li><strong>ساڵی لەدایکبوون</strong> - ساڵی لەدایکبوون وەک ٢٠١٠ (ئارەزوومەندانە)</li>
                            <li><strong>مامۆستای بابەت</strong> - ناوی مامۆستای ڕێکوپێک (ئارەزوومەندانە)</li>
                            <li><strong>نمرەی پرسیاری ١٠</strong> - نمرەی پرسیاری دەیەم لە ٠ تا ١٠ (ئارەزوومەندانە)</li>
                        </ul>
                        <button class="btn btn-link" on:click={downloadTemplate}>
                            ⬇️ داگرتنی نموونەی CSV
                        </button>
                    </div>

                    <div class="form-group">
                        <label class="form-label">هەڵبژاردنی فایل</label>
                        <input 
                            type="file" 
                            accept=".csv"
                            class="form-input file-input"
                            on:change={handleFileSelect}
                        />
                    </div>

                    {#if importResult}
                        <div class="import-result">
                            <p class="success-msg">{importResult.message}</p>
                            {#if importResult.errors && importResult.errors.length > 0}
                                <div class="errors">
                                    <p>هەڵەکان:</p>
                                    <ul>
                                        {#each importResult.errors as error}
                                            <li>{error}</li>
                                        {/each}
                                    </ul>
                                </div>
                            {/if}
                        </div>
                    {/if}
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" on:click={() => showCsvModal = false}>
                        داخستن
                    </button>
                    <button 
                        class="btn btn-success" 
                        on:click={importCsv}
                        disabled={!csvFile || importing}
                    >
                        {importing ? 'هاوردەکردن...' : 'هاوردەکردن'}
                    </button>
                </div>
            </div>
        </div>
    {/if}

    <!-- Edit Student Modal -->
    {#if showEditModal && editingStudent}
        <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
        <div class="modal-overlay" on:click={() => showEditModal = false}>
            <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
            <div class="modal" on:click|stopPropagation>
                <div class="modal-header">
                    <h2>دەستکاریکردنی قوتابی</h2>
                    <button class="modal-close" on:click={() => showEditModal = false}>✕</button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label class="form-label">ناوی قوتابی</label>
                        <input 
                            type="text" 
                            class="form-input" 
                            bind:value={editingStudent.name}
                        />
                    </div>
                    <div class="form-group">
                        <label class="form-label">ژمارەی تەلەفۆن</label>
                        <input 
                            type="text" 
                            class="form-input" 
                            bind:value={editingStudent.phone}
                        />
                    </div>
                    <div class="form-group">
                        <label class="form-label">ساڵی لەدایکبوون (ئارەزوومەندانە)</label>
                        <input 
                            type="number" 
                            class="form-input" 
                            bind:value={editingStudent.birth_year}
                            placeholder="وەک ٢٠١٠"
                        />
                    </div>
                    <div class="form-group">
                        <label class="form-label">مامۆستای بابەت</label>
                        <input 
                            type="text" 
                            class="form-input" 
                            bind:value={editingStudent.regular_teacher}
                        />
                    </div>
                    <div class="form-group">
                        <label class="form-label">نمرەی پرسیاری ١٠ (ئارەزوومەندانە)</label>
                        <input 
                            type="number" 
                            class="form-input" 
                            bind:value={editingStudent.q10_mark}
                            placeholder="0 - 10"
                            min="0"
                            max="10"
                            step="0.5"
                        />
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" on:click={() => showEditModal = false}>
                        پاشگەزبوونەوە
                    </button>
                    <button 
                        class="btn btn-success" 
                        on:click={updateStudent}
                        disabled={submitting}
                    >
                        {submitting ? 'پاشەکەوتکردن...' : 'پاشەکەوتکردن'}
                    </button>
                </div>
            </div>
        </div>
    {/if}

    <!-- Add Student Form -->
    {#if showForm}
        <div class="card mb-4">
            <div class="card-header">زیادکردنی قوتابی نوێ</div>
            <div class="card-body">
                <form on:submit|preventDefault={addStudent} class="form-grid">
                    <div class="form-group">
                        <label class="form-label">ناوی قوتابی</label>
                        <input 
                            type="text" 
                            class="form-input" 
                            bind:value={newStudent.name}
                            placeholder="ناوی قوتابی بنووسە"
                        />
                    </div>
                    <div class="form-group">
                        <label class="form-label">ژمارەی تەلەفۆن</label>
                        <input 
                            type="text" 
                            class="form-input" 
                            bind:value={newStudent.phone}
                            placeholder="07xxxxxxxxx"
                        />
                    </div>
                    <div class="form-group">
                        <label class="form-label">ساڵی لەدایکبوون (ئارەزوومەندانە)</label>
                        <input 
                            type="number" 
                            class="form-input" 
                            bind:value={newStudent.birth_year}
                            placeholder="وەک ٢٠١٠"
                        />
                    </div>
                    <div class="form-group">
                        <label class="form-label">مامۆستای بابەت</label>
                        <input 
                            type="text" 
                            class="form-input" 
                            bind:value={newStudent.regular_teacher}
                            placeholder="ناوی مامۆستای بابەت"
                        />
                    </div>
                    <div class="form-group">
                        <label class="form-label">نمرەی پرسیاری ١٠ (ئارەزوومەندانە)</label>
                        <input 
                            type="number" 
                            class="form-input" 
                            bind:value={newStudent.q10_mark}
                            placeholder="0 - 10"
                            min="0"
                            max="10"
                            step="0.5"
                        />
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="btn btn-success" disabled={submitting}>
                            {submitting ? 'زیادکردن...' : 'زیادکردنی قوتابی'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    {/if}

    <!-- Search and Actions -->
    <div class="actions-bar mb-4">
        <div class="search-box">
            <input 
                type="text" 
                class="form-input" 
                placeholder="گەڕان بەدوای قوتابیدا..." 
                bind:value={searchQuery}
            />
        </div>
        <div class="stats">
            <span>کۆی قوتابیان: <strong>{students.length}</strong></span>
            {#if students.length > 0}
                <button class="btn btn-danger btn-sm" on:click={deleteAllStudents}>
                    🗑️ سڕینەوەی هەمووی
                </button>
            {/if}
        </div>
    </div>

    <!-- Students Table -->
    <div class="card">
        <div class="card-body table-responsive">
            {#if loading}
                <div class="loading">
                    <div class="spinner"></div>
                </div>
            {:else}
                <table class="table">
                    <thead>
                        <tr>
                            <th>ژمارە</th>
                            <th>ناو</th>
                            <th>تەلەفۆن</th>
                            <th>ساڵی لەدایکبوون</th>
                            <th>مامۆستای بابەت</th>
                            <th>نمرەی پرسیاری ١٠</th>
                            <th>کردارەکان</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each filteredStudents as student}
                            <tr>
                                <td data-label="ژمارە">{student.id}</td>
                                <td data-label="ناو">{student.name}</td>
                                <td data-label="تەلەفۆن">{student.phone || '-'}</td>
                                <td data-label="ساڵی لەدایکبوون">{student.birth_year || '-'}</td>
                                <td data-label="مامۆستای بابەت">{student.regular_teacher || '-'}</td>
                                <td data-label="نمرەی پرسیاری ١٠">
                                    {#if student.q10_mark !== null && student.q10_mark !== undefined}
                                        <span style="color: #10b981; font-weight: 600;">{student.q10_mark}</span>
                                    {:else}
                                        <span style="color: #9ca3af;">-</span>
                                    {/if}
                                </td>
                                <td data-label="کردارەکان">
                                    <div class="action-buttons">
                                        <button 
                                            class="btn btn-secondary btn-sm"
                                            on:click={() => openEditModal(student)}
                                        >
                                            ✏️
                                        </button>
                                        <button 
                                            class="btn btn-danger btn-sm"
                                            on:click={() => deleteStudent(student.id)}
                                        >
                                            🗑️
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        {:else}
                            <tr>
                                <td colspan="7" class="text-center text-light">
                                    هیچ قوتابییەک نەدۆزرایەوە
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            {/if}
        </div>
    </div>
</div>

<style>
    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
        gap: 1rem;
    }

    .header-buttons {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }

    .form-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr) auto;
        gap: 1rem;
        align-items: end;
    }

    .actions-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
    }

    .search-box {
        flex: 1;
        max-width: 400px;
        min-width: 200px;
    }

    .stats {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .btn-sm {
        padding: 0.375rem 0.75rem;
        font-size: 0.75rem;
    }

    .action-buttons {
        display: flex;
        gap: 0.5rem;
    }

    .table-responsive {
        overflow-x: auto;
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
        max-width: 500px;
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

    .csv-info {
        background: var(--bg-dark);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }

    .csv-info ul {
        margin: 0.5rem 0;
        padding-right: 1.5rem;
    }

    .btn-link {
        background: none;
        border: none;
        color: var(--primary-color);
        cursor: pointer;
        padding: 0;
        text-decoration: underline;
    }

    .file-input {
        padding: 0.5rem;
    }

    .import-result {
        margin-top: 1rem;
        padding: 1rem;
        border-radius: 8px;
        background: var(--bg-dark);
    }

    .success-msg {
        color: var(--success-color);
        font-weight: bold;
    }

    .errors {
        margin-top: 0.5rem;
        color: var(--danger-color);
    }

    .errors ul {
        margin: 0.5rem 0 0;
        padding-right: 1.5rem;
    }

    /* Responsive Styles */
    @media (max-width: 992px) {
        .form-grid {
            grid-template-columns: repeat(2, 1fr);
        }

        .form-actions {
            grid-column: span 2;
        }
    }

    @media (max-width: 768px) {
        .page-header {
            flex-direction: column;
            align-items: stretch;
        }

        .header-buttons {
            justify-content: center;
        }

        .form-grid {
            grid-template-columns: 1fr;
        }

        .form-actions {
            grid-column: span 1;
        }

        .actions-bar {
            flex-direction: column;
            align-items: stretch;
        }

        .search-box {
            max-width: none;
        }

        .stats {
            justify-content: space-between;
        }

        /* Mobile table styles */
        .table thead {
            display: none;
        }

        .table tr {
            display: block;
            margin-bottom: 1rem;
            background: var(--bg-dark);
            border-radius: 8px;
            padding: 1rem;
        }

        .table td {
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid var(--border-color);
        }

        .table td:last-child {
            border-bottom: none;
            justify-content: flex-end;
        }

        .table td::before {
            content: attr(data-label);
            font-weight: bold;
            color: var(--text-light);
        }
    }
</style>
