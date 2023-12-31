# Generated by Django 3.2.16 on 2023-11-26 05:20

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0011_auto_20231126_0514'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredients',
            name='amount',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1, 'Не может быть меньше 1'), django.core.validators.MaxValueValidator(5000, 'Не может быть 5000')], verbose_name='Количество'),
        ),
    ]
