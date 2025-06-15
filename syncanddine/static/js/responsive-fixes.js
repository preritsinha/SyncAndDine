document.addEventListener('DOMContentLoaded', function() {
    // Fix for mobile viewport height issues (100vh problem)
    function setMobileHeight() {
        let vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }
    
    // Run on page load
    setMobileHeight();
    
    // Run on resize
    window.addEventListener('resize', setMobileHeight);
    
    // Fix for restaurant cards on mobile
    function equalizeCardHeights() {
        if (window.innerWidth >= 768) {
            const cards = document.querySelectorAll('.restaurant-card');
            let maxHeight = 0;
            
            // Reset heights
            cards.forEach(card => {
                card.style.height = 'auto';
            });
            
            // Find max height
            cards.forEach(card => {
                if (card.offsetHeight > maxHeight) {
                    maxHeight = card.offsetHeight;
                }
            });
            
            // Set all to max height
            if (maxHeight > 0) {
                cards.forEach(card => {
                    card.style.height = maxHeight + 'px';
                });
            }
        }
    }
    
    // Run after images load
    window.addEventListener('load', equalizeCardHeights);
    window.addEventListener('resize', equalizeCardHeights);
    
    // Fix for mobile autocomplete positioning
    const resizeAutocomplete = function() {
        const container = document.querySelector('.autocomplete-container');
        if (container) {
            const input = document.querySelector('#location') || document.querySelector('#cuisine');
            if (input) {
                container.style.width = Math.min(input.offsetWidth, window.innerWidth - 30) + 'px';
            }
        }
    };
    
    window.addEventListener('resize', resizeAutocomplete);
});