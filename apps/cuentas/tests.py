"""
Tests — app cuentas
Cobertura: login, logout, rate limiting, open redirect.
"""
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache


class LoginTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('login')
        self.user = User.objects.create_user(
            username='testuser',
            password='Pass1234!',
        )
        # Limpiar cache entre tests para no arrastrar bloqueos
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_get_muestra_formulario(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'login')

    def test_login_exitoso_redirige_a_dashboard(self):
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password': 'Pass1234!',
        })
        self.assertRedirects(response, reverse('gestion:dashboard'))

    def test_login_credenciales_invalidas_muestra_error(self):
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password': 'wrong',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'incorrectos')

    def test_open_redirect_bloqueado(self):
        """El parámetro next con URL externa debe redirigir al dashboard."""
        response = self.client.post(
            self.url + '?next=https://evil.com',
            {'username': 'testuser', 'password': 'Pass1234!'},
        )
        self.assertRedirects(response, reverse('gestion:dashboard'))

    def test_next_interno_respetado(self):
        """Un next interno válido sí debe respetarse."""
        destino = reverse('gestion:causas_lista')
        response = self.client.post(
            self.url + f'?next={destino}',
            {'username': 'testuser', 'password': 'Pass1234!'},
        )
        self.assertRedirects(response, destino)

    def test_rate_limit_bloquea_tras_5_intentos(self):
        """Después de 5 fallos la IP queda bloqueada y retorna contexto bloqueado."""
        for _ in range(5):
            self.client.post(self.url, {
                'username': 'testuser',
                'password': 'bad',
            })
        # El 6.º intento (o la próxima carga) debe mostrar bloqueo
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context.get('bloqueado', False))

    def test_login_exitoso_limpia_bloqueo(self):
        """Un login exitoso limpia los intentos fallidos acumulados."""
        for _ in range(3):
            self.client.post(self.url, {'username': 'testuser', 'password': 'bad'})
        # Login correcto
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password': 'Pass1234!',
        })
        self.assertRedirects(response, reverse('gestion:dashboard'))


class LogoutTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='logoutuser', password='Pass1234!')
        self.client.login(username='logoutuser', password='Pass1234!')

    def test_logout_redirige_a_login(self):
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    def test_logout_sin_autenticacion_redirige(self):
        self.client.logout()
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
