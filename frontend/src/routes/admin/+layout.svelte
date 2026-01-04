<script>
    import { page } from '$app/stores';
    
    $: currentPath = $page.url.pathname;
    
    let sidebarOpen = false;
    
    const navItems = [
        { path: '/admin', label: 'داشبۆرد', icon: '📊' },
        { path: '/admin/students', label: 'قوتابیان', icon: '👨‍🎓' },
        { path: '/admin/assign', label: 'دابەشکردنی قوتابیان', icon: '📋' },
        { path: '/admin/q10', label: 'نمرەدانی پ١٠', icon: '✏️' },
        { path: '/admin/results', label: 'ئەنجامەکان', icon: '📈' },
        { path: '/admin/teachers', label: 'مامۆستاکان', icon: '👨‍🏫' },
        { path: '/admin/groups', label: 'گرووپی پرسیارەکان', icon: '❓' },
        { path: '/admin/sessions', label: 'دانیشتنەکان', icon: '📅' },
    ];

    function toggleSidebar() {
        sidebarOpen = !sidebarOpen;
    }

    function closeSidebar() {
        sidebarOpen = false;
    }
</script>

<div class="admin-layout">
    <!-- Mobile Header -->
    <header class="mobile-header">
        <button class="menu-btn" on:click={toggleSidebar}>
            ☰
        </button>
        <a href="/" class="mobile-logo">
            <img src="/logo.jpg" alt="ئیقرا" />
            ئیقرا
        </a>
        <span class="role-badge-mobile">بەڕێوەبەری گشتی</span>
    </header>

    <!-- Sidebar Overlay -->
    {#if sidebarOpen}
        <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
        <div class="sidebar-overlay" on:click={closeSidebar}></div>
    {/if}

    <aside class="sidebar" class:open={sidebarOpen}>
        <div class="sidebar-header">
            <a href="/" class="logo">
                <img src="/logo.jpg" alt="ئیقرا" class="sidebar-logo" />
                ئیقرا
            </a>
            <span class="role-badge">بەڕێوەبەری گشتی</span>
        </div>
        
        <nav class="sidebar-nav">
            {#each navItems as item}
                <a 
                    href={item.path} 
                    class="nav-item"
                    class:active={currentPath === item.path}
                    on:click={closeSidebar}
                >
                    <span class="nav-icon">{item.icon}</span>
                    {item.label}
                </a>
            {/each}
        </nav>
        
        <div class="sidebar-footer">
            <a href="/" class="nav-item" on:click={closeSidebar}>
                <span class="nav-icon">🏠</span>
                گەڕانەوە بۆ سەرەتا
            </a>
        </div>
    </aside>
    
    <main class="main-content">
        <slot />
    </main>
</div>

<style>
    .admin-layout {
        display: flex;
        min-height: 100vh;
    }

    .mobile-header {
        display: none;
    }

    .sidebar-overlay {
        display: none;
    }

    .sidebar {
        width: 260px;
        background: var(--surface);
        border-left: 1px solid var(--border);
        display: flex;
        flex-direction: column;
        position: fixed;
        top: 0;
        right: 0;
        bottom: 0;
        z-index: 100;
    }

    .sidebar-header {
        padding: 1.5rem;
        border-bottom: 1px solid var(--border);
    }

    .logo {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--text);
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.5rem;
    }

    .sidebar-logo {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
    }

    .role-badge {
        font-size: 0.75rem;
        color: var(--primary);
        background: rgba(37, 99, 235, 0.1);
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
    }

    .sidebar-nav {
        flex: 1;
        padding: 1rem 0.75rem;
        overflow-y: auto;
    }

    .nav-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 1rem;
        color: var(--text);
        text-decoration: none;
        border-radius: 6px;
        margin-bottom: 0.25rem;
        transition: background 0.15s;
    }

    .nav-item:hover {
        background: var(--background);
        text-decoration: none;
    }

    .nav-item.active {
        background: var(--primary);
        color: white;
    }

    .nav-icon {
        font-size: 1.125rem;
    }

    .sidebar-footer {
        padding: 1rem 0.75rem;
        border-top: 1px solid var(--border);
    }

    .main-content {
        flex: 1;
        margin-right: 260px;
        padding: 2rem;
    }

    /* Tablet Styles */
    @media (max-width: 992px) {
        .sidebar {
            width: 220px;
        }

        .main-content {
            margin-right: 220px;
            padding: 1.5rem;
        }
    }

    /* Mobile Styles */
    @media (max-width: 768px) {
        .admin-layout {
            flex-direction: column;
        }

        .mobile-header {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem;
            background: var(--surface);
            border-bottom: 1px solid var(--border);
            position: sticky;
            top: 0;
            z-index: 50;
        }

        .menu-btn {
            background: var(--bg-dark);
            border: 1px solid var(--border);
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
            font-size: 1.25rem;
            cursor: pointer;
            color: var(--text);
        }

        .mobile-logo {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: 700;
            color: var(--text);
            text-decoration: none;
        }

        .mobile-logo img {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            object-fit: cover;
        }

        .role-badge-mobile {
            margin-right: auto;
            font-size: 0.7rem;
            color: var(--primary);
            background: rgba(37, 99, 235, 0.1);
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
        }

        .sidebar-overlay {
            display: block;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 90;
        }

        .sidebar {
            transform: translateX(100%);
            transition: transform 0.3s ease;
            width: 280px;
        }

        .sidebar.open {
            transform: translateX(0);
        }

        .main-content {
            margin-right: 0;
            padding: 1rem;
        }

        .sidebar-nav {
            flex-direction: column;
        }
    }
</style>
