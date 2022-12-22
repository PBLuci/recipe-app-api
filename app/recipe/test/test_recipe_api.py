

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe
from recipe.serializers import RecipeSerializer

RECIPE_URL = reverse('recipe:recipe-list')

def create_recipe(user, **args):
    default = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample recipe description',
        'link': 'https://example.com/recipe.pdf'
    }
    default.update(args)

    recipe = Recipe.objects.create(user=user, **default)
    return recipe

class PublicRecipeApiTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_require(self):

        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeApiTest(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )

        self.client.force_authenticate(self.user)

    def test_retrive_recipes(self):

        create_recipe(self.user)
        create_recipe(self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')

        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    def test_recipe_list_limited_to_user(self):

        other_user = get_user_model().objects.create_user(
            'user2@example.com',
            'testpass1234',
        )

        create_recipe(user=self.user)
        create_recipe(user=self.user)
        create_recipe(user=other_user)
        create_recipe(user=other_user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user).order_by('-id')

        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

