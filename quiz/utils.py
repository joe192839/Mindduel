# practice/utils.py
from django.db.models import Avg, Sum, Count
from collections import defaultdict

def calculate_session_analytics(session):
    """Calculate comprehensive analytics for a practice session"""
    responses = session.practiceanswer_set.all().select_related(
        'question',
        'question__question_type',
        'selected_choice'
    )
    
    # Basic statistics
    total_questions = responses.count()
    correct_responses = responses.filter(is_correct=True)
    correct_count = correct_responses.count()
    
    analytics = {
        'total_questions': total_questions,
        'correct_answers': correct_count,
        'score_percentage': (correct_count / total_questions * 100) if total_questions > 0 else 0,
        'average_time': responses.aggregate(avg_time=Avg('time_taken'))['avg_time'],
        'total_time': responses.aggregate(total_time=Sum('time_taken'))['total_time'],
        'performance_by_type': get_performance_by_type(responses),
        'performance_by_difficulty': get_performance_by_difficulty(responses),
        'time_analysis': analyze_time_distribution(responses),
        'improvement_suggestions': generate_suggestions(responses),
        'answer_sequence': generate_answer_sequence(responses)
    }
    
    return analytics

def get_performance_by_type(responses):
    """Calculate performance statistics grouped by question type"""
    type_stats = defaultdict(lambda: {'correct': 0, 'total': 0, 'avg_time': 0})
    
    for response in responses:
        q_type = response.question.question_type
        type_stats[q_type.name]['total'] += 1
        type_stats[q_type.name]['correct'] += 1 if response.is_correct else 0
        type_stats[q_type.name]['avg_time'] = (
            type_stats[q_type.name]['avg_time'] + response.time_taken
        )
    
    # Calculate percentages and average times
    for stats in type_stats.values():
        stats['percentage'] = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        stats['avg_time'] = stats['avg_time'] / stats['total'] if stats['total'] > 0 else 0
    
    return dict(type_stats)

def get_performance_by_difficulty(responses):
    """Calculate performance statistics grouped by difficulty level"""
    diff_stats = defaultdict(lambda: {'correct': 0, 'total': 0, 'avg_time': 0})
    
    for response in responses:
        difficulty = response.question.get_difficulty_display()
        diff_stats[difficulty]['total'] += 1
        diff_stats[difficulty]['correct'] += 1 if response.is_correct else 0
        diff_stats[difficulty]['avg_time'] += response.time_taken
    
    # Calculate percentages and average times
    for stats in diff_stats.values():
        stats['percentage'] = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        stats['avg_time'] = stats['avg_time'] / stats['total'] if stats['total'] > 0 else 0
    
    return dict(diff_stats)

def analyze_time_distribution(responses):
    """Analyze the distribution of time spent on questions"""
    time_data = {
        'fastest_time': float('inf'),
        'slowest_time': 0,
        'time_brackets': defaultdict(int)
    }
    
    for response in responses:
        # Update fastest/slowest times
        time_data['fastest_time'] = min(time_data['fastest_time'], response.time_taken)
        time_data['slowest_time'] = max(time_data['slowest_time'], response.time_taken)
        
        # Categorize into time brackets
        bracket = (response.time_taken // 15) * 15  # Group into 15-second brackets
        time_data['time_brackets'][f"{bracket}-{bracket+15}s"] += 1
    
    time_data['fastest_time'] = min(time_data['fastest_time'], float('inf'))
    
    return time_data

def generate_answer_sequence(responses):
    """Generate a sequence of answers showing progression"""
    sequence = []
    running_score = 0
    
    for i, response in enumerate(responses.order_by('created_at'), 1):
        if response.is_correct:
            running_score += 1
            
        sequence.append({
            'question_number': i,
            'is_correct': response.is_correct,
            'time_taken': response.time_taken,
            'running_accuracy': (running_score / i) * 100,
            'question_type': response.question.question_type.name,
            'difficulty': response.question.get_difficulty_display()
        })
    
    return sequence

def generate_suggestions(responses):
    """Generate improvement suggestions based on performance"""
    suggestions = []
    
    # Analyze performance by type
    type_performance = get_performance_by_type(responses)
    weak_types = [
        type_name for type_name, stats in type_performance.items()
        if stats['percentage'] < 70
    ]
    
    if weak_types:
        suggestions.append({
            'category': 'Question Types',
            'message': f"Focus on improving {', '.join(weak_types)}",
            'priority': 'high' if any(
                stats['percentage'] < 50 
                for stats in type_performance.values()
            ) else 'medium'
        })
    
    # Time management analysis
    avg_time = responses.aggregate(avg=Avg('time_taken'))['avg']
    slow_responses = responses.filter(time_taken__gt=avg_time * 1.5).count()
    if slow_responses > responses.count() * 0.3:
        suggestions.append({
            'category': 'Time Management',
            'message': "Work on improving your answer speed. Try to spend less time on each question.",
            'priority': 'medium'
        })
    
    # Difficulty level analysis
    diff_performance = get_performance_by_difficulty(responses)
    for diff, stats in diff_performance.items():
        if stats['percentage'] < 60:
            suggestions.append({
                'category': 'Difficulty Levels',
                'message': f"Practice more {diff.lower()} difficulty questions to improve your performance.",
                'priority': 'medium'
            })
    
    # Pattern analysis
    sequence = generate_answer_sequence(responses)
    if sequence:
        last_five = sequence[-5:]
        recent_correct = sum(1 for ans in last_five if ans['is_correct'])
        if recent_correct / len(last_five) > 0.8:
            suggestions.append({
                'category': 'Difficulty Progression',
                'message': "Consider trying more challenging questions as you're performing well.",
                'priority': 'low'
            })
    
    return suggestions