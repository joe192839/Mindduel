from django.contrib import admin
from .models import QuickplayQuestion, QuickplayGame, QuickplayAnswer, Leaderboard
from django.urls import path
from django.shortcuts import render, redirect
from django import forms
import csv
import io

class CsvImportForm(forms.Form):
    csv_file = forms.FileField()

@admin.register(QuickplayQuestion)
class QuickplayQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'correct_answer', 'explanation']
    change_list_template = 'admin/quickplay/quickplayquestion/change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path('import-csv/', self.import_csv, name='import_csv'),
        ]
        return new_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            if not csv_file.name.endswith('.csv'):
                self.message_user(request, 'Wrong file format. Please upload a CSV file.')
                return redirect("..")
            
            # First, clear existing questions
            QuickplayQuestion.objects.all().delete()
            
            data_set = csv_file.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            next(io_string)  # Skip the header row
            
            category_mapping = {
                'Logical Reasoning': 'logical_reasoning',
                'Verbal Linguistic': 'verbal_linguistic',
                'Spatial Reasoning': 'spatial_reasoning',
                'Critical Thinking': 'critical_thinking'
            }
            
            created_count = 0
            for row in csv.reader(io_string, delimiter=',', quotechar='"'):
                category = category_mapping.get(row[0].strip(), 'logical_reasoning')
                
                _, created = QuickplayQuestion.objects.get_or_create(
                    question_text=row[1],
                    defaults={
                        'category': category,
                        'option_1': row[2],
                        'option_2': row[3],
                        'option_3': row[4],
                        'option_4': row[5],
                        'correct_answer': row[6],
                        'explanation': row[7],
                        'difficulty': 'medium'
                    }
                )
                if created:
                    created_count += 1
            
            self.message_user(request, f"Successfully imported {created_count} questions")
            return redirect("..")
            
        form = CsvImportForm()
        payload = {"form": form}
        return render(request, "admin/csv_form.html", payload)

        
# Register other models
admin.site.register(QuickplayGame)
admin.site.register(QuickplayAnswer)
admin.site.register(Leaderboard)