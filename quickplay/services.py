# quickplay/services.py
import os
import requests
from anthropic import Anthropic
from .models import AIQuestion

class QuestionGeneratorService:
    def __init__(self):
        self.anthropic = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    def generate_question(self, category=None, difficulty=None):
        prompt = self._build_prompt(category, difficulty)
        
        try:
            response = self.anthropic.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Parse the response and create question
            parsed_question = self._parse_response(response.content)
            return self._save_question(parsed_question)
            
        except Exception as e:
            # Log the error and handle gracefully
            print(f"Error generating question: {e}")
            return None
    
    def _build_prompt(self, category, difficulty):
        return f"""Generate a multiple choice question with the following requirements:
        - Category: {category or 'any'}
        - Difficulty: {difficulty or 'medium'}
        - Include one correct answer and three wrong answers
        - Format the response as JSON with fields: question_text, correct_answer, wrong_answers, category, difficulty
        """

    def _parse_response(self, response):
        # Parse the JSON response from Claude
        try:
            return response.json()
        except:
            raise ValueError("Invalid response format from AI")

    def _save_question(self, parsed_data):
        return AIQuestion.objects.create(
            question_text=parsed_data['question_text'],
            correct_answer=parsed_data['correct_answer'],
            wrong_answers=parsed_data['wrong_answers'],
            category=parsed_data['category'],
            difficulty=parsed_data['difficulty']
        )