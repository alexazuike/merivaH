from rest_framework import permissions
from django.contrib.auth.models import User


class NursingTaskPermission(permissions.BasePermission):
    """
    Serves as base permissions class for nursing task activities
    """

    def has_permission(self, request, view):
        user: User = request.user
        return user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user: User = request.user
        EDIT_METHODS = ("PUT", "PATCH")
        SAFE_METHODS = ("OPTIONS", "HEAD")

        # check if user is admin
        if user.is_superuser:
            return True

        if request.method == "POST":
            return user.has_perm("nursing.add_task")

        if request.method == "GET":
            return user.has_perm("nursing.view_task")

        if request.method in EDIT_METHODS:
            return user.has_perm("nursing.change_task")

        if request.method == "DELETE":
            return user.has_perm("nursing.remove_task")

        if request.method in SAFE_METHODS:
            return True

        return False
