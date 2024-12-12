# quiz/urls.py
from django.urls import path
from . import views
from .views import PracticeHomeView, HomeView

app_name = 'quiz'

urlpatterns = [
    # Homepage
    path('', HomeView.as_view(), name='home'),
    
    # Your existing URL patterns
    path('test/', views.test_view, name='test'),
    path('singleplayer/', views.singleplayer, name='singleplayer'),
    path('start-game/', views.start_game, name='start_game'),
    path('play-game/<int:game_id>/', views.play_game, name='play_game'),
    
    # Practice mode URLs
    path('practice/', PracticeHomeView.as_view(), name='practice_home'),
    path('practice/game/<int:session_id>/', views.PracticeGameView.as_view(), name='practice_game'),
    path('practice/results/<int:session_id>/', views.PracticeResultsView.as_view(), name='practice_results'),
]