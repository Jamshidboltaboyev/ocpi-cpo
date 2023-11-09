from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from core.models import UploadedImage

User = get_user_model()


class LoginTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone="1234567890", password="testpassword")
        self.url = '/api/v1/account/login/'

    def test_successful_login(self):
        data = {
            "phone": "1234567890",
            "password": "testpassword"
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_incorrect_credentials(self):
        data = {
            "phone": "1234567890",
            "password": "wrongpassword"
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_credentials(self):
        data = {
            "phone": "1234567890"
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_phone(self):
        data = {
            "phone": "invalid_phone",
            "password": "testpassword"
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AccountViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone='+1234567890', password='testpassword', full_name='Test User', birth_date='1990-01-01')
        self.client.force_authenticate(user=self.user)
        self.avatar = UploadedImage.objects.create(image='testimage.jpg')

        self.url = '/api/v1/account/me/'

    def test_get_current_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_valid_data(self):
        data = {
            'full_name': 'Updated Name',
            'birth_date': '01.01.1990',
            'phone': '+1234567890',
            'avatar_id': self.avatar.id,
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_invalid_data(self):
        data = {
            'full_name': '',
            'birth_date': '01.01.1990',
            'phone': '+1234567890',
            'avatar_id': self.avatar.id,
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_invalid_avatar_id(self):
        data = {
            'full_name': 'Updated Name',
            'birth_date': '01.01.1990',
            'phone': '+1234567890',
            'avatar_id': 100,  # Non-existent avatar ID
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_invalid_phone_number(self):
        data = {
            'full_name': 'Updated Name',
            'birth_date': '01.01.1990',
            'phone': 'invalid_phone_number',
            'avatar_id': self.avatar.id,
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)