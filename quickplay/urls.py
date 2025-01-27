from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    quickplay_home,
    quickplay_game,
    quickplay_results,
    start_game,
    get_question,
    submit_answer,
    end_game,
)
from .api import QuestionViewSet  # Import directly from root api.py

app_name = 'quickplay'

# Create a router for ViewSet
router = DefaultRouter()
router.register(r'ai-questions', QuestionViewSet, basename='ai_question')

urlpatterns = [
    # Main game views
    path('', quickplay_home, name='home'),
    path('game/', quickplay_game, name='game'),
    path('anonymous-results/', quickplay_results, name='anonymous_results'),
    path('results/<str:game_id>/', quickplay_results, name='results'),
    
    # Traditional game API endpoints
    path('api/start-game/', start_game, name='start_game'),
    path('api/get-question/', get_question, name='get_question'),
    path('api/submit-answer/', submit_answer, name='submit_answer'),
    path('api/end-game/<str:game_id>/', end_game, name='end_game'),
    
    # AI Question endpoints
    path('api/v1/', include(router.urls)),
]