from django.contrib.auth.models import User
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions

from api.includes import utils, exceptions
from api.apps.users import serializers as user_serializers
from . import serializers
from . import models


@extend_schema(
    request=serializers.LoginRequestSerializer,
    responses=serializers.LoginResponseSerializer,
)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login(request, pk=None):
    serializer = serializers.LoginRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.data["username"]
    password = serializer.data["password"]

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise exceptions.BadRequest("User does not exist")

    token = None
    user_serializer = user_serializers.UserSerializer(instance=user)

    if getattr(request, "max_users_count", None):
        if Token.objects.all().count() >= request.max_users_count:
            raise exceptions.PermissionDenied("License limit is reached")

    if not user.check_password(password) and not hasattr(user, "passwordrecovery"):
        raise exceptions.BadRequest("Invalid Credentials")
    if user.check_password(password):
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        token = token.key
        user.last_login = timezone.now()
        user.save()
    if not user.check_password(password) and hasattr(user, "passwordrecovery"):
        if not user.passwordrecovery.confirm_password(password):
            raise exceptions.BadRequest("Invalid Credentials")

    serializer = serializers.LoginResponseSerializer(
        data={"token": token, **user_serializer.data}
    )
    serializer.is_valid(raise_exception=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    request=None,
    responses={204: None},
)
@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def logout(request, pk=None):
    """Logs out a user"""
    user: User = request.user
    user.auth_token.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(request=None, responses=serializers.PasswordRecoverSerializer)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated, permissions.IsAdminUser])
def reset_password(request, id):
    """Resets a user password"""
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        raise exceptions.NotFoundException("User not found")

    recovery_password = None
    if hasattr(user, "passwordrecovery"):
        recovery_password = user.passwordrecovery.password
    else:
        recovery_password = models.PasswordRecovery.setup_password_recovery(user)

    user_data = utils.model_to_dict(user)
    serializer = serializers.PasswordRecoverSerializer(
        data={"recovery_password": recovery_password, **user_data}
    )
    serializer.is_valid(raise_exception=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    request=serializers.PasswordRecoveryUpdateSerializer,
    responses=serializers.LoginResponseSerializer,
)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def update_password(request):
    """Updates a reset password"""
    serializer = serializers.PasswordRecoveryUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.process_recovery()
    token, created = Token.objects.get_or_create(user=user)
    user_data = utils.model_to_dict(user)
    serializer = serializers.LoginResponseSerializer(
        data={"token": token.key, **user_data}
    )
    serializer.is_valid(raise_exception=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)
