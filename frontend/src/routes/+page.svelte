<script>
    import { teamsAPI } from '$lib/api.js';
    import { onMount } from 'svelte';

    let teachers = [];
    let loading = true;

    onMount(async () => {
        try {
            teachers = await teamsAPI.getAllTeachers();
        } catch (error) {
            console.error('Failed to load teachers:', error);
        } finally {
            loading = false;
        }
    });

    // Group teachers by team
    $: teachersByTeam = teachers.reduce((acc, teacher) => {
        const teamName = teacher.team?.name || 'نەزانراو';
        if (!acc[teamName]) acc[teamName] = [];
        acc[teamName].push(teacher);
        return acc;
    }, {});
</script>

<div class="home-container">
    <div class="hero">
        <img src="/logo.jpg" alt="لۆگۆی ئیقرا" class="logo-img" />
        <h1>سیستەمی تاقیکردنەوەی بنچینە نوورانییەکان</h1>
        <p>ناوی خۆت هەڵبژێرە بۆ بەردەوامبوون</p>
    </div>

    {#if loading}
        <div class="loading">
            <div class="spinner"></div>
            <p>چاوەڕوانبە...</p>
        </div>
    {:else}
        <div class="instruction-box">
            <span class="instruction-icon"></span>
            <span>لەسەر ناوی خۆت کلیک بکە</span>
        </div>
        <div class="rooms-grid">
            {#each Object.entries(teachersByTeam) as [teamName, teamTeachers]}
                <div class="room-card">
                    <div class="room-header">
                        <h3>{teamName}</h3>
                    </div>
                    <div class="teachers-list">
                        {#each teamTeachers.sort((a, b) => a.position - b.position) as teacher}
                            <a href="/teacher/{teacher.id}" class="teacher-link">
                                <div class="teacher-info">
                                    <span class="teacher-name">{teacher.name}</span>
                                    <span class="teacher-position">{teacher.position === 1 ? 'سەرۆک لیژنە' : 'ئەندام لیژنە'}</span>
                                </div>
                                <span class="teacher-arrow">←</span>
                            </a>
                        {/each}
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</div>

<style>
    .home-container {
        min-height: 100vh;
        padding: 2rem;
        background: #f8f9fa;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .hero {
        text-align: center;
        margin-bottom: 3rem;
    }

    .logo-img {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        object-fit: cover;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .hero h1 {
        font-size: 1.75rem;
        color: #1a1a2e;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }

    .hero p {
        color: #666;
        font-size: 1rem;
    }

    .loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
        padding: 3rem;
    }

    .loading p {
        color: #666;
    }

    .spinner {
        width: 40px;
        height: 40px;
        border: 3px solid #e0e0e0;
        border-top-color: #1a1a2e;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    .rooms-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1.5rem;
        max-width: 900px;
        width: 100%;
    }

    .room-card {
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border: 1px solid #e8e8e8;
    }

    .room-header {
        background: #1a1a2e;
        padding: 1rem 1.25rem;
    }

    .room-header h3 {
        margin: 0;
        color: white;
        font-size: 1.1rem;
        font-weight: 500;
    }

    .teachers-list {
        padding: 0.5rem;
        display: flex;
        flex-direction: column;
    }

    .teacher-link {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 1.25rem;
        color: #333;
        text-decoration: none;
        font-size: 1rem;
        border-radius: 8px;
        transition: all 0.15s ease;
        border: 2px solid transparent;
    }

    .teacher-link:hover {
        background: #e8f4fc;
        border-color: #1a73e8;
    }

    .teacher-info {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }

    .teacher-name {
        font-weight: 500;
    }

    .teacher-position {
        font-size: 0.8rem;
        color: #666;
    }

    .teacher-arrow {
        opacity: 0;
        transform: translateX(5px);
        transition: all 0.15s ease;
        color: #1a73e8;
    }

    .teacher-link:hover .teacher-arrow {
        opacity: 1;
        transform: translateX(0);
    }

    .instruction-box {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        background: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 8px;
        padding: 0.875rem 1.25rem;
        margin-bottom: 1.5rem;
        color: #856404;
        font-size: 0.95rem;
    }

    .instruction-icon {
        font-size: 1.25rem;
    }

    /* Mobile Responsive */
    @media (max-width: 768px) {
        .home-container {
            padding: 1.5rem 1rem;
        }

        .logo-img {
            width: 80px;
            height: 80px;
        }

        .hero h1 {
            font-size: 1.4rem;
        }

        .rooms-grid {
            grid-template-columns: 1fr;
            gap: 1rem;
        }
    }

    @media (max-width: 480px) {
        .hero {
            margin-bottom: 2rem;
        }

        .hero h1 {
            font-size: 1.25rem;
        }

        .room-header {
            padding: 0.875rem 1rem;
        }

        .room-header h3 {
            font-size: 1rem;
        }

        .teacher-link {
            padding: 0.75rem;
            font-size: 0.95rem;
        }
    }
</style>
