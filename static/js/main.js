// PlayBharat Main JavaScript

// Global PlayBharat object
window.PlayBharat = {
    // Configuration
    config: {
        searchDelay: 300,
        apiEndpoint: '/api/',
        csrfToken: null
    },
    
    // Utility functions
    utils: {
        // Get CSRF token
        getCsrfToken: function() {
            const token = document.querySelector('[name=csrfmiddlewaretoken]');
            return token ? token.value : null;
        },
        
        // Format numbers (1000 -> 1K, 1000000 -> 1M)
        formatNumber: function(num) {
            if (num >= 1000000) {
                return (num / 1000000).toFixed(1) + 'M';
            } else if (num >= 1000) {
                return (num / 1000).toFixed(1) + 'K';
            }
            return num.toString();
        },
        
        // Format duration (seconds to MM:SS or HH:MM:SS)
        formatDuration: function(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = Math.floor(seconds % 60);
            
            if (hours > 0) {
                return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
            } else {
                return `${minutes}:${secs.toString().padStart(2, '0')}`;
            }
        },
        
        // Format time ago (2025-01-01 -> "2 days ago")
        formatTimeAgo: function(dateString) {
            const date = new Date(dateString);
            const now = new Date();
            const diffInSeconds = Math.floor((now - date) / 1000);
            
            const intervals = {
                year: 31536000,
                month: 2592000,
                day: 86400,
                hour: 3600,
                minute: 60
            };
            
            for (const [unit, seconds] of Object.entries(intervals)) {
                const interval = Math.floor(diffInSeconds / seconds);
                if (interval >= 1) {
                    return `${interval} ${unit}${interval > 1 ? 's' : ''} ago`;
                }
            }
            
            return 'Just now';
        },
        
        // Show toast notification
        showToast: function(message, type = 'info', duration = 5000) {
            const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
            const toastId = 'toast-' + Date.now();
            
            const toast = document.createElement('div');
            toast.id = toastId;
            toast.className = `alert alert-${type} alert-dismissible fade show mb-2`;
            toast.setAttribute('role', 'alert');
            toast.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            toastContainer.appendChild(toast);
            
            // Auto-dismiss after duration
            setTimeout(() => {
                if (document.getElementById(toastId)) {
                    toast.classList.remove('show');
                    setTimeout(() => toast.remove(), 150);
                }
            }, duration);
        },
        
        // Create toast container if it doesn't exist
        createToastContainer: function() {
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
            return container;
        },
        
        // Loading states
        showLoading: function(element) {
            element.innerHTML = '<div class="loading-spinner"></div>';
        },
        
        hideLoading: function(element) {
            element.innerHTML = '';
        }
    },
    
    // Search functionality
    search: {
        currentQuery: '',
        suggestions: [],
        
        init: function() {
            const searchInput = document.getElementById('search-input');
            if (searchInput) {
                this.setupSearchInput(searchInput);
            }
        },
        
        setupSearchInput: function(input) {
            let timeout;
            
            input.addEventListener('input', (e) => {
                clearTimeout(timeout);
                const query = e.target.value.trim();
                
                if (query.length >= 2) {
                    timeout = setTimeout(() => {
                        this.getSuggestions(query);
                    }, PlayBharat.config.searchDelay);
                } else {
                    this.hideSuggestions();
                }
            });
            
            // Hide suggestions when clicking outside
            document.addEventListener('click', (e) => {
                if (!input.contains(e.target)) {
                    this.hideSuggestions();
                }
            });
            
            // Handle search form submission
            const form = input.closest('form');
            if (form) {
                form.addEventListener('submit', (e) => {
                    e.preventDefault();
                    this.performSearch(input.value.trim());
                });
            }
        },
        
        getSuggestions: function(query) {
            // This would typically make an HTMX request
            // For now, we'll simulate it
            console.log('Getting suggestions for:', query);
        },
        
        hideSuggestions: function() {
            const suggestionsContainer = document.getElementById('search-suggestions');
            if (suggestionsContainer) {
                suggestionsContainer.innerHTML = '';
                suggestionsContainer.style.display = 'none';
            }
        },
        
        performSearch: function(query) {
            if (query) {
                window.location.href = `/search/?q=${encodeURIComponent(query)}`;
            }
        }
    },
    
    // Video functionality
    video: {
        currentPlayer: null,
        
        init: function() {
            this.setupVideoCards();
            this.setupVideoPlayer();
        },
        
        setupVideoCards: function() {
            const videoCards = document.querySelectorAll('.video-card');
            videoCards.forEach(card => {
                card.addEventListener('click', (e) => {
                    e.preventDefault();
                    const videoUrl = card.dataset.videoUrl;
                    if (videoUrl) {
                        window.location.href = videoUrl;
                    }
                });
            });
        },
        
        setupVideoPlayer: function() {
            const videoPlayers = document.querySelectorAll('.video-player');
            videoPlayers.forEach(player => {
                this.initializePlayer(player);
            });
        },
        
        initializePlayer: function(playerElement) {
            // Basic video player setup
            const video = playerElement.querySelector('video');
            if (video) {
                video.addEventListener('loadedmetadata', () => {
                    this.updateVideoInfo(video);
                });
                
                video.addEventListener('timeupdate', () => {
                    this.trackProgress(video);
                });
            }
        },
        
        updateVideoInfo: function(video) {
            const duration = PlayBharat.utils.formatDuration(video.duration);
            const durationDisplay = document.querySelector('.video-duration-display');
            if (durationDisplay) {
                durationDisplay.textContent = duration;
            }
        },
        
        trackProgress: function(video) {
            const progress = (video.currentTime / video.duration) * 100;
            
            // Update progress bar if exists
            const progressBar = document.querySelector('.video-progress');
            if (progressBar) {
                progressBar.style.width = `${progress}%`;
            }
            
            // Track view progress for analytics
            if (progress > 30 && !video.dataset.viewTracked) {
                this.trackView(video);
                video.dataset.viewTracked = 'true';
            }
        },
        
        trackView: function(video) {
            const videoId = video.dataset.videoId;
            if (videoId) {
                // Use HTMX to track the view
                htmx.ajax('POST', '/streaming/track/view/', {
                    values: { video_id: videoId },
                    headers: { 'X-CSRFToken': PlayBharat.utils.getCsrfToken() }
                });
            }
        }
    },
    
    // Interactions (likes, comments, etc.)
    interactions: {
        init: function() {
            this.setupLikeButtons();
            this.setupCommentForms();
            this.setupSubscribeButtons();
        },
        
        setupLikeButtons: function() {
            const likeButtons = document.querySelectorAll('.like-btn');
            likeButtons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.toggleLike(btn);
                });
            });
        },
        
        setupCommentForms: function() {
            const commentForms = document.querySelectorAll('.comment-form');
            commentForms.forEach(form => {
                form.addEventListener('submit', (e) => {
                    this.handleCommentSubmit(e, form);
                });
            });
        },
        
        setupSubscribeButtons: function() {
            const subscribeButtons = document.querySelectorAll('.subscribe-btn');
            subscribeButtons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.toggleSubscription(btn);
                });
            });
        },
        
        toggleLike: function(button) {
            const videoId = button.dataset.videoId;
            const isLiked = button.classList.contains('liked');
            
            // Optimistic UI update
            button.classList.toggle('liked');
            button.querySelector('i').classList.toggle('bi-heart');
            button.querySelector('i').classList.toggle('bi-heart-fill');
            
            // Update count
            const countElement = button.querySelector('.like-count');
            if (countElement) {
                let count = parseInt(countElement.textContent) || 0;
                countElement.textContent = isLiked ? count - 1 : count + 1;
            }
        },
        
        toggleSubscription: function(button) {
            const channelId = button.dataset.channelId;
            const isSubscribed = button.classList.contains('subscribed');
            
            // Optimistic UI update
            button.classList.toggle('subscribed');
            button.classList.toggle('subscribed-btn');
            
            const text = button.querySelector('.subscribe-text');
            if (text) {
                text.textContent = isSubscribed ? 'Subscribe' : 'Subscribed';
            }
            
            const icon = button.querySelector('i');
            if (icon) {
                icon.classList.toggle('bi-plus');
                icon.classList.toggle('bi-check');
            }
        },
        
        handleCommentSubmit: function(event, form) {
            const submitBtn = form.querySelector('button[type="submit"]');
            const textarea = form.querySelector('textarea');
            
            if (textarea.value.trim() === '') {
                PlayBharat.utils.showToast('Please enter a comment', 'warning');
                return;
            }
            
            // Show loading state
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="loading-spinner me-2"></span>Posting...';
        }
    },
    
    // User interface
    ui: {
        init: function() {
            this.setupResponsiveNav();
            this.setupInfiniteScroll();
            this.setupModals();
        },
        
        setupResponsiveNav: function() {
            // Handle mobile navigation
            const navToggle = document.querySelector('.navbar-toggler');
            const navCollapse = document.querySelector('.navbar-collapse');
            
            if (navToggle && navCollapse) {
                navToggle.addEventListener('click', () => {
                    navCollapse.classList.toggle('show');
                });
            }
        },
        
        setupInfiniteScroll: function() {
            const loadMoreTrigger = document.querySelector('.load-more-trigger');
            if (loadMoreTrigger) {
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            this.loadMoreContent();
                        }
                    });
                });
                
                observer.observe(loadMoreTrigger);
            }
        },
        
        loadMoreContent: function() {
            console.log('Loading more content...');
            // This would typically trigger an HTMX request
        },
        
        setupModals: function() {
            // Handle modal events
            document.addEventListener('hidden.bs.modal', (e) => {
                const forms = e.target.querySelectorAll('form');
                forms.forEach(form => form.reset());
            });
        }
    },
    
    // Analytics
    analytics: {
        init: function() {
            this.trackPageView();
            this.setupEventTracking();
        },
        
        trackPageView: function() {
            // Track page views for analytics
            const data = {
                page: window.location.pathname,
                title: document.title,
                timestamp: new Date().toISOString()
            };
            
            console.log('Page view:', data);
        },
        
        setupEventTracking: function() {
            // Track various user interactions
            document.addEventListener('click', (e) => {
                const target = e.target.closest('[data-track]');
                if (target) {
                    this.trackEvent(target.dataset.track, target.dataset);
                }
            });
        },
        
        trackEvent: function(eventName, data) {
            console.log('Event tracked:', eventName, data);
        }
    }
};

// Initialize PlayBharat when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('PlayBharat initializing...');
    
    // Initialize all modules
    PlayBharat.search.init();
    PlayBharat.video.init();
    PlayBharat.interactions.init();
    PlayBharat.ui.init();
    PlayBharat.analytics.init();
    
    // Store CSRF token
    PlayBharat.config.csrfToken = PlayBharat.utils.getCsrfToken();
    
    console.log('PlayBharat initialized successfully!');
});

// HTMX event handlers
document.addEventListener('htmx:beforeRequest', function(event) {
    // Add CSRF token to all HTMX requests
    const token = PlayBharat.utils.getCsrfToken();
    if (token) {
        event.detail.headers['X-CSRFToken'] = token;
    }
});

document.addEventListener('htmx:responseError', function(event) {
    PlayBharat.utils.showToast('Something went wrong. Please try again.', 'error');
});

document.addEventListener('htmx:timeout', function(event) {
    PlayBharat.utils.showToast('Request timed out. Please check your connection.', 'warning');
});

// Export for global access
window.PB = PlayBharat;