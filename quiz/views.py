from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.generic import FormView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.db.models import Avg, Sum, Case, When, IntegerField, F
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth import get_user_model  # Add this import
from collections import defaultdict
import json
from .models import QuestionType, UserPreference, PracticeSession, Question, Choice, PracticeAnswer
from .forms import PracticeSetupForm
import random

# Get the custom user model
User = get_user_model()

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get stats for the homepage with simpler average score calculation
        total_sessions = PracticeSession.objects.filter(is_completed=True)
        if total_sessions.exists():
            correct_answers = PracticeAnswer.objects.filter(is_correct=True).count()
            total_answers = PracticeAnswer.objects.count()
            avg_score = (correct_answers / total_answers * 100) if total_answers > 0 else 0
        else:
            avg_score = 0
        
        context.update({
            'total_users': User.objects.count(),  # Now uses the correct user model
            'questions_answered': PracticeAnswer.objects.count(),
            'practice_sessions': PracticeSession.objects.count(),
            'average_score': round(avg_score, 1)
        })
        return context
    
# Basic views - Added login_required decorator to all function-based views
@login_required
def test_view(request):
    return HttpResponse("Django server is working! This is the test view.")

@login_required
def singleplayer(request):
    return render(request, 'singleplayer.html')

@login_required
def start_game(request):
    if request.method != 'POST':
        return redirect('quiz:singleplayer')
    return HttpResponse("Game starting...")

@login_required
def play_game(request, game_id):
    return HttpResponse(f"Playing game {game_id}")

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get stats for the homepage with simpler average score calculation
        total_sessions = PracticeSession.objects.filter(is_completed=True)
        if total_sessions.exists():
            correct_answers = PracticeAnswer.objects.filter(is_correct=True).count()
            total_answers = PracticeAnswer.objects.count()
            avg_score = (correct_answers / total_answers * 100) if total_answers > 0 else 0
        else:
            avg_score = 0

        # Use User model directly instead of request.user
        from django.contrib.auth.models import User
        
        context.update({
            'total_users': User.objects.count(),  # Changed this line
            'questions_answered': PracticeAnswer.objects.count(),
            'practice_sessions': PracticeSession.objects.count(),
            'average_score': round(avg_score, 1)
        })
        return context
    
# Basic views
def test_view(request):
    return HttpResponse("Django server is working! This is the test view.")

def singleplayer(request):
    return render(request, 'singleplayer.html')

def start_game(request):
    if request.method != 'POST':
        return redirect('quiz:singleplayer')
    # Your existing start_game logic here
    return HttpResponse("Game starting...")

def play_game(request, game_id):
    # Your existing play_game logic here
    return HttpResponse(f"Playing game {game_id}")

class PracticeHomeView(LoginRequiredMixin, FormView):
    template_name = 'practice/home.html'
    form_class = PracticeSetupForm
    login_url = 'login'

    def get_success_url(self):
        return reverse_lazy('quiz:practice_game', kwargs={'session_id': self.practice_session.id})

    def get_initial(self):
        """Pre-fill form with user preferences if they exist"""
        initial = super().get_initial()
        try:
            preferences = UserPreference.objects.get(user=self.request.user)
            initial['question_types'] = preferences.preferred_question_types.all()
            initial['time_limit'] = preferences.preferred_time_limit
            initial['number_of_questions'] = preferences.preferred_question_count
        except UserPreference.DoesNotExist:
            pass
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question_types'] = QuestionType.objects.all()
        context['recent_sessions'] = PracticeSession.objects.filter(
            user=self.request.user,
            is_completed=True
        ).order_by('-created_at')[:5]
        return context

    def form_valid(self, form):
        # Save user preferences
        preferences, created = UserPreference.objects.get_or_create(user=self.request.user)
        preferences.preferred_question_types.set(form.cleaned_data['question_types'])
        preferences.preferred_time_limit = form.cleaned_data['time_limit']
        preferences.preferred_question_count = form.cleaned_data['number_of_questions']
        preferences.save()

        # Create new practice session
        self.practice_session = PracticeSession.objects.create(
            user=self.request.user,
            number_of_questions=form.cleaned_data['number_of_questions'],
            time_limit=form.cleaned_data['time_limit']
        )
        
        # Add selected question types
        self.practice_session.question_types.set(form.cleaned_data['question_types'])
        
        messages.success(self.request, 'Practice session configured successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

class PracticeGameView(LoginRequiredMixin, View):
    template_name = 'practice/game.html'

    def get(self, request, session_id):
        session = get_object_or_404(PracticeSession, id=session_id, user=request.user)
        
        if session.is_completed:
            return redirect('quiz:practice_results', session_id=session_id)
            
        # Get current question
        current_question = self.get_current_question(session)
        if not current_question:
            session.is_completed = True
            session.save()
            return redirect('quiz:practice_results', session_id=session_id)
            
        context = {
            'session': session,
            'question': current_question,
            'choices': current_question.choices.all(),
            'progress': self.get_progress(session),
            'timer': session.time_limit * 60,  # Convert to seconds
        }
        
        return render(request, self.template_name, context)

    def post(self, request, session_id):
        """Handle answer submission"""
        session = get_object_or_404(PracticeSession, id=session_id, user=request.user)
        
        if session.is_completed:
            return JsonResponse({'error': 'Session is already completed'}, status=400)

        try:
            data = json.loads(request.body)
            question_id = data.get('question_id')
            choice_id = data.get('choice_id')
            time_taken = data.get('time_taken')

            # Validate the data
            if not all([question_id, choice_id, time_taken]):
                return JsonResponse({'error': 'Missing required data'}, status=400)

            # Get the question and choice
            question = get_object_or_404(Question, id=question_id)
            choice = get_object_or_404(Choice, id=choice_id, question=question)

            # Create the answer
            answer = PracticeAnswer.objects.create(
                session=session,
                question=question,
                selected_choice=choice,
                time_taken=time_taken
            )

            # Check if this was the last question
            answered_count = session.practiceanswer_set.count()
            if answered_count >= session.number_of_questions:
                session.is_completed = True
                session.completed_at = timezone.now()
                session.save()
                return JsonResponse({
                    'redirect': reverse('quiz:practice_results', kwargs={'session_id': session.id})
                })

            # Get next question
            next_question = self.get_current_question(session)
            if not next_question:
                session.is_completed = True
                session.completed_at = timezone.now()
                session.save()
                return JsonResponse({
                    'redirect': reverse('quiz:practice_results', kwargs={'session_id': session.id})
                })

            # Return next question data
            return JsonResponse({
                'is_correct': answer.is_correct,
                'next_question': {
                    'id': next_question.id,
                    'text': next_question.text,
                    'question_type': next_question.question_type.name,
                    'context': next_question.question_context,
                    'image_url': next_question.image.url if next_question.image else None,
                    'choices': [
                        {
                            'id': choice.id,
                            'text': choice.text
                        } for choice in next_question.choices.all()
                    ]
                },
                'progress': self.get_progress(session)
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def get_current_question(self, session):
        # Get answered question IDs
        answered_questions = session.practiceanswer_set.values_list('question_id', flat=True)
        
        # Get available questions
        available_questions = Question.objects.filter(
            question_type__in=session.question_types.all(),
            is_active=True
        ).exclude(
            id__in=answered_questions
        )
        
        if not available_questions.exists():
            return None
            
        return random.choice(available_questions)

    def get_progress(self, session):
        answered_count = session.practiceanswer_set.count()
        return {
            'current': answered_count + 1,
            'total': session.number_of_questions,
            'percentage': (answered_count / session.number_of_questions) * 100
        }

class PracticeResultsView(LoginRequiredMixin, TemplateView):
    template_name = 'practice/results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_id = self.kwargs['session_id']
        session = get_object_or_404(PracticeSession, id=session_id, user=self.request.user)
        
        # Get all answers for this session with related data
        answers = session.practiceanswer_set.all().select_related(
            'question', 
            'question__question_type', 
            'selected_choice'
        ).prefetch_related('question__choices')

        # Calculate basic statistics
        correct_answers = sum(1 for answer in answers if answer.is_correct)
        total_time = sum(answer.time_taken for answer in answers)
        avg_time = total_time / len(answers) if answers else 0

        # Calculate performance by question type
        type_stats = defaultdict(lambda: {'correct': 0, 'total': 0})
        for answer in answers:
            q_type = answer.question.question_type
            type_stats[q_type]['total'] += 1
            if answer.is_correct:
                type_stats[q_type]['correct'] += 1

        question_type_stats = [
            {
                'name': q_type.name,
                'correct': stats['correct'],
                'total': stats['total'],
                'percentage': (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            }
            for q_type, stats in type_stats.items()
        ]

        # Calculate performance by difficulty
        diff_stats = defaultdict(lambda: {'correct': 0, 'total': 0})
        for answer in answers:
            difficulty = answer.question.get_difficulty_display()
            diff_stats[difficulty]['total'] += 1
            if answer.is_correct:
                diff_stats[difficulty]['correct'] += 1

        difficulty_stats = {
            diff: {
                'correct': stats['correct'],
                'total': stats['total'],
                'percentage': (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            }
            for diff, stats in diff_stats.items()
        }

        # Performance trends
        answer_sequence = []
        running_score = 0
        for i, answer in enumerate(answers, 1):
            if answer.is_correct:
                running_score += 1
            answer_sequence.append({
                'question_number': i,
                'running_accuracy': (running_score / i) * 100,
                'time_taken': answer.time_taken
            })

        context.update({
            'session': session,
            'answers': answers,
            'correct_answers': correct_answers,
            'total_time': total_time,
            'avg_time': avg_time,
            'question_type_stats': question_type_stats,
            'difficulty_stats': difficulty_stats,
            'answer_sequence': answer_sequence,
            'total_questions': len(answers),
            'accuracy_percentage': (correct_answers / len(answers) * 100) if answers else 0
        })

        # Add recommendations based on performance
        recommendations = self.generate_recommendations(
            question_type_stats,
            difficulty_stats,
            answer_sequence
        )
        context['recommendations'] = recommendations

        return context

    def generate_recommendations(self, type_stats, difficulty_stats, answer_sequence):
        recommendations = []

        # Identify weakest question types
        weak_types = [
            stat for stat in type_stats 
            if stat['percentage'] < 70
        ]
        if weak_types:
            recommendations.append({
                'category': 'Question Types',
                'message': f"Focus on improving {', '.join(t['name'] for t in weak_types)}",
                'priority': 'high' if any(t['percentage'] < 50 for t in weak_types) else 'medium'
            })

        # Time management recommendations
        slow_answers = [seq for seq in answer_sequence if seq['time_taken'] > 60]  # More than 60 seconds
        if len(slow_answers) > len(answer_sequence) * 0.3:  # More than 30% slow answers
            recommendations.append({
                'category': 'Time Management',
                'message': "Work on improving your answer speed. Try to spend no more than 60 seconds per question.",
                'priority': 'medium'
            })

        # Difficulty level recommendations
        for diff, stats in difficulty_stats.items():
            if stats['percentage'] < 60:
                recommendations.append({
                    'category': 'Difficulty Levels',
                    'message': f"Practice more {diff.lower()} difficulty questions to improve your performance.",
                    'priority': 'medium'
                })

        return recommendations