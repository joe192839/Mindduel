from django.urls import path
from . import views
app_name = 'quickplay'
urlpatterns = [
# Main views
path('', views.quickplay_home, name='home'), # Changed from home to quickplay_home
path('game/', views.quickplay_game, name='game'), # Changed from game_view to quickplay_game
# API endpoints
path('api/start-game/', views.start_game, name='start_game'),
path('api/get-question/', views.get_question, name='get_question'),
path('api/submit-answer/', views.submit_answer, name='submit_answer'),
path('api/end-game/<str:game_id>/', views.end_game, name='end_game'),
# Results views
path('anonymous-results/', views.quickplay_results, name='anonymous_results'),
path('results/<str:game_id>/', views.quickplay_results, name='results'),
]