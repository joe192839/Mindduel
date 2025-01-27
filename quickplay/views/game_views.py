from django.shortcuts import render
from django.http import JsonResponse
import uuid
import json
from django.core.cache import cache
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def quickplay_home(request):
    """View for the quickplay home page"""
    return render(request, 'quickplay/home.html')

def quickplay_game(request):
    """View for the game interface"""
    return render(request, 'quickplay/game.html')

def quickplay_results(request, game_id=None):
    """View for displaying game results"""
    context = {'game_id': game_id} if game_id else {}
    return render(request, 'quickplay/results.html', context)

def start_game(request):
    """API endpoint to start a new game.
    Initializes a new game session with default settings."""
    try:
        # Generate a unique game ID
        game_id = str(uuid.uuid4())
        
        # Create initial game state
        game_state = {
            'game_id': game_id,
            'start_time': datetime.now().isoformat(),
            'questions_answered': 0,
            'correct_answers': 0,
            'current_score': 0,
            'is_completed': False
        }
        
        # Store game state in cache
        cache.set(f"game_{game_id}", game_state, timeout=3600)  # 1 hour timeout
        
        return JsonResponse({
            'status': 'success',
            'game_id': game_id,
            'message': 'Game session started successfully'
        })
        
    except Exception as e:
        logger.error(f"Error starting game: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Failed to start game session'
        }, status=500)

def get_question(request):
    """API endpoint to get the next question.
    Returns a new question based on the game state."""
    try:
        game_id = request.GET.get('game_id')
        if not game_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Game ID is required'
            }, status=400)
            
        # Get game state
        game_state = cache.get(f"game_{game_id}")
        if not game_state:
            return JsonResponse({
                'status': 'error',
                'message': 'Game session not found'
            }, status=404)
            
        # Get a new question (you'll need to implement question generation logic)
        question = {
            'question': 'Sample question text',
            'options': ['Option A', 'Option B', 'Option C', 'Option D'],
            'question_id': str(uuid.uuid4())
        }
        
        return JsonResponse({
            'status': 'success',
            'game_id': game_id,
            'question': question
        })
        
    except Exception as e:
        logger.error(f"Error getting question: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Failed to get question'
        }, status=500)

def submit_answer(request):
    """API endpoint to submit an answer.
    Processes the answer and updates game state."""
    try:
        # Extract data from request
        data = json.loads(request.body)
        game_id = data.get('game_id')
        question_id = data.get('question_id')
        answer = data.get('answer')
        
        if not all([game_id, question_id, answer]):
            return JsonResponse({
                'status': 'error',
                'message': 'Missing required fields'
            }, status=400)
            
        # Get game state
        game_state = cache.get(f"game_{game_id}")
        if not game_state:
            return JsonResponse({
                'status': 'error',
                'message': 'Game session not found'
            }, status=404)
            
        # Process answer (implement your answer checking logic)
        is_correct = True  # Replace with actual answer validation
        points = 10 if is_correct else 0
        
        # Update game state
        game_state['questions_answered'] += 1
        game_state['correct_answers'] += 1 if is_correct else 0
        game_state['current_score'] += points
        
        # Save updated game state
        cache.set(f"game_{game_id}", game_state, timeout=3600)
        
        return JsonResponse({
            'status': 'success',
            'is_correct': is_correct,
            'points_earned': points,
            'current_score': game_state['current_score']
        })
        
    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Failed to process answer'
        }, status=500)

def end_game(request, game_id):
    """API endpoint to end the game.
    Finalizes the game session and returns results."""
    try:
        # Get game state
        game_state = cache.get(f"game_{game_id}")
        if not game_state:
            return JsonResponse({
                'status': 'error',
                'message': 'Game session not found'
            }, status=404)
            
        # Calculate final results
        total_time = datetime.now() - datetime.fromisoformat(game_state['start_time'])
        accuracy = (game_state['correct_answers'] / game_state['questions_answered'] * 100 
                   if game_state['questions_answered'] > 0 else 0)
        
        # Create final results
        final_results = {
            'game_id': game_id,
            'total_questions': game_state['questions_answered'],
            'correct_answers': game_state['correct_answers'],
            'final_score': game_state['current_score'],
            'accuracy': round(accuracy, 2),
            'total_time_seconds': round(total_time.total_seconds(), 2)
        }
        
        # Mark game as completed
        game_state['is_completed'] = True
        cache.set(f"game_{game_id}", game_state, timeout=3600)
        
        return JsonResponse({
            'status': 'success',
            'results': final_results
        })
        
    except Exception as e:
        logger.error(f"Error ending game: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Failed to end game session'
        }, status=500)