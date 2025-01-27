from django.conf import settings
from openai import OpenAI
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import AIQuestion
from .serializers import QuestionSerializer
import json
import logging
import uuid

logger = logging.getLogger(__name__)

class QuestionViewSet(viewsets.ModelViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            logger.info(f"Initializing OpenAI client with API key: {'exists' if settings.OPENAI_API_KEY else 'missing'}")
            logger.info(f"OpenAI Model configured as: {settings.OPENAI_MODEL}")
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            logger.error(f"Exception type: {type(e)}")
            logger.error(f"Exception args: {e.args}")
            raise

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a question using OpenAI"""
        logger.info("Starting question generation")
        max_retries = 3
        
        # Get category from request, default to logical_reasoning if not specified
        category = request.data.get('category', 'logical_reasoning')
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Using OpenAI Model: {settings.OPENAI_MODEL}")
                logger.info("Checking API key configuration")
                if not settings.OPENAI_API_KEY:
                    logger.error("OpenAI API key is not configured")
                    raise ValueError("OpenAI API key is not configured")

                response = self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {
                            "role": "system", 
                            "content": """You are a professional question generator focusing on reasoning questions.
                            You must keep all answer options under 25 characters.
                            The correct_answer MUST exactly match one of the provided options."""
                        },
                        {"role": "user", "content": self._generate_prompt(category)}
                    ],
                    temperature=0.5,
                    max_tokens=int(settings.OPENAI_MAX_TOKENS),
                    presence_penalty=0.1,
                    frequency_penalty=0.1
                )
                
                logger.info(f"OpenAI Response: {response.choices[0].message.content}")
                
                question_data = self._parse_ai_response(response.choices[0].message.content, category)
                logger.info(f"Parsed question data: {question_data}")
                
                serializer = QuestionSerializer(data=question_data)
                
                if serializer.is_valid():
                    question = AIQuestion.objects.create(
                        question_text=question_data['question'],
                        correct_answer=question_data['correct_answer'],
                        wrong_answers=json.dumps(question_data['wrong_answers']),
                        category=question_data['category'],
                        difficulty='medium'
                    )
                    
                    question.last_used = timezone.now()
                    question.times_used += 1
                    question.save()
                    
                    return Response({
                        'status': 'success',
                        'question': {
                            'id': question.id,
                            'text': question.question_text,
                            'category': question.category,
                            'difficulty': question.difficulty,
                            'answers': [question.correct_answer] + json.loads(question.wrong_answers)
                        }
                    })
                else:
                    logger.error(f"Validation failed: {serializer.errors}")
                    if attempt == max_retries - 1:
                        return Response(
                            {"error": "Generated question failed validation", "details": serializer.errors},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )
                    continue

            except Exception as e:
                logger.error(f"Error in generate method (attempt {attempt + 1}): {str(e)}", exc_info=True)
                if attempt == max_retries - 1:
                    return Response(
                        {"error": str(e)}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                continue

    @action(detail=False, methods=['get'])
    def get_random(self, request):
        """Get a random question from the database"""
        category = request.query_params.get('category')
        difficulty = request.query_params.get('difficulty')
        queryset = AIQuestion.objects.all()
        
        if category:
            queryset = queryset.filter(category=category)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
            
        question = queryset.order_by('?').first()
        if question:
            return Response({
                'status': 'success',
                'question': {
                    'id': question.id,
                    'text': question.question_text,
                    'category': question.category,
                    'difficulty': question.difficulty,
                    'answers': [question.correct_answer] + json.loads(question.wrong_answers)
                }
            })
        return Response(
            {'status': 'error', 'message': 'No questions available'}, 
            status=404
        )

    def _generate_prompt(self, category='logical_reasoning'):
        """Create the prompt for OpenAI based on category."""
        base_prompt = """Generate a senior high school-level {category} reasoning question in csv format.

        Required format (CSV):
        question_text,option1,option2,option3,option4,correct_answer,explanation

        STRICT Requirements:
        1. Question must be clear and engaging
        2. CRITICAL: Each option MUST be EXACTLY 25 characters or less (count carefully)
        3. CRITICAL: The correct_answer MUST EXACTLY MATCH one of the four options (option1-option4)
        4. No quotes or special characters in the response
        5. Each field separated by single comma
        6. Question should test {category} thinking
        7. Use simple numbers and short phrases for options
        8. Question must be within 150 letters
        9. Explanation must be within 200 letters"""

        category_map = {
            'logical_reasoning': 'logical',
            'quantitative_reasoning': 'quantitative',
            'linguistic_reasoning': 'linguistic',
            'spatial_reasoning': 'spatial'
        }

        formatted_category = category_map.get(category, 'logical')
        return base_prompt.format(category=formatted_category)

    def _parse_ai_response(self, response_text, category='logical_reasoning'):
        """Parse the AI response into a structured format."""
        try:
            logger.debug(f"Parsing AI response: {response_text}")
            lines = response_text.strip().split('\n')
            if len(lines) < 1:
                raise ValueError("Invalid response format - empty response")

            components = [part.strip() for part in lines[0].split(',')]
            
            if len(components) < 6:
                raise ValueError(f"Missing components in response. Got {len(components)} components: {components}")

            # Get and validate options
            options = []
            for i, option in enumerate(components[1:5]):
                if len(option) > 25:
                    logger.warning(f"Option {i+1} exceeded 25 characters, truncating: {option}")
                    option = option[:25]
                options.append(option)

            # Get correct answer and validate it matches an option
            correct_answer = components[5].strip()
            if correct_answer not in options:
                logger.error(f"Correct answer '{correct_answer}' not in options {options}")
                # Try to find the closest match
                for option in options:
                    if option.lower().strip() == correct_answer.lower().strip():
                        correct_answer = option
                        break
                else:
                    raise ValueError("Correct answer must match one of the options exactly")

            # Calculate wrong answers (all options except the correct one)
            wrong_answers = [opt for opt in options if opt != correct_answer]

            return {
                'id': str(uuid.uuid4()),
                'question': components[0],
                'options': options,
                'correct_answer': correct_answer,
                'wrong_answers': wrong_answers,
                'explanation': components[6] if len(components) > 6 else "",
                'category': category,
                'is_ai_generated': True
            }
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            logger.error(f"Response text: {response_text}")
            raise ValueError(f"Failed to parse AI response: {str(e)}")