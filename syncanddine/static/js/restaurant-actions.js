// Restaurant Actions - Like/Dislike with card removal
document.addEventListener('DOMContentLoaded', function() {
    // Handle like button clicks
    document.querySelectorAll('.like-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const button = this.querySelector('.like-btn');
            const card = this.closest('.restaurant-card').parentElement;
            
            // Show loading state
            button.disabled = true;
            button.innerHTML = '⏳';
            
            // Submit form via AJAX
            fetch(this.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (response.redirected) {
                    throw new Error('Redirect response');
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    // Animate card removal
                    card.style.transition = 'all 0.3s ease';
                    card.style.transform = 'scale(0.8)';
                    card.style.opacity = '0';
                    
                    setTimeout(() => {
                        card.remove();
                    }, 300);
                } else {
                    // Reset button on error
                    button.disabled = false;
                    button.innerHTML = '♥';
                    alert('Error liking restaurant');
                }
            })
            .catch(error => {
                // Reset button on error
                button.disabled = false;
                button.innerHTML = '♥';
                alert('Error liking restaurant');
            });
        });
    });
});