from django.test import TestCase, Client
from wechat.models import User
from codex.baseerror import *
from .views import *


# Create your tests here.
class BindTest(TestCase):
    # Test for bind API
    @classmethod
    def setUpTestData(cls):
        cls.open_id_1 = 'oxmsfsdfsaksfmksd'
        cls.open_id_2 = 'oxasfdsfdsafasdfd'
        cls.student_id_1 = '2000000000'
        cls.student_id_2 = '2016013240'
        User.objects.create(open_id=cls.open_id_1)
        User.objects.create(open_id=cls.open_id_2, student_id=cls.student_id_2)

    def setUp(self):
        self.client = Client()

    def test_get(self):
        # unbound openid
        response = self.client.get('/api/u/user/bind', {'openid': self.open_id_1})
        self.assertEqual(response.json()['data'], '')

        # bound openid
        response = self.client.get('/api/u/user/bind', {'openid': self.open_id_2})
        self.assertEqual(response.json()['data'], self.student_id_2)

        # no openid argument
        response = self.client.get('/api/u/user/bind')
        self.assertEqual(response.json()['code'], True)

    def test_post(self):
        # no openid
        response = self.client.post('/api/u/user/bind', {'student_id': self.student_id_1, 'password': '123'})
        self.assertEqual(response.json()['code'], True)

        # no student_id
        response = self.client.post('/api/u/user/bind', {'openid': self.open_id_1, 'password': '123'})
        self.assertEqual(response.json()['code'], True)

        # no password
        response = self.client.post('/api/u/user/bind', {'student_id': self.student_id_1, 'openid': self.open_id_1})
        self.assertEqual(response.json()['code'], True)

        # wrong student_id
        response = self.client.post('/api/u/user/bind', {'student_id': 'sfds2112fw', 'openid': self.open_id_1})
        self.assertEqual(response.json()['code'], True)


