from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User

from api.includes import exceptions


class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    password = serializers.CharField(required=True, allow_null=False, allow_blank=False)


class LoginResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    username = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    email = serializers.CharField(allow_null=True, allow_blank=True)
    first_name = serializers.CharField(allow_null=True, allow_blank=True)
    last_name = serializers.CharField(allow_null=True, allow_blank=True)
    token = serializers.CharField(allow_null=True, allow_blank=True)
    groups = serializers.ListField(allow_empty=True, default=[])
    menus = serializers.ListField(allow_empty=True, default=[])


class PasswordRecoverSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    username = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    email = serializers.CharField(allow_null=True, allow_blank=True)
    recovery_password = serializers.CharField(allow_null=False, allow_blank=False)


class PasswordRecoveryUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    recovery_password = serializers.CharField(
        required=True, allow_null=False, allow_blank=False
    )
    new_password = serializers.CharField(
        required=True, allow_null=False, allow_blank=False
    )
    confirm_password = serializers.CharField(
        required=True, allow_null=False, allow_blank=False
    )

    def __validate_user_password_recovery(self, username: str, recovery_password: str):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise exceptions.BadRequest("User does not exist")

        if hasattr(user, "passwordrecovery"):
            if user.passwordrecovery.confirm_password(recovery_password):
                return None
        raise exceptions.BadRequest("Invalid Recovery Password")

    def validate(self, data):
        new_password, confirm_password = data.get("new_password"), data.get(
            "confirm_password"
        )
        recovery_password = data.get("recovery_password")
        username = data.get("username")
        self.__validate_user_password_recovery(username, recovery_password)
        if new_password != confirm_password:
            raise serializers.ValidationError("Passwords do not match")

        validate_password(new_password)
        return data

    def process_recovery(self) -> User:
        new_password = self.validated_data.get("new_password")
        recovery_password = self.validated_data.get("recovery_password")
        username = self.validated_data.get("username")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise exceptions.BadRequest("User does not exist")

        if hasattr(user, "passwordrecovery"):
            if user.passwordrecovery.confirm_password(recovery_password):
                user.passwordrecovery.complete_recovery(new_password)
                return user
        raise exceptions.BadRequest("Invalid Recovery Password")
