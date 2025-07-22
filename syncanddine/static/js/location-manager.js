/**
 * Location Manager - Persistent Location Storage
 * Stores user location once permission is granted and reuses it
 */
class LocationManager {
    constructor() {
        this.storageKey = 'userLocation';
        this.init();
    }

    /**
     * Initialize location manager
     */
    init() {
        this.loadSavedLocation();
        this.autoGetLocation();
        this.setupLocationButton();
    }

    /**
     * Load saved location from localStorage
     */
    loadSavedLocation() {
        const saved = localStorage.getItem(this.storageKey);
        if (saved) {
            const location = JSON.parse(saved);
            this.applyLocationToPage(location.lat, location.lon);
            return true;
        }
        return false;
    }

    /**
     * Automatically get location if not saved
     */
    async autoGetLocation() {
        if (!this.loadSavedLocation() && window.location.pathname.includes('/restaurants')) {
            try {
                const location = await this.getCurrentLocation();
                this.applyLocationToPage(location.lat, location.lon);
                
                // Reload page with location if no restaurants shown
                if (document.querySelectorAll('.restaurant-card').length === 0) {
                    const url = new URL(window.location);
                    url.searchParams.set('lat', location.lat);
                    url.searchParams.set('lon', location.lon);
                    window.location.href = url.toString();
                }
            } catch (error) {
                console.log('Auto-location failed, user can manually enable');
            }
        }
    }

    /**
     * Save location to localStorage
     */
    saveLocation(lat, lon) {
        const location = { lat, lon, timestamp: Date.now() };
        localStorage.setItem(this.storageKey, JSON.stringify(location));
    }

    /**
     * Apply location to current page
     */
    applyLocationToPage(lat, lon) {
        // Update URL parameters if on restaurants page
        if (window.location.pathname.includes('/restaurants')) {
            const url = new URL(window.location);
            if (!url.searchParams.has('lat') && !url.searchParams.has('lon')) {
                url.searchParams.set('lat', lat);
                url.searchParams.set('lon', lon);
                window.history.replaceState({}, '', url.toString());
                
                // Reload page with location if no restaurants are shown
                if (document.querySelectorAll('.restaurant-card').length === 0) {
                    window.location.href = url.toString();
                }
            }
        }
        
        // Update form inputs if they exist and show location section
        const latInput = document.querySelector('input[name="lat"]');
        const lonInput = document.querySelector('input[name="lon"]');
        const locationInputs = document.getElementById('locationInputs');
        
        if (latInput && lonInput) {
            latInput.value = lat;
            lonInput.value = lon;
            if (locationInputs) {
                locationInputs.style.display = 'block';
            }
        }
    }

    /**
     * Get current location and save it
     */
    getCurrentLocation() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Geolocation not supported'));
                return;
            }

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    
                    this.saveLocation(lat, lon);
                    resolve({ lat, lon });
                },
                (error) => {
                    reject(error);
                }
            );
        });
    }

    /**
     * Setup location button functionality
     */
    setupLocationButton() {
        const locationBtn = document.getElementById('getLocationBtn');
        if (!locationBtn) return;

        // Check if we already have location
        const saved = localStorage.getItem(this.storageKey);
        if (saved) {
            locationBtn.innerHTML = '<i class="fas fa-check me-2"></i> Location Set';
            locationBtn.classList.remove('btn-success');
            locationBtn.classList.add('btn-outline-success');
            locationBtn.style.display = 'inline-block';
        } else {
            // Show button if auto-location failed
            setTimeout(() => {
                if (!localStorage.getItem(this.storageKey)) {
                    locationBtn.style.display = 'inline-block';
                    locationBtn.innerHTML = '<i class="fas fa-map-marker-alt me-2"></i> Enable Location';
                }
            }, 2000);
        }

        locationBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            
            locationBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Getting Location...';
            locationBtn.disabled = true;

            try {
                const location = await this.getCurrentLocation();
                
                // Update button
                locationBtn.innerHTML = '<i class="fas fa-check me-2"></i> Location Set';
                locationBtn.classList.remove('btn-success');
                locationBtn.classList.add('btn-outline-success');
                locationBtn.disabled = false;

                // Apply location to page
                this.applyLocationToPage(location.lat, location.lon);
                
                // Reload page with location
                const url = new URL(window.location);
                url.searchParams.set('lat', location.lat);
                url.searchParams.set('lon', location.lon);
                window.location.href = url.toString();

            } catch (error) {
                console.error('Location error:', error);
                locationBtn.innerHTML = '<i class="fas fa-map-marker-alt me-2"></i> Use My Location';
                locationBtn.disabled = false;
                
                if (error.code === 1) {
                    alert('Location access denied. Please enable location services and try again.');
                } else {
                    alert('Unable to get location. Please try again.');
                }
            }
        });
    }

    /**
     * Clear saved location
     */
    clearLocation() {
        localStorage.removeItem(this.storageKey);
        const locationBtn = document.getElementById('getLocationBtn');
        if (locationBtn) {
            locationBtn.innerHTML = '<i class="fas fa-map-marker-alt me-2"></i> Use My Location';
            locationBtn.classList.remove('btn-outline-success');
            locationBtn.classList.add('btn-success');
        }
    }
}

// Initialize location manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.locationManager = new LocationManager();
});