// Create an AudioManager class to handle all audio-related functionality
class AudioManager {
    constructor() {
        this.backgroundMusic = null;
        this.isInitialized = false;
        this.isMuted = localStorage.getItem('audioMuted') === 'true';
        this.initializeAudio();
    }

    initializeAudio() {
        // Create the audio element
        this.backgroundMusic = document.getElementById('backgroundMusic');
        if (!this.backgroundMusic) {
            this.backgroundMusic = document.createElement('audio');
            this.backgroundMusic.id = 'backgroundMusic';
            this.backgroundMusic.loop = true;
            document.body.appendChild(this.backgroundMusic);
        }

        // Set the source
        const musicSource = document.createElement('source');
        musicSource.src = '/static/quickplay/audio/cyberpunk-inspirational-futuristic-music-272636.mp3';
        musicSource.type = 'audio/mpeg';
        this.backgroundMusic.appendChild(musicSource);

        // Update mute buttons
        this.updateMuteButtons();

        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseMusic();
            } else if (!this.isMuted) {
                this.playMusic();
            }
        });

        // Check if we're on the game page
        if (window.location.pathname.includes('/quickplay/game/')) {
            this.stopMusic();
        } else if (this.shouldPlayMusic()) {
            this.setupAutoplay();
        }
    }

    shouldPlayMusic() {
        const path = window.location.pathname;
        return path === '/' || path === '/quickplay/home/';
    }

    setupAutoplay() {
        const startMusic = () => {
            if (!this.isInitialized && !this.isMuted) {
                this.playMusic();
                this.isInitialized = true;
            }
        };

        // Start music on user interaction
        const interactionEvents = ['click', 'touchstart', 'keydown'];
        const handleInteraction = () => {
            startMusic();
            interactionEvents.forEach(event => {
                document.removeEventListener(event, handleInteraction);
            });
        };

        interactionEvents.forEach(event => {
            document.addEventListener(event, handleInteraction);
        });
    }

    playMusic() {
        if (this.backgroundMusic && !this.isMuted) {
            this.backgroundMusic.play().catch(error => {
                console.warn('Audio playback failed:', error);
            });
        }
    }

    pauseMusic() {
        if (this.backgroundMusic) {
            this.backgroundMusic.pause();
        }
    }

    stopMusic() {
        if (this.backgroundMusic) {
            this.backgroundMusic.pause();
            this.backgroundMusic.currentTime = 0;
        }
    }

    toggleMute() {
        this.isMuted = !this.isMuted;
        localStorage.setItem('audioMuted', this.isMuted);
        
        if (this.isMuted) {
            this.stopMusic();
        } else if (this.shouldPlayMusic()) {
            this.playMusic();
        }
        
        this.updateMuteButtons();
    }

    updateMuteButtons() {
        const muteButtons = document.querySelectorAll('[data-mute-button]');
        muteButtons.forEach(button => {
            button.textContent = this.isMuted ? '🔈' : '🔊';
        });
    }
}

// Initialize the audio manager when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.audioManager = new AudioManager();
});