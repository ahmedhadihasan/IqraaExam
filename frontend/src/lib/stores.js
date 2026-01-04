import { writable } from 'svelte/store';

// Current teacher (for teacher view)
export const currentTeacher = writable(null);

// Current exam session
export const currentSession = writable(null);

// App state
export const appState = writable({
    loading: false,
    error: null,
    notification: null
});

// Helper to show notifications
export function showNotification(message, type = 'success') {
    appState.update(state => ({
        ...state,
        notification: { message, type }
    }));
    
    // Auto-clear after 3 seconds
    setTimeout(() => {
        appState.update(state => ({
            ...state,
            notification: null
        }));
    }, 3000);
}

// Helper to show errors
export function showError(message) {
    showNotification(message, 'error');
}
