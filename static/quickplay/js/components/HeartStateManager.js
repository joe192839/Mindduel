/**
 * Manages the visual state and animations of the lives/hearts display
 */
export class HeartStateManager {
    constructor(domManager) {
        this.domManager = domManager;
        this.previousLives = 3;
        this.vignette = null;
        this.initializeVignette();
    }

    initializeVignette() {
        this.vignette = document.createElement('div');
        this.vignette.className = 'vignette-overlay';
        document.body.appendChild(this.vignette);
    }

    updateHeartStates(currentLives) {
        const hearts = this.domManager.livesElement.querySelectorAll('.heart-icon');
        
        hearts.forEach(heart => {
            heart.classList.remove('critical-heart', 'warning-heart', 'healthy-heart');
        });

        switch(currentLives) {
            case 1:
                this.applyCriticalState(hearts);
                break;
            case 2:
                this.applyWarningState(hearts);
                break;
            case 3:
                this.applyHealthyState(hearts);
                break;
        }

        this.previousLives = currentLives;
    }

    applyCriticalState(hearts) {
        hearts.forEach(heart => heart.classList.add('critical-heart'));
        this.vignette.classList.add('critical-vignette');
        this.vignette.classList.remove('warning-vignette');
    }

    applyWarningState(hearts) {
        hearts.forEach(heart => heart.classList.add('warning-heart'));
        this.vignette.classList.add('warning-vignette');
        this.vignette.classList.remove('critical-vignette');
    }

    applyHealthyState(hearts) {
        hearts.forEach(heart => heart.classList.add('healthy-heart'));
        this.vignette.classList.remove('critical-vignette', 'warning-vignette');
    }

    triggerLifeLossEffects() {
        this.flashScreen();
    }

    flashScreen() {
        const flash = document.createElement('div');
        flash.className = 'screen-flash';
        document.body.appendChild(flash);
        
        requestAnimationFrame(() => {
            flash.style.opacity = '1';
            setTimeout(() => {
                flash.style.opacity = '0';
                setTimeout(() => flash.remove(), 200);
            }, 100);
        });
    }
}