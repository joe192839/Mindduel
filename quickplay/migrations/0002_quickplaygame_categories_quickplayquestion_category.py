# Generated by Django 4.2.16 on 2024-12-10 05:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("quickplay", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="quickplaygame",
            name="categories",
            field=models.CharField(
                blank=True,
                help_text="Comma-separated list of selected categories",
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name="quickplayquestion",
            name="category",
            field=models.CharField(
                choices=[
                    ("reasoning", "Reasoning (Logical)"),
                    ("linguistic", "Linguistic (Verbal)"),
                    ("quantitative", "Quantitative (Numerical)"),
                    ("spatial", "Spatial (Abstract)"),
                ],
                default="reasoning",
                max_length=20,
            ),
        ),
    ]
