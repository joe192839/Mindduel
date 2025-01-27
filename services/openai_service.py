from typing import Dict, Optional, Any
import csv
from io import StringIO
import logging
from django.conf import settings
from openai import OpenAI
from django.core.cache import cache
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service class for handling OpenAI API interactions."""
    
    def __init__(self):
        """Initialize the OpenAI client with API key from settings."""
        # We simplify the client initialization to use only the essential parameter
        # This prevents the 'proxies' error while maintaining functionality
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY
        )
        
    def _create_prompt(self) -> str:
        """Create the prompt for question generation."""
        return """Generate a senior high school-level logical reasoning question in csv format.
        Include 4 answer options, the correct answer (being the text of the selected answer),
        and a brief explanation (max 200 letters). Ensure the question is within 150 letters
        and each answer is 25 letters max."""
        
    def _parse_csv_response(self, csv_text: str) -> Optional[Dict[str, Any]]:
        """Parse CSV response into a structured question format."""
        try:
            csv_file = StringIO(csv_text.strip())
            reader = csv.DictReader(csv_file)
            question_data = next(reader)
            
            return {
                'question': question_data.get('question', ''),
                'options': [
                    question_data.get('option_a', ''),
                    question_data.get('option_b', ''),
                    question_data.get('option_c', ''),
                    question_data.get('option_d', ''),
                ],
                'correct_answer': question_data.get('correct_answer', ''),
                'explanation': question_data.get('explanation', '')
            }
        except Exception as e:
            logger.error(f"Error parsing CSV response: {e}")
            return None
            
    def generate_question(self) -> Optional[Dict[str, Any]]:
        """Generate a new question using OpenAI API."""
        try:
            # Check rate limiting
            if not self._check_rate_limit():
                logger.warning("Rate limit exceeded")
                return None
                
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional question generator."},
                    {"role": "user", "content": self._create_prompt()}
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                presence_penalty=settings.OPENAI_PRESENCE_PENALTY,
                frequency_penalty=settings.OPENAI_FREQUENCY_PENALTY,
                top_p=settings.OPENAI_TOP_P,
                stop=settings.OPENAI_STOP
            )
            
            # Parse the response
            csv_response = response.choices[0].message.content
            return self._parse_csv_response(csv_response)
            
        except Exception as e:
            logger.error(f"Error generating question: {e}")
            return None
            
    def _check_rate_limit(self) -> bool:
        """
        Implement rate limiting to prevent API abuse.
        Allows 50 requests per minute.
        """
        RATE_LIMIT_KEY = "openai_rate_limit"
        MAX_REQUESTS = 50
        WINDOW_MINUTES = 1
        
        current_time = datetime.now()
        window_start = current_time - timedelta(minutes=WINDOW_MINUTES)
        
        # Get current request timestamps
        requests = cache.get(RATE_LIMIT_KEY, [])
        requests = [ts for ts in requests if ts > window_start]
        
        if len(requests) >= MAX_REQUESTS:
            return False
            
        requests.append(current_time)
        cache.set(RATE_LIMIT_KEY, requests, timeout=WINDOW_MINUTES * 60)
        return True

    def get_question(self, question_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific question by ID.
        This method can be expanded to fetch from cache or database.
        """
        cache_key = f"question_{question_id}"
        return cache.get(cache_key)