from decimal import Decimal

from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CartItem, Favourite, Order, OrderItem, Product, Studio, User


class UserSerializer(serializers.ModelSerializer):
    isSeller = serializers.SerializerMethodField()
    memberSince = serializers.SerializerMethodField()
    studio = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "name",
            "username",
            "email",
            "isSeller",
            "memberSince",
            "earnings",
            "rating",
            "studio",
        )

    def get_isSeller(self, obj):
        return hasattr(obj, "studio")

    def get_memberSince(self, obj):
        return str(obj.date_joined.year)

    def get_studio(self, obj):
        if hasattr(obj, "studio"):
            return StudioSerializer(obj.studio).data
        return None


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    username = serializers.CharField(max_length=150, required=False, allow_blank=True)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_username(self, value):
        value = (value or "").strip()
        if value and User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def create(self, validated_data):
        name = validated_data["name"].strip()
        base_username = validated_data.get("username") or name.lower().replace(" ", "_")
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            counter += 1
            username = f"{base_username}_{counter}"

        user = User.objects.create_user(
            username=username,
            email=validated_data["email"],
            password=validated_data["password"],
            name=name,
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs["email"].lower()
        password = attrs["password"]
        user = User.objects.filter(email=email).first()
        if user is None:
            raise serializers.ValidationError("Invalid email or password.")
        user = authenticate(username=user.username, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid email or password.")
        attrs["user"] = user
        return attrs


def tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "user": UserSerializer(user).data,
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


class StudioSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.id")

    class Meta:
        model = Studio
        fields = ("id", "owner", "name", "craft_type", "description", "created_at")
        read_only_fields = ("id", "owner", "created_at")


class ProductSerializer(serializers.ModelSerializer):
    studio = serializers.CharField(source="studio.name", read_only=True)
    studio_id = serializers.IntegerField(source="studio.id", read_only=True)
    image = serializers.CharField(source="image_url", required=False, allow_blank=True)
    is_favourite = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "title",
            "studio",
            "studio_id",
            "price",
            "category",
            "image",
            "description",
            "rating",
            "active",
            "is_favourite",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "studio", "studio_id", "rating", "created_at", "updated_at")

    def get_is_favourite(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return Favourite.objects.filter(user=request.user, product=obj).exists()


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ("id", "product", "product_id", "qty", "line_total", "created_at", "updated_at")
        read_only_fields = ("id", "product", "line_total", "created_at", "updated_at")

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value, active=True).exists():
            raise serializers.ValidationError("Product does not exist or is not active.")
        return value

    def create(self, validated_data):
        product_id = validated_data.pop("product_id")
        qty = validated_data.get("qty", 1)
        item, created = CartItem.objects.get_or_create(
            user=self.context["request"].user,
            product_id=product_id,
            defaults={"qty": qty},
        )
        if not created:
            item.qty += qty
            item.save(update_fields=["qty", "updated_at"])
        return item


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "product", "title", "studio_name", "price", "qty", "line_total")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "status",
            "gift_wrap",
            "subtotal",
            "shipping",
            "gift_wrap_cost",
            "total",
            "items",
            "created_at",
        )
        read_only_fields = ("id", "status", "subtotal", "shipping", "gift_wrap_cost", "total", "items", "created_at")


class CheckoutSerializer(serializers.Serializer):
    gift_wrap = serializers.BooleanField(default=False)

    def create(self, validated_data):
        user = self.context["request"].user
        gift_wrap = validated_data.get("gift_wrap", False)
        items = list(CartItem.objects.select_related("product", "product__studio").filter(user=user))
        if not items:
            raise serializers.ValidationError("Cart is empty.")

        gift_wrap_cost = Decimal("2.50") if gift_wrap else Decimal("0.00")
        subtotal = sum((item.product.price * item.qty for item in items), Decimal("0.00"))
        shipping = Decimal("5.00") if Decimal("0.00") < subtotal < Decimal("75.00") else Decimal("0.00")
        total = subtotal + shipping + gift_wrap_cost

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                gift_wrap=gift_wrap,
                subtotal=subtotal,
                shipping=shipping,
                gift_wrap_cost=gift_wrap_cost,
                total=total,
            )
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    title=item.product.title,
                    studio_name=item.product.studio.name,
                    price=item.product.price,
                    qty=item.qty,
                )
            CartItem.objects.filter(user=user).delete()
        return order
