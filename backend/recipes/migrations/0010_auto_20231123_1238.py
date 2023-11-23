# Generated by Django 3.2.16 on 2023-11-23 12:38

from django.db import migrations, models
import recipes.validators


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_alter_recipe_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'ordering': ('recipe',), 'verbose_name': 'Избранное', 'verbose_name_plural': 'Избранное'},
        ),
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ('name',), 'verbose_name': 'Ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='recipeingredients',
            options={'ordering': ('recipe',), 'verbose_name': 'Ингредиенты', 'verbose_name_plural': 'Ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='recipetags',
            options={'ordering': ('tag',), 'verbose_name': 'Теги', 'verbose_name_plural': 'Теги'},
        ),
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={'ordering': ('recipe',), 'verbose_name': 'Список покупок', 'verbose_name_plural': 'Список покупок'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ('name',), 'verbose_name': 'Тег', 'verbose_name_plural': 'Теги'},
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(help_text='Цвет тега', max_length=7, validators=[recipes.validators.validate_color], verbose_name='Цвет тега'),
        ),
    ]