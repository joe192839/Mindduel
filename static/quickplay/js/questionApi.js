// static/quickplay/js/questionApi.js
const QuestionApi = {
    getCsrfToken() {
        return window.CSRF_TOKEN ||
            document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
            this.getCookie('csrftoken');
    },

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
    },

    async generateQuestion() {
        try {
            const csrfToken = this.getCsrfToken();
            if (!csrfToken) {
                throw new Error('CSRF token not found');
            }

            const response = await fetch('/quickplay/api/questions/generate/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-CSRFToken': csrfToken
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
            if (!data) {
                throw new Error('Invalid response from server');
            }

            return data;
        } catch (error) {
            console.error('Error generating question:', error);
            throw error;
        }
    },

    async getQuestion(questionId) {
        try {
            const response = await fetch(`/quickplay/api/questions/${questionId}/`, {
                credentials: 'same-origin',
                mode: 'same-origin',
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Server response:', errorText);
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            if (!data) {
                throw new Error('Invalid response from server');
            }

            return data;
        } catch (error) {
            console.error('Error fetching question:', error);
            throw error;
        }
    }
};