// PlayBharat Video Player JavaScript

class PlayBharatVideoPlayer {
    constructor(container) {
        this.container = container;
        this.video = container.querySelector('video');
        this.controls = container.querySelector('.video-controls');
        this.playBtn = container.querySelector('.play-btn');
        this.progressBar = container.querySelector('.video-progress-bar');
        this.progress = container.querySelector('.video-progress');
        this.timeDisplay = container.querySelector('.video-time');
        this.volumeSlider = container.querySelector('.video-volume-slider');
        this.fullscreenBtn = container.querySelector('.fullscreen-btn');
        this.qualityBtn = container.querySelector('.video-quality-btn');
        
        this.isPlaying = false;
        this.isDragging = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.updateTimeDisplay();
    }
    
    setupEventListeners() {
        // Play/pause
        if (this.playBtn) {
            this.playBtn.addEventListener('click', () => this.togglePlay());
        }
        
        if (this.video) {
            this.video.addEventListener('click', () => this.togglePlay());
            this.video.addEventListener('loadedmetadata', () => this.onVideoLoaded());
            this.video.addEventListener('timeupdate', () => this.onTimeUpdate());
            this.video.addEventListener('ended', () => this.onVideoEnded());
        }
        
        // Progress bar
        if (this.progressBar) {
            this.progressBar.addEventListener('click', (e) => this.onProgressBarClick(e));
            this.progressBar.addEventListener('mousedown', () => this.isDragging = true);
            document.addEventListener('mouseup', () => this.isDragging = false);
            this.progressBar.addEventListener('mousemove', (e) => this.onProgressBarMove(e));
        }
        
        // Volume
        if (this.volumeSlider) {
            this.volumeSlider.addEventListener('click', (e) => this.onVolumeChange(e));
        }
        
        // Fullscreen
        if (this.fullscreenBtn) {
            this.fullscreenBtn.addEventListener('click', () => this.toggleFullscreen());
        }
        
        // Quality selector
        if (this.qualityBtn) {
            this.qualityBtn.addEventListener('click', () => this.showQualityMenu());
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.onKeyPress(e));
        
        // Hide controls after inactivity
        this.setupControlsHiding();
    }
    
    togglePlay() {
        if (!this.video) return;
        
        if (this.isPlaying) {
            this.video.pause();
            this.isPlaying = false;
            if (this.playBtn) {
                this.playBtn.innerHTML = '<i class="bi bi-play-fill"></i>';
            }
        } else {
            this.video.play();
            this.isPlaying = true;
            if (this.playBtn) {
                this.playBtn.innerHTML = '<i class="bi bi-pause-fill"></i>';
            }
            
            // Track view for analytics
            this.trackView();
        }
    }
    
    onVideoLoaded() {
        this.updateTimeDisplay();
        console.log('Video loaded successfully');
    }
    
    onTimeUpdate() {
        if (!this.isDragging) {
            this.updateProgress();
        }
        this.updateTimeDisplay();
    }
    
    onVideoEnded() {
        this.isPlaying = false;
        if (this.playBtn) {
            this.playBtn.innerHTML = '<i class="bi bi-play-fill"></i>';
        }
        
        // Track completion
        this.trackCompletion();
    }
    
    updateProgress() {
        if (!this.video || !this.progress) return;
        
        const percentage = (this.video.currentTime / this.video.duration) * 100;
        this.progress.style.width = percentage + '%';
    }
    
    updateTimeDisplay() {
        if (!this.video || !this.timeDisplay) return;
        
        const current = this.formatTime(this.video.currentTime || 0);
        const total = this.formatTime(this.video.duration || 0);
        this.timeDisplay.textContent = `${current} / ${total}`;
    }
    
    formatTime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        } else {
            return `${minutes}:${secs.toString().padStart(2, '0')}`;
        }
    }
    
    onProgressBarClick(e) {
        if (!this.video || !this.progressBar) return;
        
        const rect = this.progressBar.getBoundingClientRect();
        const percentage = (e.clientX - rect.left) / rect.width;
        this.video.currentTime = percentage * this.video.duration;
    }
    
    onProgressBarMove(e) {
        if (!this.isDragging || !this.video || !this.progressBar) return;
        
        const rect = this.progressBar.getBoundingClientRect();
        const percentage = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
        this.video.currentTime = percentage * this.video.duration;
    }
    
    onVolumeChange(e) {
        if (!this.video || !this.volumeSlider) return;
        
        const rect = this.volumeSlider.getBoundingClientRect();
        const percentage = (e.clientX - rect.left) / rect.width;
        this.video.volume = Math.max(0, Math.min(1, percentage));
    }
    
    toggleFullscreen() {
        if (!document.fullscreenElement) {
            this.container.requestFullscreen().catch(err => {
                console.log('Error attempting to enable fullscreen:', err.message);
            });
        } else {
            document.exitFullscreen();
        }
    }
    
    showQualityMenu() {
        // Create quality selection menu
        const qualities = ['1080p', '720p', '480p', '360p', 'Auto'];
        const menu = document.createElement('div');
        menu.className = 'quality-menu position-absolute bg-dark text-white rounded p-2';
        menu.style.bottom = '50px';
        menu.style.right = '0px';
        menu.style.zIndex = '1000';
        
        qualities.forEach(quality => {
            const item = document.createElement('div');
            item.className = 'quality-item p-2 cursor-pointer hover:bg-gray-700';
            item.textContent = quality;
            item.addEventListener('click', () => {
                this.changeQuality(quality);
                menu.remove();
            });
            menu.appendChild(item);
        });
        
        this.container.appendChild(menu);
        
        // Remove menu when clicking outside
        setTimeout(() => {
            document.addEventListener('click', function removeMenu(e) {
                if (!menu.contains(e.target)) {
                    menu.remove();
                    document.removeEventListener('click', removeMenu);
                }
            });
        }, 0);
    }
    
    changeQuality(quality) {
        console.log(`Changing video quality to: ${quality}`);
        
        // In a real implementation, this would switch video sources
        // For now, we'll just update the button text
        if (this.qualityBtn) {
            this.qualityBtn.textContent = quality;
        }
        
        // Show notification
        PlayBharat.utils.showToast(`Video quality changed to ${quality}`, 'success', 2000);
    }
    
    onKeyPress(e) {
        // Only handle shortcuts when video player is focused
        if (!this.container.contains(document.activeElement) && document.activeElement !== document.body) {
            return;
        }
        
        switch(e.code) {
            case 'Space':
                e.preventDefault();
                this.togglePlay();
                break;
            case 'KeyF':
                e.preventDefault();
                this.toggleFullscreen();
                break;
            case 'KeyM':
                e.preventDefault();
                this.toggleMute();
                break;
            case 'ArrowLeft':
                e.preventDefault();
                this.seek(-10);
                break;
            case 'ArrowRight':
                e.preventDefault();
                this.seek(10);
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.changeVolume(0.1);
                break;
            case 'ArrowDown':
                e.preventDefault();
                this.changeVolume(-0.1);
                break;
        }
    }
    
    toggleMute() {
        if (!this.video) return;
        
        this.video.muted = !this.video.muted;
        
        // Update mute button if it exists
        const muteBtn = this.container.querySelector('.mute-btn');
        if (muteBtn) {
            muteBtn.innerHTML = this.video.muted ? 
                '<i class="bi bi-volume-mute"></i>' : 
                '<i class="bi bi-volume-up"></i>';
        }
    }
    
    seek(seconds) {
        if (!this.video) return;
        
        this.video.currentTime = Math.max(0, Math.min(this.video.duration, this.video.currentTime + seconds));
    }
    
    changeVolume(delta) {
        if (!this.video) return;
        
        this.video.volume = Math.max(0, Math.min(1, this.video.volume + delta));
    }
    
    setupControlsHiding() {
        let hideTimeout;
        
        const showControls = () => {
            if (this.controls) {
                this.controls.style.opacity = '1';
            }
            clearTimeout(hideTimeout);
            hideTimeout = setTimeout(hideControls, 3000);
        };
        
        const hideControls = () => {
            if (this.controls && this.isPlaying) {
                this.controls.style.opacity = '0';
            }
        };
        
        this.container.addEventListener('mousemove', showControls);
        this.container.addEventListener('mouseenter', showControls);
        this.container.addEventListener('mouseleave', hideControls);
    }
    
    trackView() {
        // Track video view for analytics
        const videoId = this.video.dataset.videoId;
        if (videoId && typeof htmx !== 'undefined') {
            htmx.ajax('POST', '/streaming/track/view/', {
                values: { video_id: videoId },
                headers: { 'X-CSRFToken': PlayBharat.utils.getCsrfToken() }
            });
        }
    }
    
    trackCompletion() {
        // Track video completion
        const videoId = this.video.dataset.videoId;
        if (videoId && typeof htmx !== 'undefined') {
            htmx.ajax('POST', '/streaming/track/engagement/', {
                values: { 
                    video_id: videoId, 
                    type: 'complete' 
                },
                headers: { 'X-CSRFToken': PlayBharat.utils.getCsrfToken() }
            });
        }
    }
}

// Initialize video players when page loads
document.addEventListener('DOMContentLoaded', function() {
    const videoContainers = document.querySelectorAll('.video-player-container');
    videoContainers.forEach(container => {
        new PlayBharatVideoPlayer(container);
    });
    
    console.log('PlayBharat video players initialized');
});

// Export for global use
window.PlayBharatVideoPlayer = PlayBharatVideoPlayer;