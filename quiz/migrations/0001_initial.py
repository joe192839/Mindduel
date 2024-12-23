# Generated by Django 5.1.1 on 2024-11-20 03:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
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
    ]
