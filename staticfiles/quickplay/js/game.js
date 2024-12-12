// static/quickplay/js/game.js
class QuickplayGame {
    constructor() {
        this.gameId = null;
        this.timeLimit = 300; // 5 minutes in seconds
        this.timer = null;
        this.score = 0;
        this.lives = 3;
        this.currentQuestion = null;
        this.isGameActive = false;
        this.urls = window.QUICKPLAY_URLS;

        // DOM Elements
        this.timerElement = document.getElementById('timer');
        this.scoreElement = document.getElementById('score');
        this.livesElement = document.getElementById('lives');
        this.questionElement = document.getElementById('questionText');
        this.optionsContainer = document.getElementById('options');
        this.startButton = document.getElementById('startButton');
        this.quitButton = document.getElementById('quitButton');
        this.feedbackModal = document.getElementById('feedbackModal');
        this.feedbackTitle = document.getElementById('feedbackTitle');
        this.feedbackText = document.getElementById('feedbackText');
        this.continueButton = document.getElementById('continueButton');

        // Bind event listeners
        this.startButton.addEventListener('click', () => this.startGame());
        this.quitButton.addEventListener('click', () => this.endGame('quit'));
        if (this.continueButton) {
            this.continueButton.addEventListener('click', () => this.hideFeedback());
        }
    }

    async startGame() {
        try {
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
            
            this.startButton.classList.add('hidden');
            this.quitButton.classList.remove('hidden');
            
            this.startTimer();
            this.updateDisplay();
            this.loadQuestion();
        } catch (error) {
            console.error('Failed to start game:', error);
            this.showFeedback('Error', 'Failed to start game. Please try again.');
        }
    }

    startTimer() {
        let timeLeft = this.timeLimit;
        this.timer = setInterval(() => {
            timeLeft--;
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            this.timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
            
            if (timeLeft <= 0) {
                clearInterval(this.timer);
                this.showFeedback('Time\'s Up!', 'Game Over');
                setTimeout(() => this.endGame('timeout'), 1500);
            }
        }, 1000);
    }

    async loadQuestion() {
        try {
            const response = await fetch(`${this.urls.getQuestion}?game_id=${this.gameId}`);
            const data = await response.json();
            
            if (data.status === 'game_over') {
                return this.endGame('complete');
            }
            
            this.currentQuestion = data;
            this.questionElement.textContent = data.question_text;
            
            this.optionsContainer.innerHTML = '';
            const options = [data.option_1, data.option_2, data.option_3, data.option_4];
            
            options.forEach(option => {
                const button = document.createElement('button');
                button.className = 'option-button bg-white text-[#009fdc] font-bold py-3 px-6 rounded hover:bg-gray-100 transition-all duration-300';
                button.textContent = option;
                button.addEventListener('click', () => this.submitAnswer(option, button));
                this.optionsContainer.appendChild(button);
            });
        } catch (error) {
            console.error('Failed to load question:', error);
            this.showError('Failed to load question. Please try again.');
        }
    }

    async submitAnswer(answer, button) {
        if (!this.isGameActive) return;

        try {
            // Disable all option buttons
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
            
            // Show visual feedback
            button.classList.add(data.correct ? 'correct' : 'incorrect');
            
            // Create feedback overlay
            const overlay = document.createElement('div');
            overlay.className = `feedback-overlay ${data.correct ? 'correct' : 'incorrect'}`;
            overlay.innerHTML = `
                <div class="feedback-icon">${data.correct ? '✨' : '❌'}</div>
                <div class="feedback-text">${data.correct ? 'Correct!' : 'Incorrect'}</div>
                <div class="feedback-score">+${data.correct ? '1' : '0'} points</div>
            `;
            
            this.questionElement.parentElement.appendChild(overlay);
            requestAnimationFrame(() => overlay.style.opacity = '1');
            
            // Show score popup if correct
            if (data.correct) {
                const popup = document.createElement('div');
                popup.className = 'score-popup';
                popup.textContent = '+1';
                document.body.appendChild(popup);
                setTimeout(() => popup.remove(), 1000);
            }

            // Update game state
            if (data.correct) {
                this.score++;
            } else {
                this.lives--;
                this.livesElement.classList.add('animate-shake');
                setTimeout(() => this.livesElement.classList.remove('animate-shake'), 500);
            }
            
            this.updateDisplay();
            
            // Wait before next question
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            if (this.lives <= 0) {
                this.endGame();
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
        
        clearInterval(this.timer);
        this.isGameActive = false;

        try {
            if (this.gameId === 'anonymous') {
                window.location.href = this.urls.anonymousResults;
                return;
            }

            const response = await fetch(`${this.urls.endGame}${this.gameId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            });

            const responseText = await response.text();
            let data;
            
            try {
                data = JSON.parse(responseText);
            } catch (e) {
                throw new Error('Invalid response format');
            }

            if (data.redirect) {
                window.location.href = data.redirect;
            } else {
                window.location.href = `${this.urls.results}${this.gameId}/`;
            }
        } catch (error) {
            console.error('Error during end game:', error);
            const errorOverlay = document.createElement('div');
            errorOverlay.className = 'feedback-overlay incorrect';
            errorOverlay.innerHTML = `
                <div class="feedback-icon">⚠️</div>
                <div class="feedback-text">Failed to end game</div>
                <div class="feedback-score">Error: ${error.message}</div>
            `;
            
            this.questionElement.parentElement.appendChild(errorOverlay);
            requestAnimationFrame(() => errorOverlay.style.opacity = '1');

            await new Promise(resolve => setTimeout(resolve, 2000));
            window.location.href = this.gameId === 'anonymous' 
                ? this.urls.anonymousResults
                : `${this.urls.results}${this.gameId}/`;
        }
    }

    updateDisplay() {
        this.scoreElement.textContent = this.score;
        this.livesElement.textContent = '❤️'.repeat(this.lives);
        
        if (this.score > 0 && this.score % 3 === 0) {
            this.timeLimit -= 15;
        }
    }

    showFeedback(title, message) {
        const overlay = document.createElement('div');
        overlay.className = `feedback-overlay ${title === 'Correct!' ? 'correct' : 'incorrect'}`;
        overlay.innerHTML = `
            <div class="feedback-icon">${title === 'Correct!' ? '✨' : '❌'}</div>
            <div class="feedback-text">${title}</div>
            <div class="feedback-score">${message}</div>
        `;
        
        this.questionElement.parentElement.appendChild(overlay);
        requestAnimationFrame(() => overlay.style.opacity = '1');
    }

    showError(message) {
        const overlay = document.createElement('div');
        overlay.className = 'feedback-overlay incorrect';
        overlay.innerHTML = `
            <div class="feedback-icon">⚠️</div>
            <div class="feedback-text">${message}</div>
        `;
        
        this.questionElement.parentElement.appendChild(overlay);
        requestAnimationFrame(() => overlay.style.opacity = '1');
        
        setTimeout(() => overlay.remove(), 3000);
    }

    hideFeedback() {
        if (this.feedbackModal) {
            this.feedbackModal.classList.add('hidden');
        }
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
    new QuickplayGame();
});