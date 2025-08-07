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
            const card = form.closest('.restaurant-card').parentElement;
            
            // Show loading state
            button.disabled = true;
            button.innerHTML = 'Loading...';
            
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
                    if (data.action === 'liked') {
                        // Update button to "Liked" state
                        button.innerHTML = 'Liked';
                        
                        // Fade out the entire card
                        setTimeout(() => {
                            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                            card.style.opacity = '0';
                            card.style.transform = 'scale(0.9)';
                            
                            setTimeout(() => {
                                card.remove();
                            }, 500);
                        }, 800); // Wait 800ms to show "Liked" state
                        
                    } else if (data.action === 'disliked') {
                        // If user unlikes, revert to "Like" state
                        button.className = 'btn btn-sm w-100 btn-outline-primary';
                        button.innerHTML = '<i class="fas fa-heart me-1"></i>Like';
                    }
                } else {
                    alert('Error processing request');
                }
            })
            .catch(error => {
                alert('Error processing request');
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