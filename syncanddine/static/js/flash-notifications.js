/**
 * Flash Notifications with User Visibility Detection
 */
document.addEventListener('DOMContentLoaded', function() {
    const flashNotifications = document.querySelectorAll('.flash-notification');
    
    if (flashNotifications.length === 0) return;
    
    // Check if user is actively viewing the page
    function isUserActive() {
        return !document.hidden && document.hasFocus();
    }
    
    // Show notification with animation
    function showNotification(notification) {
        notification.style.animation = 'slideInFlash 0.5s ease-out forwards';
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            if (isUserActive()) {
                notification.style.animation = 'slideOutFlash 0.5s ease-in forwards';
                setTimeout(() => {
                    notification.remove();
                }, 500);
            }
        }, 10000);
    }
    
    // Show notifications only when user is active
    function initNotifications() {
        if (isUserActive()) {
            flashNotifications.forEach((notification, index) => {
                setTimeout(() => {
                    showNotification(notification);
                }, index * 200); // Stagger multiple notifications
            });
        } else {
            // Wait for user to become active
            const checkActivity = () => {
                if (isUserActive()) {
                    initNotifications();
                    document.removeEventListener('visibilitychange', checkActivity);
                    window.removeEventListener('focus', checkActivity);
                }
            };
            
            document.addEventListener('visibilitychange', checkActivity);
            window.addEventListener('focus', checkActivity);
        }
    }
    
    // Initialize notifications
    initNotifications();
});