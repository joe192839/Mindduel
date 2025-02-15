# Generated by Django 4.2.16 on 2025-01-01 03:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Choice",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.CharField(max_length=200)),
                ("is_correct", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "question_context",
                    models.TextField(
                        blank=True,
                        help_text="The passage or context that precedes the question (e.g., reading passage, scenario description)",
                        null=True,
                    ),
                ),
                ("text", models.TextField(help_text="The actual question text")),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        help_text="Optional image for the question",
                        null=True,
                        upload_to="question_images/",
                    ),
                ),
                (
                    "difficulty",
                    models.IntegerField(
                        choices=[(1, "Easy"), (2, "Medium"), (3, "Hard")], default=1
                    ),
                ),
                (
                    "explanation",
                    models.TextField(help_text="Explanation of the correct answer"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
                ("usage_count", models.IntegerField(default=0)),
                (
                    "average_time",
                    models.FloatField(
                        default=0, help_text="Average time taken to answer in seconds"
                    ),
                ),
                (
                    "success_rate",
                    models.FloatField(
                        default=0, help_text="Percentage of correct answers"
                    ),
                ),
            ],
            options={
                "verbose_name": "Question",
                "verbose_name_plural": "Questions",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="QuestionType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField()),
                (
                    "icon_name",
                    models.CharField(
                        default="academic-cap",
                        help_text="Name of the icon from heroicons",
                        max_length=50,
                    ),
                ),
                (
                    "sample_question",
                    models.TextField(
                        help_text="A sample question to show in the preview card"
                    ),
                ),
            ],
            options={
                "verbose_name": "Question Type",
                "verbose_name_plural": "Question Types",
            },
        ),
        migrations.CreateModel(
            name="UserPreference",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("preferred_time_limit", models.IntegerField(default=30)),
                ("preferred_question_count", models.IntegerField(default=10)),
                (
                    "preferred_question_types",
                    models.ManyToManyField(to="quiz.questiontype"),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserAnswer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_correct", models.BooleanField()),
                (
                    "time_taken",
                    models.FloatField(help_text="Time taken to answer in seconds"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="quiz.question"
                    ),
                ),
                (
                    "selected_choice",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="quiz.choice"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddField(
            model_name="question",
            name="question_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="questions",
                to="quiz.questiontype",
            ),
        ),
        migrations.CreateModel(
            name="PracticeSession",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("number_of_questions", models.IntegerField()),
                ("time_limit", models.IntegerField(help_text="Time limit in minutes")),
                ("is_completed", models.BooleanField(default=False)),
                ("current_question_index", models.IntegerField(default=0)),
                ("question_types", models.ManyToManyField(to="quiz.questiontype")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PracticeAnswer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_correct", models.BooleanField()),
                ("time_taken", models.FloatField(help_text="Time taken in seconds")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="quiz.question"
                    ),
                ),
                (
                    "selected_choice",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="quiz.choice"
                    ),
                ),
                (
                    "session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="quiz.practicesession",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="choice",
            name="question",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="choices",
                to="quiz.question",
            ),
        ),
        migrations.AddConstraint(
            model_name="choice",
            constraint=models.UniqueConstraint(
                condition=models.Q(("is_correct", True)),
                fields=("question",),
                name="unique_correct_choice",
            ),
        ),
    ]
