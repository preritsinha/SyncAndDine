/**
 * Handle restaurant liking without page refresh
 */
document.addEventListener('DOMContentLoaded', function() {
    // Handle like button clicks
    document.addEventListener('submit', function(e) {
        if (e.target.classList.contains('like-form')) {
            e.preventDefault();
            
            const form = e.target;
            const button = form.querySelector('button');
            const originalText = button.textContent;
            
            // Show loading state
            button.disabled = true;
            button.textContent = '...';
            
            // Send AJAX request
            fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Check if restaurant was liked or disliked
                    if (data.action === 'liked') {
                        button.classList.add('liked');
                        button.textContent = 'Liked';
                    } else {
                        button.classList.remove('liked');
                        button.textContent = 'Like';
                    }
                } else {
                    button.textContent = originalText;
                }
            })
            .catch(error => {
                button.textContent = originalText;
            })
            .finally(() => {
                button.disabled = false;
            });
        }
    });
    
    // Handle remove button clicks in personal summary
    document.addEventListener('submit', function(e) {
        if (e.target.action && e.target.action.includes('remove-selection')) {
            e.preventDefault();
            
            const form = e.target;
            const card = form.closest('.restaurant-card').parentElement;
            
            fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (response.ok) {
                    // Fade out and remove card
                    card.style.transition = 'opacity 0.3s ease';
                    card.style.opacity = '0';
                    setTimeout(() => {
                        card.remove();
                        
                        // Update count if exists
                        const countElement = document.querySelector('strong');
                        if (countElement) {
                            const currentCount = parseInt(countElement.textContent);
                            countElement.textContent = currentCount - 1;
                        }
                        
                        // Check if no restaurants left
                        const remainingCards = document.querySelectorAll('.restaurant-card');
                        if (remainingCards.length === 0) {
                            location.reload(); // Reload to show "no restaurants" message
                        }
                    }, 300);
                }
            })
            .catch(error => {
                console.error('Error removing restaurant:', error);
            });
        }
    });
});