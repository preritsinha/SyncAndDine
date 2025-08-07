/**
 * SyncAndDine Feature Tour
 * Updated for current app flow
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
                gif: 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400&h=250&fit=crop&auto=format',
                description: 'Discover amazing restaurants with live Google Places data. Filter by location, cuisine, rating, and price to find exactly what you want.'
            },
            {
                title: 'Create Dining Groups',
                icon: '👥',
                gif: 'https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=400&h=250&fit=crop&auto=format',
                description: 'Create groups with friends and set time limits. Share group codes to invite others and make dining decisions together.'
            },
            {
                title: 'Like & Match Restaurants',
                icon: '❤️',
                gif: 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=250&fit=crop&auto=format',
                description: 'Like or dislike restaurants in your group. Our system finds matches based on everyone\'s preferences.'
            },
            {
                title: 'Get Email Results',
                icon: '📧',
                gif: 'https://images.unsplash.com/photo-1551218808-94e220e084d2?w=400&h=250&fit=crop&auto=format',
                description: 'When the timer expires, get detailed results sent to your email with the best restaurant matches for your group.'
            }
        ];
    }

    showTour() {
        if (this.isActive) return;
        
        this.isActive = true;
        this.currentSlide = 0;
        this.createModal();
        this.showSlide();
        
        localStorage.setItem('syncanddine_tour_seen', 'true');
    }

    createModal() {
        this.modal = document.createElement('div');
        this.modal.className = 'feature-tour-overlay';
        this.modal.innerHTML = `
            <div class="feature-tour-modal">
                <div class="feature-tour-header">
                    <h3>Welcome to SyncAndDine</h3>
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
        
        this.modal.querySelector('.feature-tour-close').onclick = () => this.closeTour();
        this.modal.querySelector('.tour-skip').onclick = () => this.closeTour();
        this.modal.querySelector('.tour-prev').onclick = () => this.prevSlide();
        this.modal.querySelector('.tour-next').onclick = () => this.nextSlide();
        
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isActive) this.closeTour();
        });
        
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
        
        this.modal.querySelector('.feature-gif').src = slide.gif;
        this.modal.querySelector('.slide-icon').textContent = slide.icon;
        this.modal.querySelector('.slide-title').textContent = slide.title;
        this.modal.querySelector('.slide-description').textContent = slide.description;
        
        this.modal.querySelectorAll('.slide-indicator').forEach((indicator, index) => {
            indicator.classList.toggle('active', index === this.currentSlide);
        });
        
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

window.featureTour = new FeatureTour();

function showAppTour() {
    window.featureTour.showTour();
}

document.addEventListener('DOMContentLoaded', function() {
    if (window.featureTour.shouldShowTour()) {
        setTimeout(() => {
            window.featureTour.showTour();
        }, 1000);
    }
});