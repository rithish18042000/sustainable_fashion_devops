from django.test import TestCase
from django.contrib.auth.models import User
from .models import Category, Product, Review

class ModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name="T-Shirts", description="Casual tops")

    def test_product_creation(self):
        product = Product.objects.create(
            name="Eco Cotton T-Shirt",
            description="Made from 100% organic cotton.",
            price=29.99,
            category=self.category,
            sustainability_score=85,
            materials="Organic Cotton",
            seller=self.user
        )
        self.assertEqual(product.name, "Eco Cotton T-Shirt")
        self.assertEqual(product.category.name, "T-Shirts")
        self.assertTrue(product.in_stock)

    def test_review_creation(self):
        product = Product.objects.create(
            name="Linen Pants",
            description="Breathable and comfy.",
            price=49.99,
            category=self.category,
            sustainability_score=90,
            materials="Linen",
            seller=self.user
        )
        review = Review.objects.create(
            product=product,
            user=self.user,
            rating=5,
            comment="Super comfortable and eco-friendly!"
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(str(review), f"{self.user.username}'s review for {product.name}")
