import random

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone


class PasswordRecovery(models.Model):
    user = models.OneToOneField(User, null=False, on_delete=models.CASCADE)
    recovery_password = models.CharField(max_length=256, null=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)

    @property
    def password(self) -> str:
        password = str(random.randrange(11111111, 99999999))
        hashed_password = make_password(password)
        self.recovery_password = hashed_password
        self.is_active = True
        self.save()
        return password

    def confirm_password(self, password: str) -> bool:
        if self.setup_password_recovery is None:
            return False
        return check_password(password, self.recovery_password)

    @classmethod
    def setup_password_recovery(cls, user: User) -> str:
        """Setup password recovery record for user with no provious record

        Args:
            user[User]: user object

        Returns:
            str: recovery password
        """
        password = str(random.randrange(11111111, 99999999))
        hashed_password = make_password(password)
        cls.objects.create(
            user=user,
            recovery_password=hashed_password,
            is_active=True,
        )
        return password

    def complete_recovery(self, new_password: str) -> None:
        """Completes Password recovery Process

        Args:
            new_password[str]: new password for user

        Returns:
            None
        """
        self.recovery_password = None
        self.is_active = False
        self.user.set_password(new_password)
        self.user.save()
        self.save()
        return None
