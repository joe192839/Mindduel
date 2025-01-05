import { AnimationManager } from './ui/AnimationManager.js';

class MenuManager {
    constructor() {
        this.animationManager = new AnimationManager();
        this.setupEventListeners();
    }

    setupEventListeners() {
        const startButton = document.querySelector('#startGameButton');
        if (startButton) {
            startButton.addEventListener('click', async (e) => {
                e.preventDefault();
                startButton.disabled = true;
                
                // Show animation first
                await this.animationManager.showBrainWarmup();
                
                // After animation completes, redirect to game
                window.location.href = startButton.getAttribute('href');
            });
        }
    }
}

// Initialize when DOM loads
document.addEventListener('DOMContentLoaded', () => {
    new MenuManager();
});