from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from django.http import JsonResponse
from .forms import MinduelUserCreationForm, MinduelLoginForm

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
            
            # Handle AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Welcome back, {user.username}!'
                })
            
            # Handle regular form submission
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
        else:
            # Handle invalid form
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
    
    # If it's an AJAX request and we reached here, return error
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': False,
            'error': 'Invalid request'
        })
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def profile_view(request):
    # Get user's game history and statistics
    game_history = request.user.quickplaygame_set.all().order_by('-start_time')[:5]
    total_games = request.user.quickplaygame_set.count()
    avg_score = request.user.quickplaygame_set.filter(is_completed=True).aggregate(
        Avg('score'))['score__avg'] or 0
    
    context = {
        'game_history': game_history,
        'total_games': total_games,
        'avg_score': round(avg_score, 2),
    }
    return render(request, 'accounts/profile.html', context)