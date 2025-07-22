document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Remove old dark mode toggle - now handled by theme-toggle.js
    // Force navbar color fix
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    // Force navbar background color
    const navbar = document.getElementById('mainNavbar');
    if (navbar) {
        if (currentTheme === 'dark') {
            navbar.style.backgroundColor = '#1c1c1e';
        } else {
            navbar.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
        }
    }
    
    // Location autocomplete
    const locationInput = document.getElementById('location');
    if (locationInput) {
        locationInput.addEventListener('input', function() {
            const query = this.value;
            if (query.length >= 2) {
                fetch(`/api/locations?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        showAutocomplete(this, data);
                    });
            }
        });
    }
    
    // Cuisine autocomplete
    const cuisineInput = document.getElementById('cuisine');
    if (cuisineInput) {
        cuisineInput.addEventListener('input', function() {
            const query = this.value;
            if (query.length >= 2) {
                fetch(`/api/cuisines?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        showAutocomplete(this, data);
                    });
            }
        });
    }
    
    // Helper function to show autocomplete suggestions
    function showAutocomplete(input, suggestions) {
        // Remove any existing autocomplete container
        const existingContainer = document.querySelector('.autocomplete-container');
        if (existingContainer) {
            existingContainer.remove();
        }
        
        if (suggestions.length === 0) return;
        
        // Create autocomplete container
        const container = document.createElement('div');
        container.className = 'autocomplete-container';
        container.style.position = 'absolute';
        container.style.zIndex = '1000';
        container.style.backgroundColor = '#fff';
        container.style.width = Math.min(input.offsetWidth, window.innerWidth - 30) + 'px';
        container.style.border = '1px solid #ddd';
        container.style.maxHeight = '200px';
        container.style.overflowY = 'auto';
        
        // Position the container
        const rect = input.getBoundingClientRect();
        container.style.top = (rect.bottom + window.scrollY) + 'px';
        container.style.left = (rect.left + window.scrollX) + 'px';
        
        // Add suggestions
        suggestions.forEach(suggestion => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            item.style.padding = '8px 12px';
            item.style.cursor = 'pointer';
            item.style.borderBottom = '1px solid #eee';
            item.textContent = suggestion;
            
            item.addEventListener('mouseenter', function() {
                this.style.backgroundColor = '#f0f0f0';
            });
            
            item.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '#fff';
            });
            
            item.addEventListener('click', function() {
                input.value = suggestion;
                container.remove();
            });
            
            container.appendChild(item);
        });
        
        // Add container to document
        document.body.appendChild(container);
        
        // Remove container when clicking outside
        document.addEventListener('click', function(e) {
            if (e.target !== input && !container.contains(e.target)) {
                container.remove();
            }
        });
    }
});