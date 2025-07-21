from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login),
    path("logout/", views.logout),
    path("users/<int:id>/password/reset/", views.reset_password),
    path("users/password/reset/", views.update_password),
]
