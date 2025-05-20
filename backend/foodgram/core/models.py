from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator


class User(AbstractUser):
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
                regex=r'[\w.@+-]+',
                message='Юзернейм пользователя может содержать только буквы, а также следующие символы: ./@/+/-'
            ),
        ],
        error_messages={
            'unique': "Пользователь с таким именем уже существует.",
        },
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=True
    )
    avatar = models.URLField(
        verbose_name='Аватар',
        blank=True,
        null=True
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
                fields=["user", "subscribed_to"], name="uq_Subscription"
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
        verbose_name='Пользователь')
    name = models.CharField(
        verbose_name='Название',
        max_length=256
    )
    image = models.URLField(
        verbose_name='Картинка',
        blank=True,
        null=True
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    cooking_time = models.IntegerField(
        verbose_name='Описание',
        validators=[
            MinValueValidator(
                limit_value=0,
                message="Время приготовления должно быть больше или равно одной минуте"
            )
        ]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('id',)

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='ingredients',
        verbose_name='Рецепт')
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='Ингридиент')
    amount = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Количество",
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
        ordering = ('id',)

    def __str__(self):
        return self.recipe.name + ' - ' + self.ingredient.name