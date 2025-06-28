from django.test import TestCase, Client
from .models import User, Region


class TestViews(TestCase):

    def test_logout(self):
        region = Region.objects.create(region='Харківська область')
        User.objects.create_user(email='test@gmail.com', full_name='test_name', city='test', region=region, school='test', password='testpassword1')
        c = Client()
        c.login(email='test@gmail.com', password='testpassword1')
        response = c.get('/logout')
        self.assertRedirects(response, '/')

    def test_signup(self):
        c = Client()
        response = c.get('/register')
        self.assertEqual(response.status_code, 200)

        c.post('/register', {'email': 'testgmail.com', 'full_name': 'test_name', 'city': 'test',
                                        'region': 'test', 'password': 'testpassword1', 'school': 'test'})
        self.assertEquals(0, len(User.objects.filter(email='testgmail.com')))

        region = Region.objects.create(region='Харківська область')
        User.objects.create_user(email='test@gmail.com', full_name='test_name', city='test', region=region,
                                 school='test', password='testpassword1')
        c.login(email='test@gmail.com', password='testpassword1')
        response = c.get('/register')
        self.assertRedirects(response, '/')
