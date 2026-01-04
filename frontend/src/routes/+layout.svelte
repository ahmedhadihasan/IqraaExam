<script>
    import '../app.css';
    import { appState } from '$lib/stores.js';
</script>

<!-- Notification Toast -->
{#if $appState.notification}
    <div class="toast toast-{$appState.notification.type}">
        {$appState.notification.message}
    </div>
{/if}

<slot />

<style>
    .toast {
        position: fixed;
        top: 1rem;
        right: 1rem;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    }

    .toast-success {
        background: #10b981;
        color: white;
    }

    .toast-error {
        background: #ef4444;
        color: white;
    }

    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
</style>
