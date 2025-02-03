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
        # Updated Tailwind classes to match the new design
        field_classes = (
            "form-input w-full px-4 py-3 rounded-lg "
            "bg-white bg-opacity-10 border border-white border-opacity-20 "
            "text-white placeholder-white placeholder-opacity-50 "
            "focus:bg-white focus:bg-opacity-15 focus:border-primary-500 "
            "focus:ring-2 focus:ring-primary-500 focus:ring-opacity-20 "
            "transition-all duration-300"
        )
        # Apply custom placeholders and classes
        placeholders = {
            'username': 'Choose a username',
            'email': 'Enter your email',
            'password1': 'Create a password',
            'password2': 'Confirm password'
        }
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = field_classes
            field.widget.attrs['placeholder'] = placeholders.get(field_name, '')
            # Remove default help text for cleaner UI
            field.help_text = None

class MinduelLoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()

    def _style_fields(self):
        # Updated Tailwind classes to match modal design
        field_classes = (
            "w-full px-4 py-3 bg-gray-800 border border-gray-700 "
            "focus:border-[#009fdc] rounded-md text-white placeholder-gray-500 "
            "focus:outline-none focus:ring-2 focus:ring-[#009fdc]/50 transition-colors"
        )

        # Custom styling for checkbox
        checkbox_classes = (
            "form-checkbox rounded border-white border-opacity-20 "
            "bg-white bg-opacity-10 text-primary-500 "
            "focus:ring-primary-500 focus:ring-opacity-20"
        )

        # Apply styling to fields with modal-specific IDs
        self.fields['username'].widget.attrs.update({
            'class': field_classes,
            'placeholder': 'Enter your username',
            'id': 'modal_username'
        })
        
        self.fields['password'].widget.attrs.update({
            'class': field_classes,
            'placeholder': 'Enter your password',
            'id': 'modal_password'
        })
        
        if 'remember_me' in self.fields:
            self.fields['remember_me'].widget.attrs.update({
                'class': checkbox_classes
            })