from typing import List

from rest_framework import serializers
from django.contrib.auth.models import User, Group, Permission

from . import models


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ("id", "name", "codename")
        depth = 1


class GroupRequestSerializer(serializers.ModelSerializer):
    permissions = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all()),
        write_only=True,
        required=True,
    )
    description = serializers.CharField(allow_null=True, required=False)

    class Meta:
        model = Group
        fields = ("id", "name", "description", "permissions")
        depth = 1

    def __save_update_group_extras(self, group, **kwargs):
        if hasattr(group, "groupextras"):
            for key in kwargs:
                setattr(group.groupextras, key, kwargs.get(key))
            group.groupextras.save()
        else:
            models.GroupExtras.create_record(group=group, **kwargs)
        return group

    def create(self, validated_data: dict):
        permissions = validated_data.pop("permissions")
        description = validated_data.pop("description", None)
        group = Group.objects.create(**validated_data)
        group.permissions.set(permissions)
        self.__save_update_group_extras(group, description=description)
        return group

    def update(self, instance: Group, validated_data: dict):
        permissions = validated_data.pop("permissions", instance.permissions)
        description = validated_data.pop("description", None)
        instance.name = validated_data.get("name", instance.name)
        instance.permissions.set(permissions)
        instance.save()
        self.__save_update_group_extras(instance, description=description)
        return instance


class GroupResponseSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ("id", "name", "description", "permissions")
        depth = 1

    def get_description(self, obj):
        if hasattr(obj, "groupextras"):
            return obj.groupextras.description
        return None


class UserRequestSerializer(serializers.ModelSerializer):
    groups = serializers.ListSerializer(
        write_only=True,
        child=serializers.PrimaryKeyRelatedField(queryset=Group.objects.all()),
        required=True,
    )
    menus = serializers.ListField(
        child=serializers.DictField(), allow_empty=True, required=False, default=[]
    )

    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = (
            "last_login",
            "is_superuser",
            "is_staff",
            "is_active",
            "date_joined",
            "password",
        )
        depth = 1

    def __get_user_extras(self, user):
        if hasattr(user, "userextras"):
            return user.userextras.menus
        return models.UserExtras.create_record(user).menus

    def __update_user_extras(self, user, **kwargs):
        if hasattr(user, "userextras"):
            for key in kwargs:
                setattr(user.userextras, key, kwargs.get(key))
            user.userextras.save()
        else:
            models.UserExtras.create_record(user, **kwargs)
        return user

    def create(self, validated_data: dict):
        groups: List[Group] = validated_data.pop("groups")
        menus: List[dict] = validated_data.pop("menus")
        user = User.objects.create_user(**validated_data, is_active=True)
        user.groups.set(groups)
        self.__update_user_extras(user, menus=menus)
        return user

    def update(self, instance: User, validated_data: dict):
        groups: List[Group] = validated_data.pop("groups", instance.groups.all())
        menus: List[dict] = validated_data.pop(
            "menus", self.__get_user_extras(instance)
        )
        password = validated_data.pop("password", None)
        instance.username = validated_data.get("username", instance.username)
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.email = validated_data.get("email", instance.email)
        instance.groups.set(groups)
        self.__update_user_extras(instance, menus=menus)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    menus = serializers.SerializerMethodField()
    password_recover_status = serializers.SerializerMethodField(read_only=True)
    password_recover_date = serializers.SerializerMethodField(read_only=True)

    def __get_user_extras(self, user):
        if hasattr(user, "userextras"):
            return user.userextras.menus
        return models.UserExtras.create_record(user).menus

    def get_menus(self, obj):
        return self.__get_user_extras(obj)

    def get_password_recover_status(self, obj):
        if hasattr(obj, "passwordrecovery"):
            return obj.passwordrecovery.is_active
        return False

    def get_password_recover_date(self, obj):
        if hasattr(obj, "passwordrecovery"):
            return obj.passwordrecovery.created_at
        return None

    class Meta:
        model = User
        exclude = ["password"]
        read_only_fields = (
            "last_login",
            "is_superuser",
            "is_staff",
            "is_active",
            "date_joined",
        )
        depth = 1
