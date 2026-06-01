from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from authentication.models import User


class AuthAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123',
            email='test@example.com', first_name='Test', last_name='User',
        )
        self.login_url = reverse('auth-login')
        self.register_url = reverse('auth-register')
        self.profile_url = reverse('auth-profile')

    def test_login_success(self):
        resp = self.client.post(self.login_url, {
            'username': 'testuser', 'password': 'testpass123',
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)
        self.assertIn('user', resp.data)

    def test_login_invalid_credentials(self):
        resp = self.client.post(self.login_url, {
            'username': 'testuser', 'password': 'wrongpass',
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_register_success(self):
        resp = self.client.post(self.register_url, {
            'username': 'newuser', 'password': 'newpass123',
            'password2': 'newpass123', 'email': 'new@example.com',
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_password_mismatch(self):
        resp = self.client.post(self.register_url, {
            'username': 'newuser', 'password': 'newpass123',
            'password2': 'different', 'email': 'new@example.com',
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(self.profile_url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['username'], 'testuser')

    def test_profile_unauthenticated(self):
        resp = self.client.get(self.profile_url)
        self.assertEqual(resp.status_code, 401)

    def test_profile_update(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.patch(self.profile_url, {
            'first_name': 'Updated', 'last_name': 'Name',
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')

    def test_password_change(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.patch(self.profile_url, {
            'current_password': 'testpass123',
            'password': 'newpass456',
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass456'))

    def test_password_change_wrong_current(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.patch(self.profile_url, {
            'current_password': 'wrongpass',
            'password': 'newpass456',
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_token_refresh(self):
        resp = self.client.post(self.login_url, {
            'username': 'testuser', 'password': 'testpass123',
        }, format='json')
        refresh_token = resp.data['refresh']
        resp2 = self.client.post(reverse('auth-refresh'), {
            'refresh': refresh_token,
        }, format='json')
        self.assertEqual(resp2.status_code, 200)
        self.assertIn('access', resp2.data)
