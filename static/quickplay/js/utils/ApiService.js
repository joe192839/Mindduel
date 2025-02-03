/**
 * Handles all API communications for the game
 */
export class ApiService {
    constructor(urls) {
        this.urls = urls;
        this.useAIQuestions = false; // Flag to toggle between regular and AI questions
        this.interactionData = {
            startTime: null,
            hoverPatterns: [],
            clickPatterns: [],
            timeToFirstInteraction: null
        };
    }

    setUseAIQuestions(useAI) {
        this.useAIQuestions = useAI;
    }

    getCsrfToken() {
        return window.CSRF_TOKEN ||
            document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
            this.getCookie('csrftoken');
    }

    getCookie(name) {
        if (!document.cookie) {
            return null;
        }
        const xsrfCookies = document.cookie.split(';')
            .map(c => c.trim())
            .filter(c => c.startsWith(name + '='));
        if (xsrfCookies.length === 0) {
            return null;
        }
        return decodeURIComponent(xsrfCookies[0].split('=')[1]);
    }

    getSelectedCategories() {
        const storedCategories = sessionStorage.getItem('selectedCategories');
        try {
            return storedCategories ? JSON.parse(storedCategories) : [];
        } catch (e) {
            console.error('Error parsing stored categories:', e);
            return [];
        }
    }

    // New method to collect device information
    getDeviceInfo() {
        return {
            screenSize: `${window.innerWidth}x${window.innerHeight}`,
            platform: navigator.platform,
            userAgent: navigator.userAgent,
            connectionType: navigator.connection?.effectiveType || 'unknown',
            language: navigator.language,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        };
    }

    // New method to track user interactions
    startInteractionTracking() {
        this.interactionData.startTime = Date.now();
        this.interactionData.hoverPatterns = [];
        this.interactionData.clickPatterns = [];
        this.interactionData.timeToFirstInteraction = null;
    }

    // New method to record hover patterns
    recordHover(elementId, timestamp) {
        this.interactionData.hoverPatterns.push({
            elementId,
            timestamp,
            timeSinceStart: timestamp - this.interactionData.startTime
        });
    }

    // New method to record click patterns
    recordClick(elementId, timestamp) {
        if (!this.interactionData.timeToFirstInteraction) {
            this.interactionData.timeToFirstInteraction = timestamp - this.interactionData.startTime;
        }
        this.interactionData.clickPatterns.push({
            elementId,
            timestamp,
            timeSinceStart: timestamp - this.interactionData.startTime
        });
    }

    async startGame() {
        const csrfToken = this.getCsrfToken();
        if (!csrfToken) {
            throw new Error('CSRF token not found');
        }

        // Get categories from sessionStorage
        const selectedCategories = this.getSelectedCategories();
        console.log('Starting game with categories:', selectedCategories);

        // Create form data and append categories as a proper string
        const formData = new FormData();
        
        // Convert categories array to match backend format
        const categoryData = selectedCategories.map(category => 
            category.toLowerCase().replace(' ', '_')
        );
        
        formData.append('selected_categories', JSON.stringify(categoryData));
        formData.append('device_info', JSON.stringify(this.getDeviceInfo()));

        const response = await fetch(this.urls.startGame, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            credentials: 'include',
            mode: 'same-origin',
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Server response:', errorText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (!data || !data.game_id) {
            throw new Error('Invalid response from server');
        }

        // Start tracking interactions for the new game
        this.startInteractionTracking();
        return data;
    }

    async loadQuestion(gameId) {
        if (this.useAIQuestions) {
            try {
                const response = await fetch('/api/questions/generate/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.getCsrfToken(),
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ game_id: gameId }),
                    credentials: 'same-origin',
                    mode: 'same-origin'
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                
                if (data.status === 'success' && data.question) {
                    // Transform AI question to match your existing format
                    return {
                        id: data.question.id,
                        question_text: data.question.text,
                        option_1: data.question.answers[0],
                        option_2: data.question.answers[1],
                        option_3: data.question.answers[2],
                        option_4: data.question.answers[3],
                        correct_answer: data.question.correct_answer,
                        category: data.question.category || 'logical_reasoning',
                        is_ai_generated: true
                    };
                } else {
                    throw new Error('Invalid AI question response format');
                }
            } catch (error) {
                console.error('AI Question Error:', error);
                // Fallback to regular questions if AI fails
                this.useAIQuestions = false;
                return this.loadQuestion(gameId);
            }
        }

        // Reset interaction tracking for new question
        this.startInteractionTracking();

        const response = await fetch(`${this.urls.getQuestion}?game_id=${gameId}`, {
            credentials: 'same-origin',
            mode: 'same-origin'
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }

    async submitAnswer(gameId, answer, questionId, confidenceLevel = 3) {
        const csrfToken = this.getCsrfToken();
        if (!csrfToken) {
            throw new Error('CSRF token not found');
        }

        const formData = new FormData();
        formData.append('game_id', gameId);
        formData.append('answer', answer);
        formData.append('question_id', questionId);

        // Add analytics data
        const responseTime = (Date.now() - this.interactionData.startTime) / 1000; // Convert to seconds
        formData.append('response_time', responseTime);
        formData.append('confidence_level', confidenceLevel);
        formData.append('time_to_first_interaction', this.interactionData.timeToFirstInteraction);
        formData.append('interaction_data', JSON.stringify({
            hover_patterns: this.interactionData.hoverPatterns,
            click_patterns: this.interactionData.clickPatterns
        }));

        const response = await fetch(this.urls.submitAnswer, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            credentials: 'same-origin',
            mode: 'same-origin',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }

    async endGame(gameId, reason, score, lives, highestSpeedLevel) {
        const csrfToken = this.getCsrfToken();
        if (!csrfToken) {
            throw new Error('CSRF token not found');
        }

        const url = this.urls.endGame + (gameId !== 'anonymous' ? gameId + '/' : '');
        
        // Calculate total game duration
        const sessionDuration = (Date.now() - this.interactionData.startTime) / 1000; // Convert to seconds

        const payload = {
            reason,
            score,
            lives,
            highest_speed_level: highestSpeedLevel,
            used_ai_questions: this.useAIQuestions,
            // Enhanced analytics data
            session_duration: sessionDuration,
            device_info: this.getDeviceInfo(),
            interaction_summary: {
                total_hovers: this.interactionData.hoverPatterns.length,
                total_clicks: this.interactionData.clickPatterns.length,
                avg_time_to_interact: this.calculateAverageInteractionTime()
            },
            performance_metrics: {
                browser_memory: performance.memory ? {
                    jsHeapSizeLimit: performance.memory.jsHeapSizeLimit,
                    totalJSHeapSize: performance.memory.totalJSHeapSize,
                    usedJSHeapSize: performance.memory.usedJSHeapSize
                } : null,
                navigation_timing: this.getNavigationTiming()
            }
        };

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin',
            mode: 'same-origin',
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }

    // Helper method to calculate average interaction time
    calculateAverageInteractionTime() {
        const allInteractions = [
            ...this.interactionData.hoverPatterns,
            ...this.interactionData.clickPatterns
        ].sort((a, b) => a.timeSinceStart - b.timeSinceStart);

        if (allInteractions.length <= 1) return 0;

        let totalGap = 0;
        for (let i = 1; i < allInteractions.length; i++) {
            totalGap += allInteractions[i].timeSinceStart - allInteractions[i-1].timeSinceStart;
        }

        return totalGap / (allInteractions.length - 1);
    }

    // Helper method to get navigation timing data
    getNavigationTiming() {
        if (!performance || !performance.timing) return null;

        const timing = performance.timing;
        return {
            pageLoadTime: timing.loadEventEnd - timing.navigationStart,
            domReadyTime: timing.domComplete - timing.domLoading,
            networkLatency: timing.responseEnd - timing.fetchStart
        };
    }
}