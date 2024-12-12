from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views import View
from .models import QuickplayGame, QuickplayQuestion, QuickplayAnswer, Leaderboard
from django.utils import timezone
from django.db.models import Count, Avg
from django.db import DatabaseError
from django.urls import reverse
import random
import logging

logger = logging.getLogger(__name__)

def quickplay_home(request):
    """Home page view showing game instructions and leaderboard."""
    try:
        top_scores = Leaderboard.objects.select_related('player').order_by('-score')[:5]
    except DatabaseError:
        logger.error("Failed to fetch top scores")
        top_scores = []

    context = {'top_scores': top_scores}

    if request.user.is_authenticated:
        try:
            user_best = Leaderboard.objects.filter(player=request.user).order_by('-score').first()
            total_games = QuickplayGame.objects.filter(player=request.user).count()
            avg_score = QuickplayGame.objects.filter(player=request.user).aggregate(Avg('score'))['score__avg']
            
            context.update({
                'user_best': user_best,
                'total_games': total_games,
                'avg_score': avg_score
            })
        except DatabaseError:
            logger.error("Failed to fetch user stats")

    return render(request, 'quickplay/home.html', context)

def quickplay_game(request):
    """Game page view."""
    # Get selected categories from URL parameters
    selected_categories = request.GET.getlist('categories[]', [])
    
    # Store categories in session for later use
    request.session['selected_categories'] = selected_categories
    
    context = {
        'selected_categories': selected_categories
    }
    
    if request.user.is_authenticated:
        try:
            # End any active games for this user
            QuickplayGame.objects.filter(
                player=request.user,
                is_completed=False
            ).update(is_completed=True)
            
            context['user_stats'] = {
                'best_score': Leaderboard.objects.filter(player=request.user)
                    .order_by('-score').first()
            }
        except DatabaseError:
            logger.error("Failed to update game status or fetch user stats")
    
    return render(request, 'quickplay/game.html', context)

def quickplay_results(request, game_id=None):
    """Results page showing game summary."""
    logger.info(f"Accessing results page with game_id: {game_id}")
    context = {}
    
    if request.user.is_authenticated and game_id:
        try:
            game = get_object_or_404(QuickplayGame, id=game_id, player=request.user)
            answers = QuickplayAnswer.objects.filter(game=game)\
                .select_related('question')\
                .order_by('answered_at')
            
            total_answers = answers.count()
            correct_answers = answers.filter(is_correct=True).count()
            accuracy = (correct_answers / total_answers * 100) if total_answers > 0 else 0
            
            try:
                user_rank = Leaderboard.objects.filter(score__gt=game.score).count() + 1
                user_best_score = Leaderboard.objects.filter(player=request.user)\
                    .order_by('-score').first()
                personal_best = user_best_score and game.score == user_best_score.score
            except DatabaseError:
                logger.error("Failed to calculate user rank or personal best")
                user_rank = 1
                personal_best = True

            context.update({
                'game': game,
                'answers': answers,
                'accuracy': accuracy,
                'total_answers': total_answers,
                'correct_answers': correct_answers,
                'top_scores': Leaderboard.objects.order_by('-score')[:10],
                'user_rank': user_rank,
                'personal_best': personal_best
            })
        except Exception as e:
            logger.error(f"Error accessing results: {e}")
            return redirect('quickplay:home')
    else:
        game_state = request.session.get('quickplay_game', {})
        if game_state:
            context.update({
                'score': game_state.get('score', 0),
                'message': 'Log in to save your score and track your progress!'
            })
            del request.session['quickplay_game']
    
    return render(request, 'quickplay/results.html', context)

def start_game(request):
    """API endpoint to start a new game."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        # Get selected categories from session
        selected_categories = request.session.get('selected_categories', [])
        
        if request.user.is_authenticated:
            QuickplayGame.objects.filter(
                player=request.user,
                is_completed=False
            ).update(is_completed=True)
            
            game = QuickplayGame.objects.create(
                player=request.user,
                start_time=timezone.now(),
                time_limit=300,
                categories=','.join(selected_categories) if selected_categories else ''
            )
            logger.info(f"Started new game with ID: {game.id} and categories: {selected_categories}")
            return JsonResponse({'game_id': game.id})
        else:
            game_state = {
                'score': 0,
                'lives': 3,
                'time_limit': 300,
                'start_time': timezone.now().isoformat(),
                'answered_questions': [],
                'categories': selected_categories
            }
            request.session['quickplay_game'] = game_state
            return JsonResponse({'game_id': 'anonymous'})
    except Exception as e:
        logger.error(f"Failed to start game: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def get_question(request):
    """API endpoint to get a new question."""
    selected_categories = request.session.get('selected_categories', [])
    
    if request.user.is_authenticated:
        game_id = request.GET.get('game_id')
        if not game_id:
            return JsonResponse({'error': 'Game ID required'}, status=400)
        
        try:
            game = get_object_or_404(QuickplayGame, id=game_id, player=request.user)
            if game.is_completed:
                return JsonResponse({'status': 'game_over'})
            
            answered_questions = QuickplayAnswer.objects.filter(game=game)\
                .values_list('question_id', flat=True)
        except Exception as e:
            logger.error(f"Error fetching game data: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        game_state = request.session.get('quickplay_game', {})
        if not game_state:
            return JsonResponse({'error': 'No active game'}, status=400)
        answered_questions = game_state.get('answered_questions', [])
    
    try:
        # Filter questions by category if categories are selected
        questions = QuickplayQuestion.objects.exclude(id__in=answered_questions)
        if selected_categories:
            questions = questions.filter(category__in=selected_categories)
            
        if not questions.exists():
            return JsonResponse({'status': 'game_over'})
        
        question = random.choice(list(questions))
        return JsonResponse({
            'id': question.id,
            'question_text': question.question_text,
            'option_1': question.option_1,
            'option_2': question.option_2,
            'option_3': question.option_3,
            'option_4': question.option_4
        })
    except Exception as e:
        logger.error(f"Error getting question: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def submit_answer(request):
    """API endpoint to submit an answer."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    game_id = request.POST.get('game_id')
    answer = request.POST.get('answer')
    question_id = request.POST.get('question_id')
    
    if not all([game_id, answer, question_id]):
        return JsonResponse({'error': 'Missing required fields'}, status=400)
    
    try:
        question = get_object_or_404(QuickplayQuestion, id=question_id)
        is_correct = answer.lower() == question.correct_answer.lower()
        
        if request.user.is_authenticated:
            game = get_object_or_404(QuickplayGame, id=game_id, player=request.user)
            
            if game.is_completed:
                return JsonResponse({'status': 'game_over'})
            
            # Record the answer
            QuickplayAnswer.objects.create(
                game=game,
                question=question,
                user_answer=answer,
                is_correct=is_correct
            )
            
            # Update game stats
            if is_correct:
                game.score += 1
                if game.score % 3 == 0:
                    game.time_limit = max(60, game.time_limit - 15)
            else:
                game.lives_remaining -= 1
                if game.lives_remaining <= 0:
                    game.is_completed = True
                    game.end_time = timezone.now()
                    logger.info(f"Game {game_id} completed due to no lives remaining")
            
            game.save()
            
            return JsonResponse({
                'correct': is_correct,
                'lives': game.lives_remaining,
                'score': game.score,
                'time_limit': game.time_limit,
                'explanation': question.explanation,
                'correct_answer': question.correct_answer
            })
        else:
            # Handle anonymous users
            game_state = request.session.get('quickplay_game', {})
            if not game_state:
                return JsonResponse({'error': 'No active game'}, status=400)
            
            # Update game state
            if is_correct:
                game_state['score'] = game_state.get('score', 0) + 1
            else:
                game_state['lives'] = game_state.get('lives', 3) - 1
            
            # Track answered questions
            answered_questions = game_state.get('answered_questions', [])
            answered_questions.append(question_id)
            game_state['answered_questions'] = answered_questions
            
            request.session['quickplay_game'] = game_state
            
            return JsonResponse({
                'correct': is_correct,
                'lives': game_state['lives'],
                'score': game_state['score'],
                'explanation': question.explanation,
                'correct_answer': question.correct_answer
            })
            
    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def end_game(request, game_id=None):
    """API endpoint to end a game."""
    logger.info(f"End game called with game_id: {game_id}")
    logger.info(f"Request method: {request.method}")
    logger.info(f"User authenticated: {request.user.is_authenticated}")

    if request.user.is_authenticated and game_id:
        try:
            game = get_object_or_404(QuickplayGame, id=game_id, player=request.user)
            logger.info(f"Found game: {game.id}")
            
            if not game.is_completed:
                game.is_completed = True
                game.end_time = timezone.now()
                game.save()
                logger.info("Game marked as completed")
                
                time_taken = (game.end_time - game.start_time).seconds
                try:
                    Leaderboard.objects.create(
                        player=request.user,
                        score=game.score,
                        time_taken=time_taken
                    )
                    logger.info("Created leaderboard entry")
                except DatabaseError as e:
                    logger.error(f"Failed to create leaderboard entry: {e}")
            
            results_url = reverse('quickplay:results', kwargs={'game_id': game_id})
            logger.info(f"Generated results URL: {results_url}")
            
            return JsonResponse({
                'status': 'success',
                'redirect': results_url
            })
            
        except Exception as e:
            logger.error(f"Error in end_game: {e}")
            return JsonResponse({
                'status': 'error',
                'redirect': reverse('quickplay:home')
            })
    else:
        # Handle anonymous users
        game_state = request.session.get('quickplay_game', {})
        if game_state:
            logger.info("Processing anonymous game end")
            results_url = reverse('quickplay:anonymous_results')
            return JsonResponse({
                'status': 'success',
                'redirect': results_url
            })
        
        logger.warning("No active game found")
        return JsonResponse({
            'status': 'error',
            'redirect': reverse('quickplay:home')
        })