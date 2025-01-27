from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from services.question_service import QuestionService
import json

class QuestionAPITests(APITestCase):
    """
    Test suite for the Question Generation API endpoints.
    Tests both successful operations and error handling.
    """
    
    def setUp(self):
        """
        Set up the test environment before each test.
        This runs before every test method.
        """
        # Initialize the API client for making requests
        self.client = APIClient()
        
        # Set up the URL endpoints we'll be testing
        self.generate_url = reverse('quickplay:generate_question')
        
        # Define test data that matches our expected API response structure
        self.valid_question_data = {
            'id': 'test-id',
            'question': 'What is the next number in the sequence: 2, 4, 8, 16...?',
            'options': ['32', '24', '20', '28'],
            'correct_answer': '32',
            'explanation': 'The sequence follows a pattern where each number is doubled.'
        }
        
        # Additional test data for specific test cases
        self.invalid_question_data = {
            'question': 'Invalid question without options',
            'correct_answer': 'missing options'
        }
        
        self.question_response_format = {
            'id': 'test-question-1',
            'question': 'Test question?',
            'options': ['A', 'B', 'C', 'D'],
            'correct_answer': 'A',
            'explanation': 'Test explanation'
        }

    def test_generate_question_success(self):
        """
        Test successful question generation.
        Verifies that the API returns a properly formatted question.
        """
        with patch.object(QuestionService, 'get_or_generate_question') as mock_generate:
            mock_generate.return_value = self.valid_question_data
            
            response = self.client.get(self.generate_url)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('question', response.data)
            self.assertIn('options', response.data)
            self.assertEqual(len(response.data['options']), 4)
            self.assertIn('correct_answer', response.data)
            self.assertIn('explanation', response.data)

    def test_generate_question_service_failure(self):
        """
        Test handling of question generation service failure.
        Verifies proper error handling when the service fails.
        """
        with patch.object(QuestionService, 'get_or_generate_question') as mock_generate:
            mock_generate.return_value = None
            
            response = self.client.get(self.generate_url)
            
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertIn('error', response.data)

    def test_generate_question_rate_limit(self):
        """
        Test rate limiting functionality.
        Verifies that users cannot make too many requests too quickly.
        """
        for _ in range(11):  # Our rate limit is 10/minute
            self.client.get(self.generate_url)
            
        response = self.client.get(self.generate_url)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_retrieve_specific_question(self):
        """
        Test retrieval of a specific question by ID.
        Verifies that we can fetch previously generated questions.
        """
        question_id = 'test-id'
        url = reverse('quickplay:get_ai_question', args=[question_id])
        
        with patch.object(QuestionService, 'get_or_generate_question') as mock_get:
            mock_get.return_value = self.valid_question_data
            
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['id'], question_id)
            self.assertIn('question', response.data)
            self.assertIn('options', response.data)
            self.assertEqual(len(response.data['options']), 4)

    def test_invalid_question_data(self):
        """
        Test handling of invalid question data from the service.
        Verifies that malformed questions are caught and handled properly.
        """
        with patch.object(QuestionService, 'get_or_generate_question') as mock_generate:
            mock_generate.return_value = self.invalid_question_data
            
            response = self.client.get(self.generate_url)
            
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertIn('error', response.data)

    def test_question_format_consistency(self):
        """
        Test that the question format remains consistent across different requests.
        Verifies that all required fields are present and properly formatted.
        """
        with patch.object(QuestionService, 'get_or_generate_question') as mock_generate:
            mock_generate.return_value = self.question_response_format
            
            response = self.client.get(self.generate_url)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('id', response.data)
            self.assertIn('question', response.data)
            self.assertIn('options', response.data)
            self.assertIn('correct_answer', response.data)
            self.assertIn('explanation', response.data)
            self.assertEqual(len(response.data['options']), 4)
            