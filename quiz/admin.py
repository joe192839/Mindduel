# quiz/admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django import forms
import csv
import io
from .models import QuestionType, Question, Choice, UserPreference, UserAnswer

class CsvImportForm(forms.Form):
    csv_file = forms.FileField()
    question_type = forms.ModelChoiceField(
        queryset=QuestionType.objects.all(),
        help_text="Select the question type for all imported questions"
    )
    difficulty = forms.ChoiceField(
        choices=Question.DIFFICULTY_CHOICES,
        help_text="Select the difficulty level for all imported questions"
    )

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    max_num = 4
    validate_min = True
    min_num = 4

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.validate_min = True
        return formset

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text_preview', 'question_type', 'difficulty', 'usage_count',
                   'success_rate', 'is_active', 'created_at')
    list_filter = ('question_type', 'difficulty', 'is_active', 'created_at')
    search_fields = ('question_context', 'text', 'explanation')
    inlines = [ChoiceInline]
    actions = ['export_questions', 'deactivate_questions', 'activate_questions']
    change_list_template = 'admin/quiz/question_changelist.html'
    
    fieldsets = (
        ('Question Content', {
            'fields': ('question_type', 'difficulty', 'question_context', 'text', 'image')
        }),
        ('Additional Information', {
            'fields': ('explanation', 'is_active')
        }),
        ('Statistics', {
            'fields': ('usage_count', 'average_time', 'success_rate'),
            'classes': ('collapse',)
        })
    )

    def text_preview(self, obj):
        return obj.text[:50] + "..."
    text_preview.short_description = 'Question Text'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('statistics/', self.admin_site.admin_view(self.question_statistics_view),
                 name='question-statistics'),
            path('import-csv/', self.admin_site.admin_view(self.import_csv_view),
                 name='import-csv'),
            path('download-sample-csv/', self.admin_site.admin_view(self.download_sample_csv),
                 name='download-sample-csv'),
        ]
        return custom_urls + urls

    def download_sample_csv(self, request):
        """Provide a sample CSV file format for users"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sample_questions_import.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Question Context', 'Question Text', 'Explanation', 
                        'Choice 1 (Correct)', 'Choice 2', 'Choice 3', 'Choice 4'])
        writer.writerow([
            'In a small village, there were 120 houses. After a new development, the number of houses doubled.', 
            'How many houses are there now in the village?',
            'To find the total, multiply the original number (120) by 2',
            '240', '120', '360', '180'
        ])
        return response

    def import_csv_view(self, request):
        if request.method == 'POST':
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data['csv_file']
                question_type = form.cleaned_data['question_type']
                difficulty = form.cleaned_data['difficulty']
                
                decoded_file = csv_file.read().decode('utf-8')
                csv_data = csv.reader(io.StringIO(decoded_file))
                next(csv_data)  # Skip header row
                
                questions_created = 0
                errors = []

                for row in csv_data:
                    try:
                        if len(row) < 7:  # Updated to account for question_context
                            errors.append(f"Row {questions_created + 1}: Insufficient columns")
                            continue
                            
                        question_context, question_text, explanation, *choices = row
                        
                        question = Question.objects.create(
                            question_type=question_type,
                            question_context=question_context,
                            text=question_text,
                            explanation=explanation,
                            difficulty=difficulty,
                        )
                        
                        for i, choice_text in enumerate(choices[:4]):
                            Choice.objects.create(
                                question=question,
                                text=choice_text,
                                is_correct=(i == 0)
                            )
                        
                        questions_created += 1
                    except Exception as e:
                        errors.append(f"Row {questions_created + 1}: {str(e)}")
                
                if errors:
                    messages.warning(request, f"Imported {questions_created} questions with {len(errors)} errors: {'; '.join(errors)}")
                else:
                    messages.success(request, f"Successfully imported {questions_created} questions")
                
                return redirect('..')
        else:
            form = CsvImportForm()
        
        return render(
            request,
            'admin/quiz/csv_import_form.html',
            {
                'form': form,
                'title': 'Import Questions from CSV',
                'site_header': 'Quiz Administration',
            }
        )

    def question_statistics_view(self, request):
        context = {
            'questions': Question.objects.all(),
            'title': 'Question Statistics'
        }
        return render(request, 'admin/quiz/question_statistics.html', context)

    def export_questions(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="questions.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Question Type', 'Question Context', 'Question Text', 
                        'Difficulty', 'Explanation', 'Usage Count', 'Success Rate'])
        
        for question in queryset:
            writer.writerow([
                question.question_type.name,
                question.question_context,
                question.text,
                question.get_difficulty_display(),
                question.explanation,
                question.usage_count,
                f"{question.success_rate:.2f}%"
            ])
        return response
    export_questions.short_description = "Export selected questions to CSV"

    def deactivate_questions(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_questions.short_description = "Deactivate selected questions"

    def activate_questions(self, request, queryset):
        queryset.update(is_active=True)
    activate_questions.short_description = "Activate selected questions"

@admin.register(QuestionType)
class QuestionTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'question_count', 'average_success_rate')
    search_fields = ('name', 'description')
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Number of Questions'
    
    def average_success_rate(self, obj):
        questions = obj.questions.all()
        if not questions:
            return "N/A"
        avg_rate = sum(q.success_rate for q in questions) / questions.count()
        return f"{avg_rate:.2f}%"
    average_success_rate.short_description = 'Avg Success Rate'

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'preferred_time_limit', 'preferred_question_count')
    search_fields = ('user__username',)
    filter_horizontal = ('preferred_question_types',)

@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'is_correct', 'time_taken', 'created_at')
    list_filter = ('is_correct', 'created_at', 'question__question_type')
    search_fields = ('user__username', 'question__text')
    readonly_fields = ('is_correct', 'time_taken', 'created_at')

    def has_add_permission(self, request):
        return False  # Prevent manual creation of user answers