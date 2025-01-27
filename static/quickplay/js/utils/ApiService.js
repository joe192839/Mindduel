/**
 * Handles all API communications for the game
 */
export class ApiService {
    constructor(urls) {
        this.urls = urls;
        this.useAIQuestions = false; // Flag to toggle between regular and AI questions
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

    async startGame() {
        const csrfToken = this.getCsrfToken();
        if (!csrfToken) {
            throw new Error('CSRF token not found');
        }
        const response = await fetch(this.urls.startGame, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'include',
            mode: 'same-origin'
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

        const response = await fetch(`${this.urls.getQuestion}?game_id=${gameId}`, {
            credentials: 'same-origin',
            mode: 'same-origin'
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }

    async submitAnswer(gameId, answer, questionId) {
        const csrfToken = this.getCsrfToken();
        if (!csrfToken) {
            throw new Error('CSRF token not found');
        }

        const formData = new FormData();
        formData.append('game_id', gameId);
        formData.append('answer', answer);
        formData.append('question_id', questionId);

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
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin',
            mode: 'same-origin',
            body: JSON.stringify({
                reason,
                score,
                lives,
                highest_speed_level: highestSpeedLevel,
                used_ai_questions: this.useAIQuestions
            })
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }
}