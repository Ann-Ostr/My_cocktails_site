from django.core.validators import MinValueValidator
from django.db import models

from users.models import User

from .validators import validate_color

LENGTH = 200


class Ingredient(models.Model):
    name = models.CharField(
        max_length=LENGTH,
        verbose_name='Название ингредиента',
        help_text='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=LENGTH,
        verbose_name='Единица измерения ингредиента',
        help_text='Единица измерения ингредиента',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=LENGTH,
        verbose_name='Название тега',
        help_text='Название тега',
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет тега',
        help_text='Цвет тега',
        validators=[validate_color,],
    )
    slug = models.SlugField(
        max_length=LENGTH,
        unique=True,
        verbose_name='Слаг тега',
        help_text='Слаг тега',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        related_name='recipes',
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=LENGTH,
        verbose_name='Название рецепта',
        help_text='Название рецепта',
    )
    image = models.ImageField(
        verbose_name='Фото блюда рецепта',
        help_text='Фото блюда рецепта',
        # атрибут обеспечивает способ указания каталога загрузки и имени файла
        upload_to='recipes/images/',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Описание рецепта',
    )
    # Множественное поле с выбором из предустановленного списка
    # и с указанием количества и единицы измерения.
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
        related_name='recipes',
        verbose_name='Игредиенты рецепта',
        help_text='Игредиенты рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTags',
        related_name='recipes',
        verbose_name='Теги рецепта',
        help_text='Теги рецепта',
    )
    cooking_time = models.PositiveIntegerField(
        # минимальное значение 1 минута
        validators=(MinValueValidator(
            1, 'Время готовки не может быть меньше минуты'),),
        verbose_name='Время приготовления в минутах',
        help_text='Время приготовления в минутах',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeTags(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег')

    class Meta:
        verbose_name = 'Теги'
        verbose_name_plural = 'Теги'
        ordering = ('tag',)

    def __str__(self):
        return f"У рецепта {self.recipe} есть тег {self.tag}"


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        validators=(MinValueValidator(1, 'Не может быть меньше 1'),),
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиенты'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('recipe',)

    def __str__(self):
        return f"В рецепте {self.recipe} есть ингредиент {self.ingredient}"


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепт',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('recipe',)

    def __str__(self):
        return f'Избранное пользователя {self.user}'


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        ordering = ('recipe',)

    def __str__(self):
        return (
            f"Рецепт {self.recipe} в списке покупок у пользователя {self.user}"
        )
