console.log('Game.js loaded successfully');

class HeartStateManager {
    constructor(game) {
        this.game = game;
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
        const hearts = this.game.livesElement.querySelectorAll('.heart-icon');
        
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

class QuickplayGame {
    constructor() {
        // Clean up any existing game instance
        if (window.quickplayGame) {
            if (window.quickplayGame.timer) {
                clearInterval(window.quickplayGame.timer);
            }
            window.quickplayGame = null;
        }

        console.log('QuickplayGame initialized');
        this.gameId = null;
        this.questionNumber = 0;
        this.timer = null;
        this.score = 0;
        this.lives = 3;
        this.currentQuestion = null;
        this.isGameActive = false;
        this.isInTransition = false;
        this.urls = window.QUICKPLAY_URLS;

        // Timer properties
        this.progressCircle = null;
        this.timerText = null;
        this.circumference = null;

        // Sound setup
        this.soundEnabled = true;
        this.correctSound = document.getElementById('correctSound');
        this.wrongSound = document.getElementById('wrongSound');

        // DOM Elements with existence checks
        this.timerElement = document.getElementById('timer');
        this.scoreElement = document.getElementById('score');
        this.livesElement = document.getElementById('lives');
        this.questionElement = document.getElementById('questionText');
        this.optionsContainer = document.getElementById('options');
        this.quitButton = document.getElementById('quitButton');
        this.startButton = document.getElementById('startButton');
        this.gameHeader = document.querySelector('.game-header');

        // Verify critical elements exist
        if (!this.timerElement || !this.scoreElement || !this.livesElement || 
            !this.questionElement || !this.optionsContainer) {
            console.error('Critical game elements not found');
            return;
        }

        // Initialize heart state manager
        this.heartStateManager = new HeartStateManager(this);

        // Add navbar and fullscreen properties
        this.navbar = document.querySelector('nav');
        this.isFullscreen = false;

        // Initialize with hidden header
        if (this.gameHeader) {
            this.gameHeader.classList.remove('active');
        }

        // Bind event listeners
        if (this.startButton) {
            this.startButton.addEventListener('click', () => this.startGame());
        }
        if (this.quitButton) {
            this.quitButton.addEventListener('click', () => this.endGame('quit'));
        }

        // Initialize sound toggle
        const muteButton = document.getElementById('muteButton');
        const floatingMuteButton = document.getElementById('floatingMuteButton');

        if (muteButton && floatingMuteButton) {
            [muteButton, floatingMuteButton].forEach(button => {
                button.addEventListener('click', () => this.toggleSound());
            });
            
            const savedSoundState = localStorage.getItem('soundEnabled');
            if (savedSoundState !== null) {
                this.soundEnabled = savedSoundState === 'true';
                this.updateSoundIcon();
            }
        }

        // Add ESC key handler
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isFullscreen) {
                this.exitFullscreenMode();
            }
        });

        // Initialize timer structure
        this.initializeTimerStructure();
    }

    enterFullscreenMode() {
        this.isFullscreen = true;
        if (this.navbar) {
            this.navbar.style.transition = 'transform 0.5s ease, opacity 0.5s ease';
            this.navbar.style.transform = 'translateY(-100%)';
            this.navbar.style.opacity = '0';
        }
        document.body.style.paddingTop = '1rem';
    }

    exitFullscreenMode() {
        if (!this.isFullscreen) return;
        
        this.isFullscreen = false;
        if (this.navbar) {
            this.navbar.style.transform = 'translateY(0)';
            this.navbar.style.opacity = '1';
        }
        document.body.style.paddingTop = '0';
    }

    initializeTimerStructure() {
        const size = 200;
        const strokeWidth = 15;
        const radius = (size - strokeWidth) / 2;
        
        if (this.timerElement) {
            this.timerElement.className = 'timer-container';
            this.timerElement.innerHTML = `
                <div class="timer-text">0:00</div>
                <svg class="timer-circle">
                    <circle cx="${size/2}" cy="${size/2}" r="${radius}" 
                            stroke="#334155" stroke-width="${strokeWidth}" fill="none"/>
                    <circle class="progress-circle" cx="${size/2}" cy="${size/2}" r="${radius}" 
                            stroke="#22c55e" stroke-width="${strokeWidth}" fill="none" stroke-linecap="round"/>
                </svg>
            `;
        
            this.progressCircle = this.timerElement.querySelector('.progress-circle');
            this.timerText = this.timerElement.querySelector('.timer-text');
            
            this.circumference = radius * 2 * Math.PI;
            if (this.progressCircle) {
                this.progressCircle.style.strokeDasharray = this.circumference;
            }
        }
    }

    getQuestionTimeLimit() {
        const questionGroup = Math.floor(this.questionNumber / 3);
        const previousGroup = Math.floor((this.questionNumber - 1) / 3);
        
        const oldTimeLimit = (() => {
            switch (previousGroup) {
                case 0: return 60;
                case 1: return 50;
                case 2: return 40;
                case 3: return 30;
                case 4: return 20;
                case 5: return 15;
                case 6: return 10;
                default: return 5;
            }
        })();
        
        const newTimeLimit = (() => {
            switch (questionGroup) {
                case 0: return 60;
                case 1: return 50;
                case 2: return 40;
                case 3: return 30;
                case 4: return 20;
                case 5: return 15;
                case 6: return 10;
                default: return 5;
            }
        })();
        
        if (questionGroup !== previousGroup && this.questionNumber > 1 && !this.isInTransition) {
            this.triggerDifficultyTransition(oldTimeLimit, newTimeLimit);
        }
        
        return newTimeLimit;
    }

    triggerDifficultyTransition(oldTimeLimit, newTimeLimit) {
        this.isInTransition = true;
        
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
        
        this.timerElement.classList.add('time-change-pulse');
        
        this.timerText.innerHTML = `
            <div class="old-time">${oldTimeLimit}s</div>
            <div class="new-time">${newTimeLimit}s</div>
        `;
        
        this._nextTimeLimit = newTimeLimit;
        
        setTimeout(() => {
            this.isInTransition = false;
            this.timerElement.classList.remove('time-change-pulse');
            this.timerText.innerHTML = newTimeLimit + 's';
            this.startTimer(this._nextTimeLimit);
            this._nextTimeLimit = null;
        }, 1500);
    }

    toggleSound() {
        this.soundEnabled = !this.soundEnabled;
        localStorage.setItem('soundEnabled', this.soundEnabled);
        this.updateSoundIcon();
    }

    updateSoundIcon() {
        const muteButton = document.getElementById('muteButton');
        const floatingMuteButton = document.getElementById('floatingMuteButton');
        
        const icon = this.soundEnabled ? '🔊' : '🔈';
        
        if (muteButton) muteButton.textContent = icon;
        if (floatingMuteButton) floatingMuteButton.textContent = icon;
    }

    async showBrainWarmup() {
        return new Promise((resolve) => {
            const overlay = document.createElement('div');
            overlay.className = 'brain-warmup-overlay';
            overlay.innerHTML = `
                <div class="brain-warmup-content">
                    <div class="brain-icon-container">
                        <svg class="brain-icon" style="width: 16rem; height: 16rem;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"/>
                            <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"/>
                        </svg>
                        <div class="synapses hidden">
                            ${[0, 120, 240].map(angle => `
                                <svg class="synapse" style="width: 4rem; height: 4rem; transform: rotate(${angle}deg) translateY(-40px)" ...>
                                    <path d="M13 2L3 14h9l-1 8 10-16h-9l1-4z"/>
                                </svg>
                            `).join('')}
                        </div>
                    </div>
                    <div class="animation-message text-gray-600" style="font-size: 3rem;">Initializing...</div>
                    <div class="progress-dots">
                        ${[...Array(4)].map(() => '<div class="progress-dot"></div>').join('')}
                    </div>
                </div>
            `;

            document.body.appendChild(overlay);

            const brain = overlay.querySelector('.brain-icon');
            const synapses = overlay.querySelector('.synapses');
            const message = overlay.querySelector('.animation-message');
            const dots = overlay.querySelectorAll('.progress-dot');

            let phase = 0;

            const updatePhase = () => {
                phase++;
                brain.classList.add('active');
                
                if (phase > 1) {
                    synapses.classList.remove('hidden');
                }

                message.className = 'animation-message';
                switch(phase) {
                    case 1:
                        message.textContent = 'Brain Engaged';
                        message.classList.add('text-[#009fdc]');
                        break;
                    case 2:
                        message.textContent = 'Synapses Firing';
                        break;
                    case 3:
                        message.textContent = 'Ready For Challenge';
                        break;
                    case 4:
                        message.innerHTML = '<div class="flex items-center justify-center gap-2 text-[#009fdc]"><span>GO</span><span class="animate-bounce">→</span></div>';
                        break;
                }

                for (let i = 0; i < phase; i++) {
                    if (dots[i]) {
                        dots[i].classList.add('active');
                    }
                }
            };

            setTimeout(() => updatePhase(), 1000);
            setTimeout(() => updatePhase(), 2000);
            setTimeout(() => updatePhase(), 3000);
            setTimeout(() => updatePhase(), 4000);

            setTimeout(() => {
                overlay.style.animation = 'fadeOut 0.5s forwards';
                setTimeout(() => {
                    overlay.remove();
                    resolve();
                }, 500);
            }, 5000);
        });
    }

    async startGame() {
        console.log('Starting game...');
        if (this.startButton) {
            this.startButton.disabled = true;
        }

        try {
            await this.showBrainWarmup();
            
            this.enterFullscreenMode();
            
            const response = await fetch(this.urls.startGame, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken'),
                }
            });
            const data = await response.json();
            
            this.gameId = data.game_id;
            this.isGameActive = true;
            this.score = 0;
            this.lives = 3;
            this.questionNumber = 0;
            
            if (this.timer) {
                clearInterval(this.timer);
                this.timer = null;
            }
            this.initializeTimerStructure();

            if (this.gameHeader) {
                this.gameHeader.classList.add('active');
            }
            
            if (this.startButton) {
                this.startButton.classList.add('hidden');
            }
            if (this.quitButton) {
                this.quitButton.classList.remove('hidden');
            }
            
            this.updateDisplay();
            this.loadQuestion();
        } catch (error) {
            console.error('Failed to start game:', error);
            this.exitFullscreenMode();
            if (this.startButton) {
                this.startButton.disabled = false;
            }
            this.showError('Failed to start game. Please try again.');
        }
    }
        
    updateLivesDisplay() {
        this.livesElement.innerHTML = '';
        for (let i = 0; i < this.lives; i++) {
            const heartImg = document.createElement('img');
            heartImg.src = '/static/images/heart.png';
            heartImg.alt = 'Heart';
            heartImg.style.width = '3rem';
            heartImg.style.height = '3rem';
            heartImg.style.marginRight = i < this.lives - 1 ? '0.5rem' : '0';
            heartImg.classList.add('heart-icon');
            this.livesElement.appendChild(heartImg);
        }
        this.heartStateManager.updateHeartStates(this.lives);
    }

    updateDisplay() {
        this.scoreElement.textContent = this.score;
        this.updateLivesDisplay();
    }

    startTimer(specificTimeLimit = null) {
        if (this.timer) {
            clearInterval(this.timer);
        }
    
        let timeLeft = specificTimeLimit || this.getQuestionTimeLimit();
        const totalTime = timeLeft;
        
        const updateTimer = () => {
            if (!this.isGameActive || this.isInTransition) {
                clearInterval(this.timer);
                return;
            }
    
            const seconds = timeLeft;
            
            if (!this.timerElement.classList.contains('time-change-pulse')) {
                this.timerText.textContent = `0:${seconds.toString().padStart(2, '0')}`;
            }
            
            const progress = (timeLeft / totalTime) * 100;
            const offset = this.circumference - (progress / 100) * this.circumference;
            this.progressCircle.style.strokeDashoffset = offset;
            
            if (progress > 60) {
                this.progressCircle.style.stroke = '#22c55e';
            } else if (progress > 30) {
                this.progressCircle.style.stroke = '#eab308';
            } else {
                this.progressCircle.style.stroke = '#dc2626';
            }
    
            if (timeLeft <= 5) {
                this.timerText.classList.add('final-countdown');
                if (navigator.vibrate) {
                    navigator.vibrate(100);
                }
            }
            
            if (timeLeft <= 0) {
                clearInterval(this.timer);
                this.timerText.classList.remove('final-countdown');
                this.lives--;
                this.updateDisplay();
                
                if (this.lives <= 0) {
                    this.endGame('lives');
                } else {
                    this.loadQuestion();
                }
            }
        };
            
        if (!this.isInTransition) {
            this.timer = setInterval(() => {
                timeLeft--;
                updateTimer();
            }, 1000);
            
            updateTimer();
        }
    }

    async loadQuestion() {
        try {
            if (!this.isGameActive) return;
            
            this.timerText.classList.remove('final-countdown');
            document.body.style.backgroundColor = '#009fdc';
            
            if (this.timer) {
                clearInterval(this.timer);
                this.timer = null;
            }
            
            const response = await fetch(`${this.urls.getQuestion}?game_id=${this.gameId}`);
            const data = await response.json();
            
            if (data.status === 'game_over') {
                return this.endGame('complete');
            }
            
            this.optionsContainer.innerHTML = '';
            this.questionElement.style.opacity = '0';
            
            this.questionNumber++;
            this.currentQuestion = data;
            
            setTimeout(() => {
                this.questionElement.textContent = data.question_text;
                this.questionElement.style.opacity = '1';
                
                const options = [data.option_1, data.option_2, data.option_3, data.option_4];
                
                options.forEach((option) => {
                    const button = document.createElement('button');
                    button.className = 'option-button bg-white text-[#009fdc] font-bold py-3 px-6 rounded hover:bg-gray-100 transition-all duration-300';
                    button.textContent = option;
                    button.addEventListener('click', () => this.submitAnswer(option, button));
                    this.optionsContainer.appendChild(button);
                });
                
                this.optionsContainer.style.opacity = '1';
                this.startTimer();
            }, 100);
            
        } catch (error) {
            console.error('Failed to load question:', error);
            this.showError('Failed to load question. Please try again.');
            this.isGameActive = false;
        }
    }

    async submitAnswer(answer, button) {
        if (!this.isGameActive) return;

        try {
            const buttons = this.optionsContainer.querySelectorAll('button');
            buttons.forEach(btn => btn.disabled = true);

            const formData = new FormData();
            formData.append('game_id', this.gameId);
            formData.append('answer', answer);
            formData.append('question_id', this.currentQuestion.id);

            const response = await fetch(this.urls.submitAnswer, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken'),
                },
                body: formData
            });
            
            const data = await response.json();

            const getPointText = (p) => p === 1 ? 'point' : 'points';
        
            const overlay = document.createElement('div');
            overlay.className = `feedback-overlay ${data.correct ? 'correct' : 'incorrect'}`;
            const points = data.correct ? 1 : 0;
            overlay.innerHTML = `
                <div class="feedback-icon">${data.correct ? '✨' : '❌'}</div>
                <div class="feedback-text">${data.correct ? 'Correct!' : 'Incorrect'}</div>
                <div class="feedback-score">+${points} ${getPointText(points)}</div>
            `;
            
            this.questionElement.parentElement.appendChild(overlay);
            requestAnimationFrame(() => overlay.style.opacity = '1');
            
            if (data.correct) {
                if (this.soundEnabled && this.correctSound) {
                    this.correctSound.currentTime = 0;
                    this.correctSound.play().catch(err => console.warn('Audio play failed:', err));
                }
                this.score = data.score;
            } else {
                if (this.soundEnabled && this.wrongSound) {
                    this.wrongSound.currentTime = 0;
                    this.wrongSound.play().catch(err => console.warn('Audio play failed:', err));
                }
                const oldLives = this.lives;
                this.lives = data.lives;
                
                const hearts = this.livesElement.querySelectorAll('.heart-icon');
                const lastHeart = hearts[hearts.length - 1];
                if (lastHeart) {
                    lastHeart.classList.add('heart-break');
                    await new Promise(resolve => setTimeout(resolve, 600));
                }
                
                this.updateDisplay();
                this.heartStateManager.triggerLifeLossEffects();
            }
            
            this.updateDisplay();
            
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            if (this.lives <= 0) {
                this.endGame('lives');
            } else {
                overlay.remove();
                this.loadQuestion();
            }
        } catch (error) {
            console.error('Failed to submit answer:', error);
            this.showError('Failed to submit answer. Please try again.');
        }
    }

    async endGame(reason = 'unknown') {
        if (!this.isGameActive) return;
        
        this.isGameActive = false;
        
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
        
        const buttons = this.optionsContainer.querySelectorAll('button');
        buttons.forEach(button => {
            button.disabled = true;
            const newButton = button.cloneNode(true);
            button.parentNode.replaceChild(newButton, button);
        });
        
        this.exitFullscreenMode();
        
        if (this.gameHeader) {
            this.gameHeader.classList.remove('active');
        }
        
        await new Promise(resolve => setTimeout(resolve, 500));
        
        try {
            const response = await fetch(this.urls.endGame + (this.gameId !== 'anonymous' ? this.gameId + '/' : ''), {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    reason: reason,
                    score: this.score,
                    lives: this.lives
                })
            });
            
            const data = await response.json();
            
            if (data.redirect) {
                window.location.href = data.redirect;
            } else if (this.gameId === 'anonymous') {
                window.location.href = this.urls.anonymousResults;
            } else {
                window.location.href = `${this.urls.results}${this.gameId}/`;
            }
        } catch (error) {
            console.error('Error during end game:', error);
            window.location.href = this.gameId === 'anonymous' ? 
                this.urls.anonymousResults : 
                this.urls.results;
        }
    }

    showError(message) {
        console.error(message);
        alert(message);
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded - Initializing QuickplayGame');
    window.quickplayGame = new QuickplayGame();
});