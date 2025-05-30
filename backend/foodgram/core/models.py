from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    RegexValidator,
    MinValueValidator,
    MaxValueValidator
)

from core.const import (
    MIN_COOKING_TIME,
    MAX_COOKING_TIME,
    MIN_INGREDIENT_AMOUNT,
    MAX_INGREDIENT_AMOUNT
)


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True
    )
    username = models.CharField(
        verbose_name='Юзернейм пользователя',
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message=(
                    'Юзернейм пользователя может содержать только буквы, '
                    'а также следующие символы: ./@/+/-'
                )
            ),
        ],
        error_messages={
            'unique': 'Пользователь с таким именем уже существует.',
        },
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='users',
        blank=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribers',
        verbose_name='Пользователь')
    subscribed_to = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribed',
        verbose_name='Подписчик')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscribed_to'], name='uq_Subscription'
            )
        ]

        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('id',)

    def __str__(self):
        return self.user.username + ' > ' + self.subscribed_to.username


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=128
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=64
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('id',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='Пользователь'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты'
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=256
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                limit_value=MIN_COOKING_TIME,
                message=(
                    'Время приготовления должно быть '
                    f'больше или равно {MIN_COOKING_TIME} минут'
                )
            ),
            MaxValueValidator(
                limit_value=MAX_COOKING_TIME,
                message=(
                    'Время приготовления должно быть '
                    f'меньше {MAX_COOKING_TIME} минут'
                )
            )
        ]
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created',)

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='ingredient_amounts', verbose_name='Рецепт')
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='ingredient_amounts', verbose_name='Ингридиент')
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                limit_value=MIN_INGREDIENT_AMOUNT,
                message=(
                    'Количество ингредиентов должно быть '
                    f'больше или равно {MIN_INGREDIENT_AMOUNT} шт.'
                )
            ),
            MaxValueValidator(
                limit_value=MAX_INGREDIENT_AMOUNT,
                message=(
                    'Количество ингредиентов должно быть '
                    f'меньше {MAX_INGREDIENT_AMOUNT} шт.'
                )
            )
        ],
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
        ordering = ('id',)

    def __str__(self):
        return self.recipe.name + ' - ' + self.ingredient.name


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites',
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='users_in_favorite',
        verbose_name='Рецепт')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='uq_Favorite'
            )
        ]

        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('id',)

    def __str__(self):
        return self.user.username + ' > ' + self.recipe.name


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_cart',
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='users_in_shopcart',
        verbose_name='Подписчик')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='uq_Shopcart'
            )
        ]

        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        ordering = ('id',)

    def __str__(self):
        return self.user.username + ' > ' + self.recipe.name
