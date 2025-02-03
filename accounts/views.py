from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Max, Count, F, ExpressionWrapper, fields
from django.http import JsonResponse
from django.utils import timezone
from django.core.exceptions import FieldError
from datetime import timedelta
from .forms import MinduelUserCreationForm, MinduelLoginForm
from .models import UserPerformanceMetrics
from django_countries import countries
import json


def register_view(request):
    if request.method == 'POST':
        form = MinduelUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = MinduelUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = MinduelLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Welcome back, {user.username}!'
                })
            
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next')
            return redirect(next_url if next_url else 'home')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = dict(form.errors.items())
            return JsonResponse({
                'success': False,
                'error': 'Invalid username or password',
                'errors': errors
            })
        
        messages.error(request, 'Invalid username or password')
    else:
        form = MinduelLoginForm()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': False,
            'error': 'Invalid request'
        })
    
    return redirect('home')

@login_required
def profile_view(request):
    try:
        # Get the game data first and print detailed debug
        game_history = request.user.quickplaygame_set.all().order_by('-start_time')
        total_games = game_history.count()
        completed_games = game_history.filter(is_completed=True)
        completed_count = completed_games.count()
        
        print(f"""
        DETAILED GAME DEBUG:
        Username: {request.user.username}
        Raw Game Count: {request.user.quickplaygame_set.all().count()}
        Total Games in DB: {total_games}
        Completed Games: {completed_count}
        Game History Items: {[{'id': g.id, 'score': g.score, 'completed': g.is_completed} for g in game_history[:5]]}  # Show first 5 games
        Country Code: {request.user.country_code}
        """)

        # Ensure performance metrics exist
        performance_metrics, created = UserPerformanceMetrics.objects.get_or_create(user=request.user)
        if created or (timezone.now() - performance_metrics.updated_at) > timedelta(hours=1):
            UserPerformanceMetrics.update_user_metrics(request.user)
        
        # Calculate level and XP with detailed debug
        current_level = (total_games // 5) + 1
        next_level_threshold = current_level * 5
        level_progress = (total_games % 5) / 5 * 100
        
        print(f"""
        LEVEL CALCULATION DEBUG:
        Total Games Used: {total_games}
        Current Level: {current_level}
        Next Level Threshold: {next_level_threshold}
        Level Progress: {level_progress}%
        Games Needed for Next Level: {next_level_threshold - total_games}
        """)
        
        # Score Statistics from existing games
        avg_score = completed_games.aggregate(Avg('score'))['score__avg'] or 0
        highest_score = completed_games.aggregate(Max('score'))['score__max'] or 0
        wins = completed_games.filter(score__gte=70).count()
        win_rate = (wins / completed_count * 100) if completed_count > 0 else 0

        # Calculate accuracy metrics for each category
        def calculate_category_stats(correct, total):
            if total == 0:
                return 0, 0, 0
            percentage = (correct / total * 100) if total > 0 else 0
            return correct, total, round(percentage, 1)

        # Overview (all categories combined)
        overview_correct = (
            performance_metrics.logical_reasoning_correct +
            performance_metrics.verbal_linguistic_correct +
            performance_metrics.spatial_reasoning_correct +
            performance_metrics.critical_thinking_correct
        )
        overview_total = (
            performance_metrics.logical_reasoning_total +
            performance_metrics.verbal_linguistic_total +
            performance_metrics.spatial_reasoning_total +
            performance_metrics.critical_thinking_total
        )
        overview_correct, overview_total, overview_percentage = calculate_category_stats(
            overview_correct, overview_total
        )

        # Individual category calculations
        logical_correct, logical_total, logical_percentage = calculate_category_stats(
            performance_metrics.logical_reasoning_correct,
            performance_metrics.logical_reasoning_total
        )
        
        verbal_correct, verbal_total, verbal_percentage = calculate_category_stats(
            performance_metrics.verbal_linguistic_correct,
            performance_metrics.verbal_linguistic_total
        )
        
        spatial_correct, spatial_total, spatial_percentage = calculate_category_stats(
            performance_metrics.spatial_reasoning_correct,
            performance_metrics.spatial_reasoning_total
        )
        
        critical_correct, critical_total, critical_percentage = calculate_category_stats(
            performance_metrics.critical_thinking_correct,
            performance_metrics.critical_thinking_total
        )

        # Debug print for metrics
        print("\nDEBUG - Performance Metrics:")
        print(f"Logical: {performance_metrics.logical_reasoning_correct}/{performance_metrics.logical_reasoning_total}")
        print(f"Verbal: {performance_metrics.verbal_linguistic_correct}/{performance_metrics.verbal_linguistic_total}")
        print(f"Spatial: {performance_metrics.spatial_reasoning_correct}/{performance_metrics.spatial_reasoning_total}")
        print(f"Critical: {performance_metrics.critical_thinking_correct}/{performance_metrics.critical_thinking_total}")

        # Debug print for calculations
        print("\nDEBUG - Calculated Percentages:")
        print(f"Overview: {overview_correct}/{overview_total} ({overview_percentage}%)")
        print(f"Logical: {logical_correct}/{logical_total} ({logical_percentage}%)")
        print(f"Verbal: {verbal_correct}/{verbal_total} ({verbal_percentage}%)")
        print(f"Spatial: {spatial_correct}/{spatial_total} ({spatial_percentage}%)")
        print(f"Critical: {critical_correct}/{critical_total} ({critical_percentage}%)")
        
        # Calculate rank based on overall performance
        def calculate_rank(metrics):
            avg_accuracy = (
                metrics.logical_reasoning_accuracy +
                metrics.verbal_linguistic_accuracy +
                metrics.spatial_reasoning_accuracy +
                metrics.critical_thinking_accuracy
            ) / 4
            
            if avg_accuracy >= 90: return 'Grand Master'
            elif avg_accuracy >= 80: return 'Master'
            elif avg_accuracy >= 70: return 'Diamond'
            elif avg_accuracy >= 60: return 'Platinum'
            elif avg_accuracy >= 50: return 'Gold'
            elif avg_accuracy >= 40: return 'Silver'
            else: return 'Bronze'
        
        rank = calculate_rank(performance_metrics)
        print(f"""
        RANK CALCULATION DEBUG:
        Current Rank: {rank}
        Accuracy Components:
            Logical: {performance_metrics.logical_reasoning_accuracy}
            Verbal: {performance_metrics.verbal_linguistic_accuracy}
            Spatial: {performance_metrics.spatial_reasoning_accuracy}
            Critical: {performance_metrics.critical_thinking_accuracy}
        """)
        
        # Chart data
        recent_games = game_history[:10]
        game_dates = [game.start_time.strftime('%Y-%m-%d') for game in recent_games]
        game_scores = [game.score for game in recent_games]
        
        # Category data for radar chart
        categories = [
            'Logical Reasoning',
            'Verbal Linguistic',
            'Spatial Reasoning',
            'Critical Thinking'
        ]
        
        skill_scores = [
            performance_metrics.logical_reasoning_accuracy,
            performance_metrics.verbal_linguistic_accuracy,
            performance_metrics.spatial_reasoning_accuracy,
            performance_metrics.critical_thinking_accuracy
        ]
        
        context = {
            'user': request.user,
            'game_history': recent_games,
            'total_games': total_games,
            'avg_score': round(avg_score, 1),
            'highest_score': highest_score,
            'win_rate': round(win_rate, 1),
            'current_level': current_level,
            'next_level_threshold': next_level_threshold,
            'level_progress': round(level_progress, 1),
            'rank': rank,
            'performance_metrics': performance_metrics,
            'game_dates': json.dumps(game_dates),
            'game_scores': json.dumps(game_scores),
            'categories': json.dumps(categories),
            'skill_scores': json.dumps(skill_scores),
            'overview_correct': overview_correct,
            'overview_total': overview_total,
            'overview_percentage': overview_percentage,
            'logical_correct': logical_correct,
            'logical_total': logical_total,
            'logical_percentage': logical_percentage,
            'verbal_correct': verbal_correct,
            'verbal_total': verbal_total,
            'verbal_percentage': verbal_percentage,
            'spatial_correct': spatial_correct,
            'spatial_total': spatial_total,
            'spatial_percentage': spatial_percentage,
            'critical_correct': critical_correct,
            'critical_total': critical_total,
            'critical_percentage': critical_percentage,
            'countries': list(countries),  
        }
        
        print(f"""
        FINAL CONTEXT DEBUG:
        Total Games: {context['total_games']}
        Level Progress: {context['level_progress']}
        Current Level: {context['current_level']}
        Next Level Threshold: {context['next_level_threshold']}
        """)
        
    except Exception as e:
        print(f"CRITICAL ERROR IN PROFILE VIEW: {str(e)}")
        print(f"Error Type: {type(e)}")
        print(f"Error Location: {e.__traceback__.tb_lineno}")
        messages.error(request, f"An error occurred while loading your profile: {str(e)}")
        context = {
            'error': str(e),
            'user': request.user,
            'total_games': 0,
            'current_level': 1,
            'level_progress': 0,
            'rank': 'Bronze',
            'countries': list(countries) 
        }
    
    return render(request, 'accounts/profile/profile.html', context)

@login_required
def update_profile_photo(request):
    if request.method == 'POST' and request.FILES.get('profile_photo'):
        try:
            request.user.profile_photo = request.FILES['profile_photo']
            request.user.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'No photo provided'}, status=400)

@login_required
def update_country(request):
    if request.method == 'POST':
        country_code = request.POST.get('country_code')
        if country_code and len(country_code) == 2:
            try:
                request.user.country_code = country_code.upper()
                request.user.save()
                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid country code'}, status=400)