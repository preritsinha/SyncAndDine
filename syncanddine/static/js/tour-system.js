/**
 * SyncAndDine Feature Tour
 * Slide-based tour with GIF animations
 */

class FeatureTour {
    constructor() {
        this.isActive = false;
        this.modal = null;
        this.currentSlide = 0;
        this.slides = [
            {
                title: 'Browse Restaurants',
                icon: '🔍',
                gif: 'https://picsum.photos/400/250?random=1',
                description: 'Discover amazing restaurants near you with live Google Places data. Use powerful filters to find exactly what you\'re craving - by location, cuisine, rating, and price range.'
            },
            {
                title: 'Create Groups',
                icon: '👥',
                gif: 'https://picsum.photos/400/250?random=2',
                description: 'Invite friends to dining groups and make decisions together. Share group codes via WhatsApp or copy links to bring everyone into the conversation.'
            },
            {
                title: 'Like & Dislike',
                icon: '❤️',
                gif: 'https://picsum.photos/400/250?random=3',
                description: 'Express your preferences by liking or disliking restaurants. Your choices help create the perfect match for your group with our smart scoring system.'
            },
            {
                title: 'Group Leaderboard',
                icon: '🏆',
                gif: 'https://picsum.photos/400/250?random=4',
                description: 'See real-time rankings based on everyone\'s preferences. Our weighted scoring system (Like = 1.0, Dislike = 0.7) shows the most popular choices at the top.'
            },
            {
                title: 'WhatsApp Integration',
                icon: '💬',
                gif: 'https://picsum.photos/400/250?random=5',
                description: 'Connect your WhatsApp groups to get final restaurant results delivered automatically. Set time limits and receive formatted results when the deadline is reached.'
            },
            {
                title: 'Smart Matching',
                icon: '✨',
                gif: 'https://picsum.photos/400/250?random=6',
                description: 'Our algorithm finds restaurants everyone will love. Get perfect matches when all members agree, or see top recommendations based on group preferences.'
            }
        ];
    }

    showTour() {
        if (this.isActive) return;
        
        this.isActive = true;
        this.currentSlide = 0;
        this.createModal();
        this.showSlide();
        
        // Mark as seen
        localStorage.setItem('syncanddine_tour_seen', 'true');
    }

    createModal() {
        this.modal = document.createElement('div');
        this.modal.className = 'feature-tour-overlay';
        this.modal.innerHTML = `
            <div class="feature-tour-modal">
                <div class="feature-tour-header">
                    <h3>🍽️ Welcome to SyncAndDine!</h3>
                    <button class="feature-tour-close">&times;</button>
                </div>
                <div class="feature-tour-content">
                    <div class="slide-container">
                        <div class="slide-gif">
                            <img src="" alt="Feature demonstration" class="feature-gif">
                        </div>
                        <div class="slide-info">
                            <div class="slide-icon"></div>
                            <h4 class="slide-title"></h4>
                            <p class="slide-description"></p>
                        </div>
                    </div>
                </div>
                <div class="feature-tour-footer">
                    <div class="slide-indicators"></div>
                    <div class="slide-controls">
                        <button class="tour-btn tour-prev">Previous</button>
                        <button class="tour-btn tour-skip">Skip Tour</button>
                        <button class="tour-btn tour-next">Next</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(this.modal);
        
        // Event listeners
        this.modal.querySelector('.feature-tour-close').onclick = () => this.closeTour();
        this.modal.querySelector('.tour-skip').onclick = () => this.closeTour();
        this.modal.querySelector('.tour-prev').onclick = () => this.prevSlide();
        this.modal.querySelector('.tour-next').onclick = () => this.nextSlide();
        
        // ESC key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isActive) this.closeTour();
        });
        
        // Create indicators
        this.createIndicators();
    }

    createIndicators() {
        const container = this.modal.querySelector('.slide-indicators');
        container.innerHTML = '';
        
        this.slides.forEach((_, index) => {
            const indicator = document.createElement('div');
            indicator.className = 'slide-indicator';
            indicator.onclick = () => this.goToSlide(index);
            container.appendChild(indicator);
        });
    }

    showSlide() {
        const slide = this.slides[this.currentSlide];
        if (!slide) return;
        
        // Update content
        this.modal.querySelector('.feature-gif').src = slide.gif;
        this.modal.querySelector('.slide-icon').textContent = slide.icon;
        this.modal.querySelector('.slide-title').textContent = slide.title;
        this.modal.querySelector('.slide-description').textContent = slide.description;
        
        // Update indicators
        this.modal.querySelectorAll('.slide-indicator').forEach((indicator, index) => {
            indicator.classList.toggle('active', index === this.currentSlide);
        });
        
        // Update buttons
        this.modal.querySelector('.tour-prev').style.display = 
            this.currentSlide === 0 ? 'none' : 'inline-block';
        this.modal.querySelector('.tour-next').textContent = 
            this.currentSlide === this.slides.length - 1 ? 'Get Started' : 'Next';
    }

    nextSlide() {
        if (this.currentSlide < this.slides.length - 1) {
            this.currentSlide++;
            this.showSlide();
        } else {
            this.closeTour();
        }
    }

    prevSlide() {
        if (this.currentSlide > 0) {
            this.currentSlide--;
            this.showSlide();
        }
    }

    goToSlide(index) {
        this.currentSlide = index;
        this.showSlide();
    }

    closeTour() {
        if (this.modal) {
            this.modal.remove();
        }
        this.isActive = false;
    }

    shouldShowTour() {
        return !localStorage.getItem('syncanddine_tour_seen');
    }
}

// Global feature tour instance
window.featureTour = new FeatureTour();

// Auto-show tour for new users
document.addEventListener('DOMContentLoaded', function() {
    // Auto-show for new users (with delay to let page load)
    if (window.featureTour.shouldShowTour()) {
        setTimeout(() => {
            window.featureTour.showTour();
        }, 1000);
    }
});