import { GameState } from './core/GameState.js';  
import { GameTimer } from './core/Timer.js';
import { DOMManager } from './ui/DOMManager.js';
import { HeartStateManager } from './components/HeartStateManager.js';
import { AnimationManager } from './ui/AnimationManager.js';
import { AudioManager } from './utils/AudioManager.js';
import { ApiService } from './utils/ApiService.js';

class QuickplayGame {
    constructor() {
        // Clean up any existing game instance
        if (window.quickplayGame) {
            if (window.quickplayGame.timer) {
                clearInterval(window.quickplayGame.timer);
            }
            window.quickplayGame = null;
        }

        this.initializeComponents();
        this.setupEventListeners();
    }

    initializeComponents() {
        // Initialize core components
        this.domManager = new DOMManager();
        this.gameState = new GameState();
        this.timer = new GameTimer(this.domManager);
        
        // Initialize UI components
        this.heartStateManager = new HeartStateManager(this.domManager);
        this.animationManager = new AnimationManager(this.domManager);  // Pass domManager here
        
        // Initialize utility components
        this.audioManager = new AudioManager();
        this.apiService = new ApiService(window.QUICKPLAY_URLS);
        
        // Update initial UI state
        this.domManager.updateSoundIcon(this.audioManager.isSoundEnabled());
        this.domManager.setGameHeaderState(false);
    }

    setupEventListeners() {
        // Start button
        if (this.domManager.startButton) {
            this.domManager.startButton.addEventListener('click', () => this.startGame());
        }
        
        // Quit button
        if (this.domManager.quitButton) {
            this.domManager.quitButton.addEventListener('click', () => this.endGame('quit'));
        }
        
        // Sound toggle buttons
        if (this.domManager.muteButton && this.domManager.floatingMuteButton) {
            [this.domManager.muteButton, this.domManager.floatingMuteButton].forEach(button => {
                button.addEventListener('click', () => this.toggleSound());
            });
        }
        
        // ESC key for fullscreen exit
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.gameState.isFullscreen) {
                this.exitFullscreenMode();
            }
        });
        const questionTypeToggle = document.getElementById('questionTypeToggle');
        if (questionTypeToggle) {
            questionTypeToggle.addEventListener('click', () => {
                this.apiService.setUseAIQuestions(!this.apiService.useAIQuestions);
                questionTypeToggle.textContent = `Question Mode: ${this.apiService.useAIQuestions ? 'AI' : 'Regular'}`;
            });
        }
    }

    async startGame() {
        if (this.domManager.startButton) {
            this.domManager.startButton.disabled = true;
        }
    
        try {
            console.log('Starting game...');
            
            // Get categories from URL parameters
            const urlParams = new URLSearchParams(window.location.search);
            const selectedCategories = urlParams.getAll('categories');
            
            // Store categories in sessionStorage
            sessionStorage.setItem('selectedCategories', JSON.stringify(selectedCategories));
            
            console.log('Selected categories:', selectedCategories);
            
            // Log the API service state
            console.log('API Service state:', {
                urls: this.apiService.urls,
                gameState: this.gameState
            });
    
            // Start both the animation and game data loading in parallel
            const [gameData] = await Promise.all([
                this.apiService.startGame().catch(error => {
                    console.error('Failed to start game:', error);
                    throw error;
                }),
                this.animationManager.showBrainWarmup().catch(error => {
                    console.error('Animation error:', error);
                    return null; // Don't fail the game if animation fails
                })
            ]);
    
            console.log('Game started successfully:', gameData);
    
            if (!gameData || !gameData.game_id) {
                throw new Error('Invalid game data received');
            }
    
            this.enterFullscreenMode();
            this.gameState.initializeGame(gameData.game_id);
            
            console.log('Game state initialized:', {
                gameId: this.gameState.gameId,
                isActive: this.gameState.isGameActive
            });
    
            this.timer.initializeTimerStructure();
            this.domManager.setGameHeaderState(true);
            
            if (this.domManager.startButton) {
                this.domManager.startButton.classList.add('hidden');
            }
            if (this.domManager.quitButton) {
                this.domManager.quitButton.classList.remove('hidden');
            }
            
            this.updateDisplay();
            await this.loadQuestion();
            
        } catch (error) {
            console.error('Error starting game:', error);
            console.error('Stack trace:', error.stack);
            
            // Re-enable start button
            if (this.domManager.startButton) {
                this.domManager.startButton.disabled = false;
            }
    
            this.domManager.showError(`Failed to start game: ${error.message}`);
            
            // Don't redirect immediately on error
            if (this.gameState && this.gameState.gameId) {
                setTimeout(() => {
                    window.location.href = this.gameState.gameId === 'anonymous' ? 
                        this.apiService.urls.anonymousResults : 
                        `${this.apiService.urls.results}${this.gameState.gameId}/`;
                }, 2000);
            }
        }
    }

    async loadQuestion() {
        try {
            if (!this.gameState.isGameActive) return;
            
            this.timer.stopTimer();
            document.body.style.backgroundColor = '#009fdc';
            
            const questionData = await this.apiService.loadQuestion(this.gameState.gameId);
            
            if (questionData.status === 'game_over') {
                return this.endGame('complete');
            }
            
            this.gameState.setCurrentQuestion(questionData);
            
            // Pass the submitAnswer method bound to this instance
            this.domManager.displayQuestion(
                questionData,
                (answer, button) => this.submitAnswer(answer, button)
            );
            
            const { timeLimit, oldTimeLimit, difficultyChanged } = this.gameState.getQuestionTimeLimit();
            
            if (difficultyChanged) {
                await this.timer.triggerDifficultyTransition(oldTimeLimit, timeLimit);
            }
            
            this.timer.startTimer(timeLimit, this.gameState.isGameActive, () => {
                this.gameState.updateLives(this.gameState.lives - 1);
                this.updateDisplay();
                
                if (this.gameState.lives <= 0) {
                    this.endGame('lives');
                } else {
                    this.loadQuestion();
                }
            });
            
        } catch (error) {
            console.error('Failed to load question:', error);
            this.domManager.showError('Failed to load question. Please try again.');
            this.gameState.isGameActive = false;
        }
    }

    async submitAnswer(answer, button) {
        if (!this.gameState.isGameActive) return;  // Fixed: check gameState.isGameActive instead of this.isGameActive
    
        try {
            this.domManager.disableOptions();
            
            const data = await this.apiService.submitAnswer(
                this.gameState.gameId,
                answer,
                this.gameState.currentQuestion.id
            );
    
            if (data.correct) {
                this.audioManager.playCorrectSound();
                this.gameState.updateScore(data.score);
            } else {
                this.audioManager.playWrongSound();
                const shouldEndGame = this.gameState.updateLives(data.lives);
                this.heartStateManager.triggerLifeLossEffects();
                if (shouldEndGame) {
                    return this.endGame('lives');
                }
            }
            
            this.updateDisplay();
            await this.animationManager.showAnswerFeedback(data.correct, data.correct ? 1 : 0);
            await this.loadQuestion();
            
        } catch (error) {
            console.error('Failed to submit answer:', error);
            this.domManager.showError('Failed to submit answer. Please try again.');
        }
    }

    async endGame(reason = 'unknown') {
        if (!this.gameState.isGameActive) return;
        
        this.gameState.isGameActive = false;
        this.timer.stopTimer();
        this.domManager.disableOptions();
        this.exitFullscreenMode();
        this.domManager.setGameHeaderState(false);
        
        try {
            const data = await this.apiService.endGame(
                this.gameState.gameId,
                reason,
                this.gameState.score,
                this.gameState.lives,
                this.gameState.highestSpeedLevel
            );
            
            // Handle redirection based on user type and response
            if (data.redirect) {
                window.location.href = data.redirect;
            } else if (this.gameState.gameId === 'anonymous') {
                window.location.href = this.urls.anonymousResults;
            } else {
                window.location.href = `${this.urls.results}${this.gameState.gameId}/`;
            }
        } catch (error) {
            console.error('Error during end game:', error);
            // Fallback redirection if there's an error
            window.location.href = this.gameState.gameId === 'anonymous' ? 
                this.apiService.urls.anonymousResults : 
                `${this.apiService.urls.results}${this.gameState.gameId}/`;
        }
    }

    toggleSound() {
        const newSoundState = this.audioManager.toggleSound();
        this.domManager.updateSoundIcon(newSoundState);
    }

    enterFullscreenMode() {
        this.gameState.setFullscreen(true);
        this.domManager.updateFullscreenState(true);
    }

    exitFullscreenMode() {
        this.gameState.setFullscreen(false);
        this.domManager.updateFullscreenState(false);
    }

    updateDisplay() {
        this.domManager.updateScore(this.gameState.score);
        this.domManager.updateLivesDisplay(this.gameState.lives);
        this.heartStateManager.updateHeartStates(this.gameState.lives);
    }
}

// Initialize game when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded - Initializing QuickplayGame');
    window.quickplayGame = new QuickplayGame();
});

export default QuickplayGame;