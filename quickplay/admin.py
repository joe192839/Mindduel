# quickplay/admin.py
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
    list_display = ['question_text', 'correct_answer']
    change_list_template = 'admin/quickplay/quickplayquestion/change_list.html'  # Add this line
    
    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path('import-csv/', self.import_csv, name='import_csv'),  # Add name parameter
        ]
        return new_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            
            # Check if it's a CSV file
            if not csv_file.name.endswith('.csv'):
                self.message_user(request, 'Wrong file format. Please upload a CSV file.')
                return redirect("..")
                
            # Read CSV file
            data_set = csv_file.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            next(io_string) # Skip the header row
            
            for row in csv.reader(io_string, delimiter=',', quotechar='"'):
                _, created = QuickplayQuestion.objects.update_or_create(
                    question_text=row[1],
                    defaults={
                        'option_1': row[2],
                        'option_2': row[3],
                        'option_3': row[4],
                        'option_4': row[5],
                        'correct_answer': row[6],
                        'difficulty': 'medium'  # default difficulty
                    }
                )
                    
            self.message_user(request, "Your csv file has been imported")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(request, "admin/csv_form.html", payload)