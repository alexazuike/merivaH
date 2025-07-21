from django.contrib.auth.models import User
from rest_framework.permissions import BasePermission


class EncounterVitalsPermission(BasePermission):
    """Handles permissions for taking vitals an getting vitals"""

    def has_permission(self, request, view):
        user: User = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user: User = request.user
        EDIT_METHODS = ("PUT", "PATCH")
        SAFE_METHODS = ("OPTIONS", "HEAD")

        if user.is_superuser:
            return True

        if request.method in ["POST", "DELETE"]:
            return user.has_perm("encounters.take_vitals")

        if request.method in EDIT_METHODS:
            return user.has_perm("encounters.change_encounter")

        if request.method == "GET":
            return user.is_authenticated

        if request.method in SAFE_METHODS:
            return True

        return False
