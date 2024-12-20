from django.urls import path
from . import views

app_name = 'quickplay'

urlpatterns = [
    # Main game routes
    path('', views.quickplay_home, name='home'),
    path('game/', views.quickplay_game, name='game'),
    path('results/<int:game_id>/', views.quickplay_results, name='results'),
    path('results/', views.quickplay_results, name='anonymous_results'),

    # API endpoints
    path('api/start-game/', views.start_game, name='start_game'),
    path('api/get-question/', views.get_question, name='get_question'),
    path('api/submit-answer/', views.submit_answer, name='submit_answer'),
    path('api/end-game/<str:game_id>/', views.end_game, name='end_game'),
]