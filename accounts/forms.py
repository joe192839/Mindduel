from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import MinduelUser

class MinduelUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = MinduelUser
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()

    def _style_fields(self):
        # Common Tailwind classes for form fields
        field_classes = "appearance-none rounded relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
        
        for field in self.fields.values():
            field.widget.attrs['class'] = field_classes

class MinduelLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()

    def _style_fields(self):
        field_classes = "appearance-none rounded relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
        
        for field in self.fields.values():
            field.widget.attrs['class'] = field_classes