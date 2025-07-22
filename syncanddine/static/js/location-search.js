/**
 * Dynamic Location Search - Cities and Areas
 */
class LocationSearch {
    constructor() {
        this.cities = [];
        this.areas = {};
        this.init();
    }

    init() {
        this.populateCities();
        this.setupEventListeners();
        this.makeSelectsSearchable();
    }

    async populateCities() {
        const citySelect = document.getElementById('city');
        if (!citySelect) return;

        try {
            const response = await fetch('/api/cities');
            this.cities = await response.json();
            
            citySelect.innerHTML = '<option value="">Current Location</option>';
            
            this.cities.forEach(city => {
                const option = document.createElement('option');
                option.value = city;
                option.textContent = city;
                citySelect.appendChild(option);
            });

            // Set selected city if exists in URL
            const urlParams = new URLSearchParams(window.location.search);
            const selectedCity = urlParams.get('city');
            if (selectedCity) {
                citySelect.value = selectedCity;
                await this.populateAreas(selectedCity);
            }
        } catch (error) {
            console.error('Error loading cities:', error);
        }
    }

    async populateAreas(city) {
        const areaSelect = document.getElementById('area');
        if (!areaSelect || !city) return;

        areaSelect.innerHTML = '<option value="">Loading areas...</option>';
        areaSelect.disabled = true;

        try {
            const response = await fetch(`/api/areas?city=${encodeURIComponent(city)}`);
            const areas = await response.json();
            
            areaSelect.innerHTML = '<option value="">All Areas</option>';
            areaSelect.disabled = false;

            areas.forEach(area => {
                const option = document.createElement('option');
                option.value = area;
                option.textContent = area;
                areaSelect.appendChild(option);
            });

            // Set selected area if exists in URL
            const urlParams = new URLSearchParams(window.location.search);
            const selectedArea = urlParams.get('area');
            if (selectedArea) {
                areaSelect.value = selectedArea;
            }
        } catch (error) {
            console.error('Error loading areas:', error);
            areaSelect.innerHTML = '<option value="">Error loading areas</option>';
        }
    }

    setupEventListeners() {
        const citySelect = document.getElementById('city');
        const areaSelect = document.getElementById('area');

        if (citySelect) {
            citySelect.addEventListener('change', async (e) => {
                const selectedCity = e.target.value;
                if (selectedCity) {
                    await this.populateAreas(selectedCity);
                } else {
                    areaSelect.innerHTML = '<option value="">Select city first</option>';
                    areaSelect.disabled = true;
                }
            });
        }
    }

    makeSelectsSearchable() {
        // Simple search functionality for select elements
        document.querySelectorAll('.searchable-select').forEach(select => {
            select.addEventListener('focus', () => {
                select.setAttribute('data-live-search', 'true');
            });
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new LocationSearch();
});