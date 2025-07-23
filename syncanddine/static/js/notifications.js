// Notification System with Push Notifications
document.addEventListener('DOMContentLoaded', function() {
    if (typeof currentUserId !== 'undefined') {
        requestNotificationPermission();
        checkNotifications();
        setInterval(checkNotifications, 30000); // Check every 30 seconds
    }
});

function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
}

function showPushNotification(title, body) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, {
            body: body,
            icon: '/static/favicon.ico',
            badge: '/static/favicon.ico'
        });
    }
}

let lastNotificationCount = 0;

function checkNotifications() {
    fetch('/api/notifications')
        .then(response => response.json())
        .then(data => {
            const badge = document.getElementById('notificationBadge');
            const list = document.getElementById('notificationList');
            
            if (data.notifications && data.notifications.length > 0) {
                // Show push notification for new notifications
                if (data.notifications.length > lastNotificationCount && lastNotificationCount > 0) {
                    const newNotifications = data.notifications.slice(0, data.notifications.length - lastNotificationCount);
                    newNotifications.forEach(notification => {
                        showPushNotification(
                            'SyncAndDine',
                            `${notification.sender_name}: ${notification.content}`
                        );
                    });
                }
                lastNotificationCount = data.notifications.length;
                
                badge.textContent = data.notifications.length;
                badge.style.display = 'block';
                
                list.innerHTML = '<li><h6 class="dropdown-header">Notifications</h6></li>';
                data.notifications.forEach(notification => {
                    const item = document.createElement('li');
                    item.innerHTML = `
                        <div class="dropdown-item">
                            <small class="text-muted">${notification.sender_name}</small><br>
                            ${notification.content}
                            <br><small class="text-muted">${notification.time_ago}</small>
                        </div>
                    `;
                    list.appendChild(item);
                });
                
                // Add mark all as read option
                const markRead = document.createElement('li');
                markRead.innerHTML = '<hr class="dropdown-divider"><li><a class="dropdown-item text-center" href="#" onclick="markAllRead()">Mark all as read</a></li>';
                list.appendChild(markRead);
            } else {
                lastNotificationCount = 0;
                badge.style.display = 'none';
                list.innerHTML = '<li><h6 class="dropdown-header">Notifications</h6></li><li><div class="dropdown-item text-muted">No new notifications</div></li>';
            }
        })
        .catch(error => console.error('Error fetching notifications:', error));
}

function markAllRead() {
    fetch('/api/notifications/mark-read', { method: 'POST' })
        .then(() => {
            lastNotificationCount = 0;
            checkNotifications();
        })
        .catch(error => console.error('Error marking notifications as read:', error));
}