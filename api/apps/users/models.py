from django.db import models
from django.contrib.auth.models import User, Group


class UserExtras(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    menus = models.JSONField(default=list)

    def __str__(self):
        self.user.get_full_name()

    @classmethod
    def create_record(cls, user, **kwargs):
        object = cls.objects.create(user=user)
        return object


class GroupExtras(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    description = models.CharField(max_length=256, null=True)

    def __str__(self):
        return self.group.name

    @classmethod
    def create_record(cls, group, **kwargs):
        object = cls.objects.create(group=group, **kwargs)
        return object
