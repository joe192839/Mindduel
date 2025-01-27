# quickplay/management/commands/generate_questions.py
from django.core.management.base import BaseCommand
from quickplay.services import QuestionGeneratorService

class Command(BaseCommand):
    help = 'Generate AI questions for the question bank'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Number of questions to generate')
        parser.add_argument('--category', type=str, help='Category of questions to generate', required=False)
        parser.add_argument('--difficulty', type=str, help='Difficulty level of questions', required=False)

    def handle(self, *args, **options):
        service = QuestionGeneratorService()
        count = options['count']
        category = options.get('category')
        difficulty = options.get('difficulty')

        self.stdout.write(f'Generating {count} questions...')

        for i in range(count):
            try:
                question = service.generate_question(category=category, difficulty=difficulty)
                if question:
                    self.stdout.write(
                        self.style.SUCCESS(f'Generated question {i+1}/{count}: {question.question_text[:50]}...')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Failed to generate question {i+1}/{count}')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error generating question {i+1}/{count}: {str(e)}')
                )

        self.stdout.write(self.style.SUCCESS('Question generation completed!'))