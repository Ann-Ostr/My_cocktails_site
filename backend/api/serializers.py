from django.core.validators import MinValueValidator
from djoser.serializers import UserSerializer, UserCreateSerializer
import base64
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404

from rest_framework import exceptions, serializers

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
)
from users.models import Subscription, User
from api.pagination import PageNumberPagination


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
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    def get_name(self, obj):
        ingredients = Ingredient.objects.filter(id=obj.id)
        serializer = IngredientSerializer(ingredients, many=True)
        return serializer.data[0]['name']

    def get_measurement_unit(self, obj):
        ingredients = Ingredient.objects.filter(id=obj.id)
        serializer = IngredientSerializer(ingredients, many=True)
        return serializer.data[0]['measurement_unit']
   
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


class CreateUpdateRecipeIngredientsSerializer(serializers.ModelSerializer):
    # проверка мин.кол-ва ингридиента
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        validators=(MinValueValidator(1, message='Не может быть меньше 1'),)
    )

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class CustomUserSerializer(UserSerializer):
    # поле подписки, котрого нет в модели User
    is_subscribed = serializers.SerializerMethodField()
    

    class Meta:
        model = User
        fields = ('email', 'id',  'username', 'first_name', 'last_name', 
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        id_user = self.context.get('request').user.id
        return Subscription.objects.filter(
            author=obj.id, user=id_user
        ).exists()
   


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
                  'cooking_time',
                  )


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = CreateUpdateRecipeIngredientsSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=(
            MinValueValidator(1, message='Не может быть меньше 1'),)
    )

    # Проверка ингридиентов для рецепта
    def validate_ingredients(self, value):
        if not value:
            raise exceptions.ValidationError(
                'Ингридиент не может быть пустым')
        ingredient_set = set()
        ingredient_list = list()
        for i in value:
            ingredient_set.add(i['id'])
            ingredient_list.append(i['id'])
        if len(ingredient_set) != len(ingredient_list):
            raise exceptions.ValidationError(
                    'Ингрединты в рецепте повторяются')
        return value

    # Проверки тегов для рецепта
    def validate_tags(self, value):
        if not value:
            raise exceptions.ValidationError('Тег не может быть пустым')
        tag_set = set()
        tag_list = list()
        for i in value:
            tag_set.add(i)
            tag_list.append(i)
        if len(tag_set) != len(tag_list):
            raise exceptions.ValidationError(
                    'Теги в рецепте повторяются')
        return value

    def create(self, validated_data):
        author = self.context.get('request').user
        # Уберем список из словаря validated_data и сохраним его
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        # Создадим новый рецепт пока без инг. и тегов
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        # Для каждого ингридиента из списка
        for ingredient in ingredients:
            # узнаем кол-во 
            amount = ingredient.get('amount')
            # создадим новую запись или получим существующий экземпляр из БД
            ingredient = get_object_or_404(
                Ingredient, pk=ingredient.get('id').id
            )
            # Поместим ссылку  во вспомогательную таблицу
            # Не забыв указать к какому рецепту оно относится
            RecipeIngredients.objects.create(
                recipe=recipe, ingredient=ingredient, amount=amount
            )
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.set(tags)

        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            instance.ingredients.clear()

            for ingredient in ingredients:
                amount = ingredient.get('amount')
                ingredient = get_object_or_404(
                    Ingredient, pk=ingredient.get('id').id
                )

                RecipeIngredients.objects.update_or_create(
                    recipe=instance,
                    ingredient=ingredient,
                    defaults={'amount': amount},
                )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance, context={'request': self.context.get('request')}
        )
        return serializer.data

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time')


class SubscriptionSerializer(CustomUserSerializer,
                             PageNumberPagination
                             ):
    email = serializers.ReadOnlyField()
    id = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_subscribed', 'recipes', 'recipes_count',)

    def get_recipes(self, obj):
        # список рецептов fатора
        from api.serializers import RecipeSubscibeSerializer
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
