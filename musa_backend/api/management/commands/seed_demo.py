from decimal import Decimal

from django.core.management.base import BaseCommand

from api.models import Product, Studio, User


PRODUCTS = [
    {
        "title": "Blue Crochet Top",
        "price": Decimal("45.00"),
        "category": "Crochet",
        "image_url": "https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=700&q=80",
        "rating": Decimal("4.9"),
        "active": True,
    },
    {
        "title": "Beaded Necklace",
        "price": Decimal("32.00"),
        "category": "Jewelry",
        "image_url": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=700&q=80",
        "rating": Decimal("4.7"),
        "active": True,
    },
    {
        "title": "Soft Pink Shawl",
        "price": Decimal("28.00"),
        "category": "Textile",
        "image_url": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=700&q=80",
        "rating": Decimal("4.8"),
        "active": True,
    },
    {
        "title": "Ceramic Trinket Dish",
        "price": Decimal("38.00"),
        "category": "Pottery",
        "image_url": "https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?auto=format&fit=crop&w=700&q=80",
        "rating": Decimal("4.6"),
        "active": True,
    },
    {
        "title": "Earthy Cardigan",
        "price": Decimal("120.00"),
        "category": "Crochet",
        "image_url": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=700&q=80",
        "rating": Decimal("5.0"),
        "active": True,
    },
    {
        "title": "Floral Press-on Nails",
        "price": Decimal("24.00"),
        "category": "Jewelry",
        "image_url": "https://images.unsplash.com/photo-1604654894610-df63bc536371?auto=format&fit=crop&w=700&q=80",
        "rating": Decimal("4.5"),
        "active": True,
    },
    {
        "title": "Handmade Vase",
        "price": Decimal("64.00"),
        "category": "Pottery",
        "image_url": "https://images.unsplash.com/photo-1610701596007-11502861dcfa?auto=format&fit=crop&w=700&q=80",
        "rating": Decimal("4.8"),
        "active": True,
    },
    {
        "title": "Crochet Set",
        "price": Decimal("65.00"),
        "category": "Crochet",
        "image_url": "https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?auto=format&fit=crop&w=700&q=80",
        "rating": Decimal("4.7"),
        "active": True,
    },
]


class Command(BaseCommand):
    help = "Create demo Musa user, studio, and products."

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username="user_nn",
            defaults={"email": "demo@musa.com", "name": "nn", "earnings": Decimal("1240.00"), "rating": Decimal("100.0")},
        )
        if created:
            user.set_password("password")
            user.save()

        studio, _ = Studio.objects.get_or_create(
            owner=user,
            defaults={"name": "Studio 138", "craft_type": "Crochet", "description": "Cozy handmade pieces."},
        )

        for data in PRODUCTS:
            Product.objects.get_or_create(studio=studio, title=data["title"], defaults=data)

        self.stdout.write(self.style.SUCCESS("Seeded demo data. Login: demo@musa.com / password"))
