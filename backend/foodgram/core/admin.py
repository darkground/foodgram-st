from django.contrib import admin

from .models import (
    Ingredient,
    IngredientInRecipe,
    Recipe,
    Subscription,
    User
)

# Register your models here.

admin.site.register(User)
admin.site.register(Subscription)
admin.site.register(Ingredient)
admin.site.register(IngredientInRecipe)
admin.site.register(Recipe)