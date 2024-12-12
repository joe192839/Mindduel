# forms.py
from django import forms
from .models import QuestionType

class PracticeSetupForm(forms.Form):
    question_types = forms.ModelMultipleChoiceField(
        queryset=QuestionType.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox h-4 w-4 text-blue-600'}),
        required=True
    )
    number_of_questions = forms.IntegerField(
        min_value=5,
        max_value=50,
        initial=10,
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
            'min': '5',
            'max': '50'
        })
    )
    time_limit = forms.IntegerField(
        min_value=5,
        max_value=120,
        initial=30,
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
            'min': '5',
            'max': '120'
        })
    )