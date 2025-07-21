from django.test import TestCase

from api.apps.users import models


class UserTest(TestCase):
    def setUp(self) -> None:
        self.user_one = models.User.objects.create_user(
            username="test", email="mail@mail.com", password="pass432dsd**"
        )
        self.user_two = models.User.objects.create_user(
            username="test_2", email="amail@mail.com", password="sdsd34d**"
        )

    def test_list_users(self):
        users = models.User.objects.all()
        self.assertEqual(2, len(users))

    def test_user_details(self):
        user = models.User.objects.get(username="test")
        self.assertEqual(type(user), models.User)
        self.assertIsNotNone(user.auth_token)
