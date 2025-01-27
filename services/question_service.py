from django.core.cache import cache
from datetime import datetime, timedelta
import uuid
from .openai_service import OpenAIService
import logging

logger = logging.getLogger(__name__)

class QuestionService:
    """
    Service class for managing question generation, caching, and validation.
    This class coordinates between the OpenAI service and our application,
    ensuring questions meet our format and quality requirements.
    """
    
    def __init__(self):
        """Initialize the service with OpenAI integration."""
        self.openai_service = OpenAIService()

    def generate_question(self):
        """
        Generate a new question using OpenAI and format it for our application.
        This method handles the complete flow from generation to validation.
        """
        try:
            # First, we get the raw question from OpenAI
            raw_question = self.openai_service.generate_question()
            
            # Check if we successfully got a question
            if not raw_question:
                logger.warning("Failed to generate raw question from OpenAI")
                return None

            # Generate a unique identifier for this question
            question_id = str(uuid.uuid4())

            # Format the question with all necessary metadata
            formatted_question = {
                'id': question_id,
                'question': raw_question['question'],
                'options': raw_question['options'],
                'correct_answer': raw_question['correct_answer'],
                'explanation': raw_question['explanation'],
                'created_at': datetime.now().isoformat(),
                'metadata': {
                    'difficulty': self._calculate_difficulty(raw_question),
                    'category': 'logical_reasoning',
                    'source': 'openai'
                }
            }

            # Store the question in cache for future retrieval
            cache.set(
                f"question_{question_id}", 
                formatted_question,
                timeout=3600  # Cache for 1 hour
            )

            return formatted_question

        except Exception as e:
            logger.error(f"Error in generate_question: {e}")
            return None

    def _calculate_difficulty(self, question):
        """
        Calculate question difficulty based on content length and complexity.
        Returns one of: 'easy', 'medium', or 'hard'
        """
        question_length = len(question['question'])
        explanation_length = len(question['explanation'])
        
        # Assign difficulty based on content length
        if question_length < 50 and explanation_length < 100:
            return 'easy'
        elif question_length > 100 or explanation_length > 150:
            return 'hard'
        return 'medium'

    def get_or_generate_question(self, question_id=None):
        """
        Retrieve an existing question or generate a new one.
        This is the main method that should be called by API endpoints.
        """
        if question_id:
            cached_question = self._get_cached_question(question_id)
            if cached_question:
                return cached_question
        return self.generate_question()

    def _get_cached_question(self, question_id):
        """
        Retrieve a cached question by ID.
        Returns None if the question isn't found in cache.
        """
        return cache.get(f"question_{question_id}")

    def _format_question(self, response):
        """
        Format a raw question response into our standardized structure.
        Includes validation to ensure the question meets our requirements.
        """
        if not response:
            return None
            
        formatted_question = {
            'id': str(uuid.uuid4()),
            'question': response['question'],
            'options': response['options'],
            'correct_answer': response['correct_answer'],
            'explanation': response['explanation'],
            'metadata': {
                'difficulty': self._calculate_difficulty(response),
                'category': 'logical_reasoning',
                'created_at': datetime.now().isoformat(),
                'source': 'openai',
                'version': '1.0'
            },
            'stats': {
                'times_used': 0,
                'correct_answers': 0,
                'incorrect_answers': 0
            }
        }

        # Validate before returning
        if self._validate_question(formatted_question):
            return formatted_question
        return None

    def _validate_question(self, question):
        """
        Comprehensive validation of question structure and content.
        Ensures all required fields are present and content meets our requirements.
        """
        try:
            # Verify all required fields are present
            required_fields = ['id', 'question', 'options', 'correct_answer', 'explanation']
            if not all(field in question for field in required_fields):
                logger.warning("Question missing required fields")
                return False

            # Validate question length
            if len(question['question']) > 150:
                logger.warning("Question text exceeds maximum length")
                return False

            # Validate options
            if len(question['options']) != 4:
                logger.warning("Question does not have exactly 4 options")
                return False
            if any(len(option) > 25 for option in question['options']):
                logger.warning("One or more options exceed maximum length")
                return False

            # Validate correct answer is in options
            if question['correct_answer'] not in question['options']:
                logger.warning("Correct answer not found in options")
                return False

            # Validate explanation length
            if len(question['explanation']) > 200:
                logger.warning("Explanation exceeds maximum length")
                return False

            return True
            
        except Exception as e:
            logger.error(f"Error validating question: {e}")
            return False