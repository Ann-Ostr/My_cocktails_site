# Generated by Django 3.2.16 on 2023-11-26 06:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0013_auto_20231126_0521'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.IntegerField(help_text='Время приготовления в минутах', validators=[django.core.validators.MinValueValidator(1, 'Время готовки не может быть меньше минуты')], verbose_name='Время приготовления в минутах'),
        ),
        migrations.AlterField(
            model_name='recipeingredients',
            name='amount',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1, 'Не может быть меньше 1')], verbose_name='Количество'),
        ),
    ]
