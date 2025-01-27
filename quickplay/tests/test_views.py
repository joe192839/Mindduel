from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
import json

User = get_user_model()

class QuickplayViewTests(TestCase):
    """
    Test suite for the main game views and game flow.
    Tests both authenticated and anonymous user scenarios.
    """
    
    def setUp(self):
        """
        Set up test environment before each test.
        Creates a test client and sample user.
        """
        self.client = Client()
        # Create a test user
        self.user = User.objects.create_user(
            username='testplayer',
            email='test@example.com',
            password='testpass123'
        )
        # Store URLs we'll use frequently in tests
        self.home_url = reverse('quickplay:home')
        self.game_url = reverse('quickplay:game')
        self.start_game_url = reverse('quickplay:start_game')
        self.get_question_url = reverse('quickplay:get_question')
        
        # Sample game data for testing
        self.sample_game_id = 'test-game-123'
        self.sample_question = {
            'question': 'Test question?',
            'options': ['A', 'B', 'C', 'D'],
            'correct_answer': 'A'
        }

    def test_home_page_load(self):
        """Test that the home page loads correctly."""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quickplay/home.html')

    def test_game_page_load(self):
        """Test that the game page loads correctly."""
        response = self.client.get(self.game_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quickplay/game.html')

    def test_start_game_endpoint(self):
        """Test the game initialization endpoint."""
        response = self.client.post(self.start_game_url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('game_id', data)

    def test_get_question_endpoint(self):
        """Test retrieving a question during gameplay."""
        # First start a game
        start_response = self.client.post(self.start_game_url)
        game_data = json.loads(start_response.content)
        
        # Then try to get a question
        response = self.client.get(
            self.get_question_url,
            {'game_id': game_data['game_id']}
        )
        self.assertEqual(response.status_code, 200)
        question_data = json.loads(response.content)
        self.assertIn('question', question_data)
        self.assertIn('options', question_data)

    def test_submit_answer_endpoint(self):
        """Test submitting an answer to a question."""
        # Start a game first
        start_response = self.client.post(self.start_game_url)
        game_data = json.loads(start_response.content)
        
        # Submit an answer
        submit_url = reverse('quickplay:submit_answer')
        response = self.client.post(submit_url, {
            'game_id': game_data['game_id'],
            'question_id': '1',
            'answer': 'A'
        })
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertIn('is_correct', result)

    def test_end_game_endpoint(self):
        """Test ending a game and getting results."""
        # Start a game
        start_response = self.client.post(self.start_game_url)
        game_data = json.loads(start_response.content)
        
        # End the game
        end_url = reverse('quickplay:end_game', args=[game_data['game_id']])
        response = self.client.post(end_url)
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertIn('score', result)

    def test_anonymous_results_page(self):
        """Test viewing results for an anonymous game."""
        response = self.client.get(reverse('quickplay:anonymous_results'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quickplay/results.html')

    def test_authenticated_results_page(self):
        """Test viewing results for an authenticated user's game."""
        # Log in the user
        self.client.login(username='testplayer', password='testpass123')
        # View results with a specific game ID
        response = self.client.get(
            reverse('quickplay:results', args=[self.sample_game_id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quickplay/results.html')