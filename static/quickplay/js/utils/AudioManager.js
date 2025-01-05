/**
 * Manages all game audio functionality
 */
export class AudioManager {
    constructor() {
        this.correctSound = document.getElementById('correctSound');
        this.wrongSound = document.getElementById('wrongSound');
        this.soundEnabled = this.loadSoundPreference();
    }

    loadSoundPreference() {
        const savedSoundState = localStorage.getItem('soundEnabled');
        return savedSoundState !== null ? savedSoundState === 'true' : true;
    }

    /**
     * Plays the correct answer sound if sound is enabled
     */
    playCorrectSound() {
        if (this.soundEnabled && this.correctSound) {
            this.correctSound.currentTime = 0;
            this.correctSound.play().catch(err => {
                console.warn('Audio play failed:', err);
            });
        }
    }

    /**
     * Plays the wrong answer sound if sound is enabled
     */
    playWrongSound() {
        if (this.soundEnabled && this.wrongSound) {
            this.wrongSound.currentTime = 0;
            this.wrongSound.play().catch(err => {
                console.warn('Audio play failed:', err);
            });
        }
    }

    /**
     * Toggles sound on/off and saves preference
     * @returns {boolean} New sound state
     */
    toggleSound() {
        this.soundEnabled = !this.soundEnabled;
        localStorage.setItem('soundEnabled', this.soundEnabled);
        return this.soundEnabled;
    }

    /**
     * Gets current sound state
     * @returns {boolean} Whether sound is enabled
     */
    isSoundEnabled() {
        return this.soundEnabled;
    }
}