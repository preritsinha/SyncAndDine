/**
 * Apple-style Dark Mode Toggle
 * Provides smooth theme switching with system preference detection
 */
class ThemeManager {
    constructor() {
        this.init();
    }

    /**
     * Initialize theme manager
     * Sets up event listeners and applies saved theme
     */
    init() {
        // Get saved theme or default to system preference
        const savedTheme = localStorage.getItem('theme');
        const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        const currentTheme = savedTheme || systemTheme;
        
        this.applyTheme(currentTheme);
        this.setupToggleButton();
        this.watchSystemTheme();
    }

    /**
     * Apply theme to document
     * @param {string} theme - 'light' or 'dark'
     */
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        this.updateToggleButton(theme);
    }

    /**
     * Toggle between light and dark themes
     */
    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme(newTheme);
    }

    /**
     * Setup theme toggle button
     */
    setupToggleButton() {
        const toggleButton = document.getElementById('themeToggle');
        if (toggleButton) {
            toggleButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleTheme();
            });
        }
    }

    /**
     * Update toggle button appearance
     * @param {string} theme - Current theme
     */
    updateToggleButton(theme) {
        const toggleButton = document.getElementById('themeToggle');
        if (toggleButton) {
            const icon = theme === 'dark' ? 'fa-sun' : 'fa-moon';
            const text = theme === 'dark' ? 'Light Mode' : 'Dark Mode';
            toggleButton.innerHTML = `${text} <i class="fas ${icon} ms-2"></i>`;
        }
    }

    /**
     * Watch for system theme changes
     */
    watchSystemTheme() {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                this.applyTheme(e.matches ? 'dark' : 'light');
            }
        });
    }
}

// Initialize theme manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ThemeManager();
});