from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register("groups", views.GroupsviewSet)
router.register("permissions", views.PermissionsViewset)


urlpatterns = [
    path("", views.UserCreateList.as_view()),
    path("<int:pk>/", views.UserDetail.as_view()),
    path("<int:pk>/activate/", views.activate_user),
    path("<int:pk>/deactivate/", views.deactivate_user),
    path("", include(router.urls)),
]
