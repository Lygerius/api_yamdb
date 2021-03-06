from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action

from api_yamdb.settings import YAMDB_EMAIL

from .filters import TitleFilter
from .models import Category, Genre, Review, Title, User
from .permissions import IsAdminPerm, OwnResourcePermission, ReadOnly
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleListSerializer,
    TitlePostSerializer,
    TokenSerializer,
    UserCodeSerializer,
)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [OwnResourcePermission]

    def perform_create(self, serializer):
        title = get_object_or_404(Title,
                                  pk=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs["title_id"])
        return title.reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [OwnResourcePermission]

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get("review_id"))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get("review_id"))
        serializer.save(author=self.request.user, review=review)


class CreateCodeViewSet(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        email = serializer.data.get("email")
        confirmation_code = default_token_generator.make_token()
        User.objects.get_or_create(
            email=email,
            username=str(email),
            confirmation_code=confirmation_code,
            is_active=False,
        )
        send_mail(
            f"Код регистрации для YAMDB",
            f"{confirmation_code}",
            YAMDB_EMAIL,
            [f"{email}"],
            fail_silently=False,
        )
        return Response(
            {"result": "Код подтверждения отправлен на почту"}, status=200
        )


class CodeJWTView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TokenSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            email=serializer.data["email"],
            confirmation_code=serializer.data["confirmation_code"],
        )
        user.save()
        refresh_token = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh_token),
                "token": str(refresh_token.access_token),
            }
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserCodeSerializer
    lookup_field = "username"
    pagination_class = PageNumberPagination
    permission_classes = [permissions.IsAuthenticated, IsAdminPerm]

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        serializer = self.get_serializer(
            user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class CatalogViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    permission_classes = [IsAuthenticated & IsAdminPerm | ReadOnly]
    lookup_field = "slug"
    search_fields = ["=name"]
    filter_backends = [filters.SearchFilter]
    pagination_class = PageNumberPagination


class CategoryViewSet(CatalogViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CatalogViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated & IsAdminPerm | ReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return TitleListSerializer
        return TitlePostSerializer
