from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CartItemDetailView,
    CartListCreateView,
    FavouriteListView,
    LoginView,
    LogoutView,
    MeView,
    OrderListCreateView,
    ProductViewSet,
    RegisterView,
    StudioMeView,
)

router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("auth/me/", MeView.as_view(), name="auth-me"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("studios/me/", StudioMeView.as_view(), name="studio-me"),
    path("favourites/", FavouriteListView.as_view(), name="favourites"),
    path("cart/", CartListCreateView.as_view(), name="cart"),
    path("cart/<int:item_id>/", CartItemDetailView.as_view(), name="cart-item"),
    path("orders/", OrderListCreateView.as_view(), name="orders"),
    path("", include(router.urls)),
]
