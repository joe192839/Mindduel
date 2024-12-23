# Generated by Django 5.1.1 on 2024-11-20 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("quiz", "0002_alter_questiontype_options_question_choice_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="question_context",
            field=models.TextField(
                blank=True,
                help_text="The passage or context that precedes the question (e.g., reading passage, scenario description)",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="question",
            name="text",
            field=models.TextField(help_text="The actual question text"),
        ),
    ]
