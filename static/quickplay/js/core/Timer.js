/**
 * Manages the game timer and its visual representation
 */
export class GameTimer {
    constructor(domManager) {
        this.domManager = domManager;
        this.animationFrameId = null;
        this.progressCircle = null;
        this.timerText = null;
        this.circumference = null;
        this.isInTransition = false;
        this._nextTimeLimit = null;
        
        // New properties for accurate timing
        this.startTime = null;
        this.timeLimit = null;
        this.onTimeUp = null;
        this.isGameActive = false;
        
        // Bind methods
        this.handleVisibilityChange = this.handleVisibilityChange.bind(this);
        this.updateTimer = this.updateTimer.bind(this);
        
        // Add visibility change listener
        document.addEventListener('visibilitychange', this.handleVisibilityChange);
    }

    initializeTimerStructure() {
        const size = 200;
        const strokeWidth = 15;
        const radius = (size - strokeWidth) / 2;
        
        if (this.domManager.timerElement) {
            this.domManager.timerElement.className = 'timer-container';
            this.domManager.timerElement.innerHTML = `
                <div class="timer-text">0:00</div>
                <svg class="timer-circle">
                    <circle cx="${size/2}" cy="${size/2}" r="${radius}" 
                            stroke="#334155" stroke-width="${strokeWidth}" fill="none"/>
                    <circle class="progress-circle" cx="${size/2}" cy="${size/2}" r="${radius}" 
                            stroke="#22c55e" stroke-width="${strokeWidth}" fill="none" stroke-linecap="round"/>
                </svg>
            `;
        
            this.progressCircle = this.domManager.timerElement.querySelector('.progress-circle');
            this.timerText = this.domManager.timerElement.querySelector('.timer-text');
            
            this.circumference = radius * 2 * Math.PI;
            if (this.progressCircle) {
                this.progressCircle.style.strokeDasharray = this.circumference;
            }
        }
    }

    handleVisibilityChange() {
        if (document.hidden) {
            // Tab is hidden, continue timer but stop visual updates
            if (this.animationFrameId) {
                cancelAnimationFrame(this.animationFrameId);
                this.animationFrameId = null;
            }
        } else {
            // Tab is visible again, resume visual updates
            if (this.isGameActive && !this.isInTransition) {
                this.animationFrameId = requestAnimationFrame(this.updateTimer);
            }
        }
    }

    updateTimer(currentTime) {
        if (!this.isGameActive || this.isInTransition || !this.startTime) {
            if (this.animationFrameId) {
                cancelAnimationFrame(this.animationFrameId);
                this.animationFrameId = null;
            }
            return;
        }

        const elapsedTime = (currentTime - this.startTime) / 1000;
        const timeLeft = Math.max(0, Math.ceil(this.timeLimit - elapsedTime));
        
        if (!this.domManager.timerElement.classList.contains('time-change-pulse')) {
            this.timerText.textContent = `0:${timeLeft.toString().padStart(2, '0')}`;
        }
        
        const progress = (timeLeft / this.timeLimit) * 100;
        const offset = this.circumference - (progress / 100) * this.circumference;
        this.progressCircle.style.strokeDashoffset = offset;
        
        this.updateTimerColor(progress);

        if (timeLeft <= 5) {
            this.timerText.classList.add('final-countdown');
            if (navigator.vibrate) {
                navigator.vibrate(100);
            }
        }
        
        if (timeLeft <= 0) {
            this.timerText.classList.remove('final-countdown');
            this.stopTimer();
            this.onTimeUp();
            return;
        }

        this.animationFrameId = requestAnimationFrame(this.updateTimer);
    }

    startTimer(timeLimit, isGameActive, onTimeUp) {
        this.stopTimer();

        this.timeLimit = timeLimit;
        this.isGameActive = isGameActive;
        this.onTimeUp = onTimeUp;
        this.startTime = performance.now();

        if (!this.isInTransition) {
            this.animationFrameId = requestAnimationFrame(this.updateTimer);
        }
    }

    updateTimerColor(progress) {
        if (progress > 60) {
            this.progressCircle.style.stroke = '#22c55e';
        } else if (progress > 30) {
            this.progressCircle.style.stroke = '#eab308';
        } else {
            this.progressCircle.style.stroke = '#dc2626';
        }
    }

    triggerDifficultyTransition(oldTimeLimit, newTimeLimit) {
        this.isInTransition = true;
        this.stopTimer();
    
        // Create a temporary progress circle for the transition
        const oldProgressCircle = this.progressCircle.cloneNode(true);
        this.progressCircle.parentNode.appendChild(oldProgressCircle);
        
        // Add spiral animation classes
        oldProgressCircle.classList.add('timer-spiral-out');
        this.progressCircle.classList.add('timer-spiral-in');
        this.progressCircle.style.opacity = '0';
        
        // Set up number transition
        const oldNumber = document.createElement('div');
        oldNumber.className = 'timer-text timer-number-spiral-out';
        oldNumber.textContent = `${oldTimeLimit}s`;
        
        const newNumber = document.createElement('div');
        newNumber.className = 'timer-text timer-number-spiral-in';
        newNumber.textContent = `${newTimeLimit}s`;
        newNumber.style.opacity = '0';
        
        this.timerText.innerHTML = '';
        this.timerText.appendChild(oldNumber);
        this.timerText.appendChild(newNumber);
        
        this._nextTimeLimit = newTimeLimit;
        
        return new Promise(resolve => {
            setTimeout(() => {
                this.progressCircle.style.opacity = '1';
                newNumber.style.opacity = '1';
            }, 50);
    
            setTimeout(() => {
                oldProgressCircle.remove();
                this.timerText.innerHTML = newTimeLimit + 's';
                
                this.isInTransition = false;
                this.progressCircle.classList.remove('timer-spiral-in');
                
                resolve(this._nextTimeLimit);
                this._nextTimeLimit = null;
            }, 1500);
        });
    }

    stopTimer() {
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
            this.animationFrameId = null;
        }
        this.startTime = null;
        this.timeLimit = null;
        this.isGameActive = false;
        this.onTimeUp = null;
        this.timerText?.classList.remove('final-countdown');
    }

    // Clean up when the timer is destroyed
    destroy() {
        document.removeEventListener('visibilitychange', this.handleVisibilityChange);
        this.stopTimer();
    }
}