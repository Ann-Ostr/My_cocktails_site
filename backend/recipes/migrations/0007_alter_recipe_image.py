# Generated by Django 3.2.16 on 2023-11-20 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_alter_recipe_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(help_text='Фото блюда рецепта', upload_to='media/media/', verbose_name='Фото блюда рецепта'),
        ),
    ]
