from django.contrib.auth.models import User, Group, Permission
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import filters, permissions, generics, viewsets, status
from rest_framework.decorators import api_view, permission_classes

from api.apps.users import serializers
from api.apps.authentication import serializers as auth_serializers
from api.apps.authentication import models as auth_models
from api.includes import exceptions
from api.includes import pagination
from . import filters as user_filters


class PermissionsViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = serializers.PermissionSerializer
    permission_classes = [permissions.IsAdminUser, permissions.IsAuthenticated]


class GroupsviewSet(
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Group.objects.all()
    permission_classes = [permissions.IsAdminUser, permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return serializers.GroupRequestSerializer
        return serializers.GroupResponseSerializer


class UserCreateList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAdminUser, permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = user_filters.UserFilters
    pagination_class = pagination.CustomPagination
    ordering = "-id"

    def get_serializer_class(self):
        if self.request.method == "GET":
            return serializers.UserSerializer
        return serializers.UserRequestSerializer

    @extend_schema(
        request=serializers.UserRequestSerializer,
        responses=auth_serializers.PasswordRecoverSerializer,
    )
    def post(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        context["max_users_count"] = getattr(request, "max_users_count", None)
        serializer: serializers.UserRequestSerializer = self.get_serializer(
            data=request.data, context=context
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        recovery_password = auth_models.PasswordRecovery.setup_password_recovery(user)
        response_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "recovery_password": recovery_password,
        }
        serializer = auth_serializers.PasswordRecoverSerializer(data=response_data)
        serializer.is_valid(raise_exception=True)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return serializers.UserRequestSerializer
        return serializers.UserSerializer


############## Extra Routes ###################


@extend_schema(
    request=None,
    responses=serializers.UserSerializer,
)
@api_view(["PATCH"])
@permission_classes([permissions.IsAuthenticated, permissions.IsAdminUser])
def activate_user(request, pk=None):
    """Activates a deactivated user account"""
    try:
        user = User.objects.get(id=pk)
    except User.DoesNotExist:
        raise exceptions.NotFoundException("User not found")

    if user.is_active:
        return Response(
            data={"message": "User is already active"}, status=status.HTTP_200_OK
        )
    active_users = User.objects.filter(is_active=True)
    if getattr(request, "max_users_count", None):
        if active_users.count() >= request.max_users_count:
            raise exceptions.PermissionDenied("License limit is reached")
    user.is_active = True
    user.save()
    return Response(
        data={"message": "User activation is successful"}, status=status.HTTP_200_OK
    )


@extend_schema(
    request=None,
    responses=serializers.UserSerializer,
)
@api_view(["PATCH"])
@permission_classes([permissions.IsAuthenticated, permissions.IsAdminUser])
def deactivate_user(request, pk=None):
    """Deactivates an activated user account"""
    try:
        user = User.objects.get(id=pk)
    except User.DoesNotExist:
        raise exceptions.NotFoundException("User not found")
    if not user.is_active:
        return Response(
            data={"message": "User is already deactivated"},
            status=status.HTTP_200_OK,
        )
    user.is_active = False
    user.save()
    return Response(
        data={"message": "User deactivation is successful"},
        status=status.HTTP_200_OK,
    )
