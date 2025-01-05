/**
 * Manages all DOM-related operations
 */
export class DOMManager {
    constructor() {
        this.initializeElements();
    }

    initializeElements() {
        // Game elements
        this.timerElement = document.getElementById('timer');
        this.scoreElement = document.getElementById('score');
        this.livesElement = document.getElementById('lives');
        this.questionElement = document.getElementById('questionText');
        this.questionCategory = document.getElementById('questionCategory');
        this.optionsContainer = document.getElementById('options');

        
        // Control buttons
        this.quitButton = document.getElementById('quitButton');
        this.startButton = document.getElementById('startButton');
        this.gameHeader = document.querySelector('.game-header');
        
        // Sound controls
        this.muteButton = document.getElementById('muteButton');
        this.floatingMuteButton = document.getElementById('floatingMuteButton');
        
        // Navigation
        this.navbar = document.querySelector('nav');

        this.verifyCriticalElements();
    }

    verifyCriticalElements() {
        const criticalElements = [
            this.timerElement,
            this.scoreElement,
            this.livesElement,
            this.questionElement,
            this.questionCategory,
            this.optionsContainer
        ];

        if (criticalElements.some(element => !element)) {
            console.error('Critical game elements not found');
            throw new Error('Critical game elements not found');
        }
    }

    displayQuestion(questionData, onAnswerClick) {
        this.questionElement.style.opacity = '0';
        this.questionCategory.style.opacity = '0';
        this.optionsContainer.innerHTML = '';
        
        setTimeout(() => {
            // Display and format category
            if (questionData.category) {
                const categoryMap = {
                    'logical_reasoning': 'Logical Reasoning',
                    'verbal_linguistic': 'Verbal Linguistic',
                    'spatial_reasoning': 'Spatial Reasoning',
                    'critical_thinking': 'Critical Thinking'
                };
                
                const formattedCategory = categoryMap[questionData.category] || questionData.category;
                this.questionCategory.textContent = formattedCategory;
                this.questionCategory.style.opacity = '1';
                this.questionCategory.style.display = 'inline-block';
                
                // Add category-specific styling
                this.questionCategory.className = 'question-category';
                this.questionCategory.classList.add(`category-${questionData.category}`);
            } else {
                this.questionCategory.style.display = 'none';
            }

            this.questionElement.textContent = questionData.question_text;
            this.questionElement.style.opacity = '1';
            
            const options = [
                questionData.option_1, 
                questionData.option_2, 
                questionData.option_3, 
                questionData.option_4
            ];
            
            options.forEach((option, index) => {
                const button = document.createElement('button');
                // Add specific styling for left buttons (index 0 and 2)
                if (index === 0 || index === 2) {
                    button.className = 'option-button bg-white text-[#009fdc] font-bold py-3 px-6 rounded-r hover:bg-gray-100 transition-all duration-300';
                } else {
                    // Right buttons (index 1 and 3)
                    button.className = 'option-button bg-white text-[#009fdc] font-bold py-3 px-6 rounded-l hover:bg-gray-100 transition-all duration-300';
                }
                button.textContent = option;
                button.addEventListener('click', () => onAnswerClick(option, button));
                this.optionsContainer.appendChild(button);
            });
            
            this.optionsContainer.style.opacity = '1';
        }, 100);
    }

    // Other methods remain the same
    updateScore(score) {
        this.scoreElement.textContent = score;
    }

    updateLivesDisplay(lives) {
        this.livesElement.innerHTML = '';
        for (let i = 0; i < lives; i++) {
            const heartImg = document.createElement('img');
            heartImg.src = '/static/images/heart.png';
            heartImg.alt = 'Heart';
            heartImg.style.width = '3rem';
            heartImg.style.height = '3rem';
            heartImg.style.marginRight = i < lives - 1 ? '0.5rem' : '0';
            heartImg.classList.add('heart-icon');
            this.livesElement.appendChild(heartImg);
        }
    }

    updateSoundIcon(soundEnabled) {
        const icon = soundEnabled ? '🔊' : '🔈';
        if (this.muteButton) this.muteButton.textContent = icon;
        if (this.floatingMuteButton) this.floatingMuteButton.textContent = icon;
    }

    setGameHeaderState(active) {
        if (this.gameHeader) {
            this.gameHeader.classList.toggle('active', active);
        }
    }

    updateFullscreenState(isFullscreen) {
        if (isFullscreen) {
            if (this.navbar) {
                this.navbar.style.transition = 'transform 0.5s ease, opacity 0.5s ease';
                this.navbar.style.transform = 'translateY(-100%)';
                this.navbar.style.opacity = '0';
            }
            document.body.style.paddingTop = '1rem';
        } else {
            if (this.navbar) {
                this.navbar.style.transform = 'translateY(0)';
                this.navbar.style.opacity = '1';
            }
            document.body.style.paddingTop = '0';
        }
    }

    disableOptions() {
        const buttons = this.optionsContainer.querySelectorAll('button');
        buttons.forEach(btn => {
            btn.disabled = true;
            const newButton = btn.cloneNode(true);
            btn.parentNode.replaceChild(newButton, btn);
        });
    }

    showError(message) {
        console.error('Game Error:', message);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background-color: #ff4444;
            color: white;
            padding: 1rem;
            border-radius: 4px;
            z-index: 9999;
        `;
        errorDiv.textContent = message;
        document.body.appendChild(errorDiv);
        setTimeout(() => errorDiv.remove(), 5000);
    }
}