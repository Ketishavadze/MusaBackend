from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=120)
    earnings = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    rating = models.DecimalField(max_digits=4, decimal_places=1, default=Decimal("0.0"))

    REQUIRED_FIELDS = ["email", "name"]

    def __str__(self):
        return self.username


class Studio(models.Model):
    class CraftType(models.TextChoices):
        CROCHET = "Crochet", "Crochet"
        JEWELRY = "Jewelry", "Jewelry"
        POTTERY = "Pottery", "Pottery"
        TEXTILE = "Textile", "Textile"
        MIXED = "Mixed Crafts", "Mixed Crafts"

    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name="studio")
    name = models.CharField(max_length=120, unique=True)
    craft_type = models.CharField(max_length=40, choices=CraftType.choices)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    class Category(models.TextChoices):
        CROCHET = "Crochet", "Crochet"
        JEWELRY = "Jewelry", "Jewelry"
        POTTERY = "Pottery", "Pottery"
        TEXTILE = "Textile", "Textile"

    studio = models.ForeignKey(Studio, on_delete=models.CASCADE, related_name="products")
    title = models.CharField(max_length=160)
    category = models.CharField(max_length=30, choices=Category.choices)
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=Decimal("0.0"))
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Favourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favourites")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="favourited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} likes {self.product.title}"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    qty = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "product")
        ordering = ["-updated_at"]

    @property
    def line_total(self):
        return self.product.price * self.qty

    def __str__(self):
        return f"{self.user.username} × {self.product.title} ({self.qty})"


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PAID)
    gift_wrap = models.BooleanField(default=False)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    gift_wrap_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=160)
    studio_name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    qty = models.PositiveIntegerField(default=1)

    @property
    def line_total(self):
        return self.price * self.qty

    def __str__(self):
        return f"{self.title} × {self.qty}"
