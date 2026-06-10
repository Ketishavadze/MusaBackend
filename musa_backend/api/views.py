from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken



from .models import CartItem, Favourite, Order, Product, Studio
from .permissions import IsProductOwnerOrReadOnly
from .serializers import (
    CartItemSerializer,
    CheckoutSerializer,
    LoginSerializer,
    OrderSerializer,
    ProductSerializer,
    RegisterSerializer,
    StudioSerializer,
    UserSerializer,
    tokens_for_user,
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(tokens_for_user(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(tokens_for_user(serializer.validated_data["user"]))


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except Exception:
                pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class StudioMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        studio = getattr(request.user, "studio", None)
        if not studio:
            return Response({"registered": False, "studio": None})
        return Response({"registered": True, "studio": StudioSerializer(studio).data})

    def post(self, request):
        if hasattr(request.user, "studio"):
            return Response(StudioSerializer(request.user.studio).data, status=status.HTTP_200_OK)
        serializer = StudioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        studio = serializer.save(owner=request.user)
        return Response(StudioSerializer(studio).data, status=status.HTTP_201_CREATED)




class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]

        if self.action == "favourite":
            return [IsAuthenticated()]

        return [IsAuthenticated(), IsProductOwnerOrReadOnly()]

    def get_queryset(self):
        qs = Product.objects.select_related("studio", "studio__owner")

        mine = self.request.query_params.get("mine")

        if mine == "true":
            if (
                not self.request.user.is_authenticated
                or not hasattr(self.request.user, "studio")
            ):
                return Product.objects.none()

            qs = qs.filter(studio=self.request.user.studio)
        else:
            qs = qs.filter(active=True)

        category = self.request.query_params.get("category")
        if category and category != "All Crafts":
            qs = qs.filter(category=category)

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(studio__name__icontains=search)
            )

        return qs.order_by("-created_at")

    def perform_create(self, serializer):
        studio = getattr(self.request.user, "studio", None)

        if not studio:
            raise ValidationError("Register your studio before creating listings.")

        serializer.save(studio=studio)

    def perform_update(self, serializer):
        product = self.get_object()

        if product.studio.owner_id != self.request.user.id and not self.request.user.is_staff:
            raise PermissionDenied("Only the studio owner can edit this listing.")

        serializer.save(studio=product.studio)

    def perform_destroy(self, instance):
        if instance.studio.owner_id != self.request.user.id and not self.request.user.is_staff:
            raise PermissionDenied("Only the studio owner can delete this listing.")

        instance.delete()

    @action(detail=True, methods=["post"], url_path="favourite")
    def favourite(self, request, pk=None):
        product = self.get_object()

        favourite, created = Favourite.objects.get_or_create(
            user=request.user,
            product=product,
        )

        if created:
            liked = True
        else:
            favourite.delete()
            liked = False

        return Response({"liked": liked})


class FavouriteListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        products = Product.objects.filter(favourited_by__user=request.user, active=True).select_related("studio")
        return Response(ProductSerializer(products, many=True, context={"request": request}).data)


class CartListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = CartItem.objects.filter(user=request.user).select_related("product", "product__studio")
        return Response(CartItemSerializer(items, many=True, context={"request": request}).data)

    def post(self, request):
        serializer = CartItemSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        item = serializer.save()
        return Response(CartItemSerializer(item, context={"request": request}).data, status=status.HTTP_201_CREATED)


class CartItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):
        item = get_object_or_404(CartItem, id=item_id, user=request.user)
        qty = request.data.get("qty")
        if qty is None:
            raise ValidationError("qty is required.")
        qty = int(qty)
        if qty <= 0:
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        item.qty = qty
        item.save(update_fields=["qty", "updated_at"])
        return Response(CartItemSerializer(item, context={"request": request}).data)

    def delete(self, request, item_id):
        item = get_object_or_404(CartItem, id=item_id, user=request.user)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).prefetch_related("items")
        return Response(OrderSerializer(orders, many=True).data)

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
