/**
 * Manages the core state of the QuickplayGame
 */
export class GameState {
    constructor() {
        // Game identification
        this.gameId = null;
        
        // Game progress
        this.questionNumber = 0;
        this.score = 0;
        this.lives = 3;
        this.currentQuestion = null;
        
        // Game state flags
        this.isGameActive = false;
        this.isInTransition = false;
        this.isFullscreen = false;
        
        // Settings
        this.soundEnabled = this.loadSoundPreference();
        this.highestSpeedLevel = 60;
    }

    /**
     * Loads sound preference from localStorage
     * @returns {boolean} Whether sound is enabled
     */
    loadSoundPreference() {
        const savedSoundState = localStorage.getItem('soundEnabled');
        return savedSoundState !== null ? savedSoundState === 'true' : true;
    }

    /**
     * Resets the game state to initial values
     */
    reset() {
        this.gameId = null;
        this.questionNumber = 0;
        this.score = 0;
        this.lives = 3;
        this.currentQuestion = null;
        this.isGameActive = false;
        this.isInTransition = false;
        this.highestSpeedLevel = 60;
    }

    /**
     * Updates game state when starting a new game
     * @param {string} gameId - The ID of the new game
     */
    initializeGame(gameId) {
        this.reset();
        this.gameId = gameId;
        this.isGameActive = true;
    }

    /**
     * Updates state for a new question
     * @param {Object} questionData - The new question data
     */
    setCurrentQuestion(questionData) {
        this.currentQuestion = questionData;
        this.questionNumber++;
    }

    /**
     * Updates score and returns if it's a new high score
     * @param {number} newScore - The new score to set
     * @returns {boolean} Whether this is a new high score
     */
    updateScore(newScore) {
        const previousScore = this.score;
        this.score = newScore;
        return this.score > previousScore;
    }

    /**
     * Updates lives and returns if game should end
     * @param {number} newLives - The new number of lives
     * @returns {boolean} Whether the game should end due to no lives
     */
    updateLives(newLives) {
        this.lives = newLives;
        return this.lives <= 0;
    }

    /**
     * Calculates time limit based on current score
     * @returns {Object} Contains new time limit and whether difficulty changed
     */
    getQuestionTimeLimit() {
        const scoreGroup = Math.floor(this.score / 3);
        const previousScoreGroup = Math.floor((this.score - 1) / 3);
        const getTimeLimit = (group) => {
            switch (group) {
                case 0: return 60;  // Questions 1-3
                case 1: return 50;  // Questions 4-6
                case 2: return 40;  // Questions 7-9
                case 3: return 30;  // Questions 10-12
                case 4: return 25;  // Questions 13-15
                case 5: return 20;  // Questions 16-18
                case 6: return 15;  // Questions 19-21
                case 7: return 10;  // Questions 22-24
                case 8: return 9;   // Questions 25-27
                case 9: return 8;   // Questions 28-30
                case 10: return 7;  // Questions 31-33
                case 11: return 6;  // Questions 34-36
                default: return 5;  // Questions 37+
            }
        };
        const oldTimeLimit = getTimeLimit(previousScoreGroup);
        const newTimeLimit = getTimeLimit(scoreGroup);
        
        // Update highest speed level
        this.highestSpeedLevel = Math.min(this.highestSpeedLevel, newTimeLimit);
        
        return {
            timeLimit: newTimeLimit,
            oldTimeLimit: oldTimeLimit,
            difficultyChanged: scoreGroup !== previousScoreGroup && this.score > 1
        };
    }
    /**
     * Toggles sound setting and saves preference
     * @returns {boolean} New sound state
     */
    toggleSound() {
        this.soundEnabled = !this.soundEnabled;
        localStorage.setItem('soundEnabled', this.soundEnabled);
        return this.soundEnabled;
    }

    /**
     * Updates fullscreen state
     * @param {boolean} isFullscreen - New fullscreen state
     */
    setFullscreen(isFullscreen) {
        this.isFullscreen = isFullscreen;
    }
}