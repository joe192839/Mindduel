from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from ..services import QuestionGeneratorService
from ..models import AIQuestion
import json
import logging

logger = logging.getLogger(__name__)

class QuestionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling AI-generated questions.
    Provides endpoints for generating and retrieving questions.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a new AI question based on category and difficulty."""
        try:
            category = request.data.get('category')
            difficulty = request.data.get('difficulty')
            
            service = QuestionGeneratorService()
            question = service.generate_question(category, difficulty)
            
            if question:
                # Update usage statistics
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
            
            return Response(
                {'status': 'error', 'message': 'Failed to generate question'}, 
                status=400
            )
        except Exception as e:
            logger.error(f"Error generating question: {e}")
            return Response(
                {'status': 'error', 'message': str(e)}, 
                status=500
            )

    @action(detail=False, methods=['get'])
    def get_random(self, request):
        """Retrieve a random question based on optional filters."""
        try:
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
        except Exception as e:
            logger.error(f"Error retrieving random question: {e}")
            return Response(
                {'status': 'error', 'message': str(e)}, 
                status=500
            )