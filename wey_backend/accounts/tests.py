from django.test import TestCase
from django.contrib.auth import get_user_model


class UserManagerTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            email="normal@abc.com", name="normal", password="foo"
        )
        self.assertEqual(user.email, "normal@abc.com")
        self.assertEqual(user.name, "normal")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        with self.assertRaises(ValueError):
            User.objects.create_user()
        with self.assertRaises(ValueError):
            User.objects.create_user(email="")
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="foo")

    def test_create_superuser(self):
        User = get_user_model()
        super_user = User.objects.create_superuser(
            email="super@abc.com", name="super", password="boo"
        )
        self.assertEqual(super_user.email, "super@abc.com")
        self.assertEqual(super_user.name, "super")
        self.assertTrue(super_user.is_active)
        self.assertTrue(super_user.is_staff)
        self.assertTrue(super_user.is_superuser)

        with self.assertRaises(ValueError):
            User.objects.create_superuser(email="", password="foo")
