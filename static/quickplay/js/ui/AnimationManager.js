/**
 * Manages game animations and transitions
 */
export class AnimationManager {
    /**
     * Initialize AnimationManager with DOMManager instance
     * @param {DOMManager} domManager - Instance of DOMManager
     */
    constructor(domManager) {
        this.domManager = domManager;
    }

    /**
     * Shows brain warmup animation
     * @returns {Promise} Resolves when animation completes
     */
    showBrainWarmup() {
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
                                <svg class="synapse" style="width: 4rem; height: 4rem; transform: rotate(${angle}deg) translateY(-40px)">
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

            // Resolve earlier, during the "GO" phase
            setTimeout(() => {
                resolve();  // Resolve here, at 4 seconds
            }, 4000);

            // Clean up the overlay separately
            setTimeout(() => {
                overlay.style.animation = 'fadeOut 0.5s forwards';
                setTimeout(() => {
                    overlay.remove();
                }, 500);
            }, 5000);
        });
    }

    /**
     * Shows answer feedback overlay
     * @param {boolean} isCorrect - Whether answer was correct
     * @param {number} points - Points earned
     * @returns {Promise} Resolves when animation completes
     */
    showAnswerFeedback(isCorrect, points) {
        return new Promise((resolve) => {
            const overlay = document.createElement('div');
            overlay.className = `feedback-overlay ${isCorrect ? 'correct' : 'incorrect'}`;
            
            const getPointText = (p) => p === 1 ? 'point' : 'points';
            
            overlay.innerHTML = `
                <div class="feedback-icon">${isCorrect ? '✨' : '❌'}</div>
                <div class="feedback-text">${isCorrect ? 'Correct!' : 'Incorrect'}</div>
                <div class="feedback-score">+${points} ${getPointText(points)}</div>
            `;
            
            // Find the question container and append the overlay to it instead of body
            const questionContainer = document.querySelector('.question-container > div');
            questionContainer.appendChild(overlay);
            requestAnimationFrame(() => overlay.style.opacity = '1');
            
            setTimeout(() => {
                overlay.remove();
                resolve();
            }, 1500);
        });
    }
}