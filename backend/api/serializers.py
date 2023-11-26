import base64

from django.core.files.base import ContentFile
from django.core.validators import MaxValueValidator, MinValueValidator
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import exceptions, serializers

from api.pagination import PageNumberPagination
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                            ShoppingCart, Tag)
from users.models import Subscription, User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        # Если полученный объект строка, и эта строка
        # начинается с 'data:image'...
        if isinstance(data, str) and data.startswith('data:image'):
            # начинаем декодировать изображение из base64.
            # Сначала нужно разделить строку на части.
            format, imgstr = data.split(';base64,')  # кодировка в base64
            # И извлечь расширение файла.
            ext = format.split('/')[-1]
            # Затем декодировать сами данные и поместить результат в файл,
            # которому дать название по шаблону.
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount', )


class RecipeSubscibeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class CustomUserCreateSerializer(UserCreateSerializer):
    # Проверка символов в юзернейме
    def validate_username(self, value):
        symbol = str(value)
        forbidden_symbol = '$'
        if forbidden_symbol in symbol:
            raise exceptions.ValidationError(
                f'Знак {forbidden_symbol} запрещен в юзернейме')
        return value

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'password')


class CustomUserSerializer(UserSerializer):
    # поле подписки, котрого нет в модели User
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        id_user = self.context.get('request').user.id
        return Subscription.objects.filter(
            author=obj.id, user=id_user
        ).exists()


class CreateUpdateRecipeIngredientsSerializer(serializers.ModelSerializer):
    # проверка мин.кол-ва ингридиента
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        validators=(MinValueValidator(1, message='Не может быть меньше 1'),
                    MaxValueValidator(5000, 'Не может быть больше 5000'),)
    )

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        ingredients = RecipeIngredients.objects.filter(recipe=obj)
        serializer = RecipeIngredientsSerializer(ingredients, many=True)
        return serializer.data

    def get_is_favorited(self, obj):
        user_id = self.context.get('request').user.id
        return Favorite.objects.filter(user=user_id, recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user_id = self.context.get('request').user.id
        return ShoppingCart.objects.filter(
            user=user_id, recipe=obj.id
        ).exists()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time',)


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = CreateUpdateRecipeIngredientsSerializer(many=True)
    image = Base64ImageField()
    image_url = serializers.SerializerMethodField(
        'get_image_url',
        read_only=True,
    )
    cooking_time = serializers.IntegerField(
        validators=(
            MinValueValidator(1, message='Не может быть меньше 1'),
            MaxValueValidator(1440, 'Не может быть больше суток'),),
    )

    # Проверка ингридиентов для рецепта
    def validate_ingredients(self, value):
        if not value:
            raise exceptions.ValidationError(
                'Ингридиент не может быть пустым')
        ingredients_ids = [ingredient['id'] for ingredient in value]
        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise exceptions.ValidationError('Ингрединты повторяются')
        return value

    # Проверки тегов для рецепта
    def validate_tags(self, value):
        if not value:
            raise exceptions.ValidationError('Тег не может быть пустым')
        tags = [tag for tag in value]
        if len(set(tags)) != len(tags):
            raise exceptions.ValidationError('Теги в рецепте повторяются')
        return value

    def create(self, validated_data):
        author = self.context.get('request').user
        # Уберем список из словаря validated_data и сохраним его
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        # Создадим новый рецепт пока без инг. и тегов
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_update_ingredients(self, ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.set(tags)
        else:
            raise exceptions.ValidationError('Поле тег в рецепте должно быть')
        ingrs = validated_data.pop('ingredients', None)
        if ingrs is not None:
            instance.ingredients.clear()
            self.create_update_ingredients(
                self, ingrs, instance)
        else:
            raise exceptions.ValidationError('Поле ингридиент должно быть')
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance, context={'request': self.context.get('request')}
        )
        return serializer.data

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    @staticmethod
    def create_update_ingredients(self, ingredients, recip):
        all_recipe_inredients = list()
        for ingr in ingredients:
            amount = ingr.get('amount')
            ingr_id = get_object_or_404(Ingredient, name=ingr.get('id'))
            recipe_ingreients = RecipeIngredients(recipe=recip,
                                                  ingredient=ingr_id,
                                                  amount=amount)
            all_recipe_inredients.append(recipe_ingreients)
        RecipeIngredients.objects.bulk_create(all_recipe_inredients)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'image_url', 'text', 'cooking_time')


class SubscriptionSerializer(CustomUserSerializer,
                             PageNumberPagination
                             ):
    email = serializers.ReadOnlyField(source="author.email")
    id = serializers.ReadOnlyField(source="author.id")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count',)

    def get_recipes(self, obj):
        # список рецептов fатора
        author_recipes = obj.author.recipes.all()
        if author_recipes:
            serializer = RecipeSubscibeSerializer(
                author_recipes,
                context={'request': self.context.get('request')},
                many=True,
            )
            return serializer.data
        return []

    def get_recipes_count(self, obj):
        # кол-во рецептов автора
        return Recipe.objects.filter(author=obj.id).count()
