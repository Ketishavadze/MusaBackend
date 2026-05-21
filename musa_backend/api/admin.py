from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import CartItem, Favourite, Order, OrderItem, Product, Studio, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (("Musa fields", {"fields": ("name", "earnings", "rating")}),)
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (("Musa fields", {"fields": ("name", "email")}),)
    list_display = ("username", "email", "name", "is_staff", "date_joined")
    search_fields = ("username", "email", "name")


@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "craft_type", "created_at")
    search_fields = ("name", "owner__username", "owner__email")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "studio", "category", "price", "active", "created_at")
    list_filter = ("category", "active")
    search_fields = ("title", "studio__name")


admin.site.register(Favourite)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
