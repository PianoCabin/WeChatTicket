from django.test import TestCase, Client
from wechat.models import User,Ticket
from django.contrib.auth import get_user_model
from codex.baseerror import *
from .views import *

DefaultUser = get_user_model()

class LoginTest(TestCase):
    '''test for login api 4'''

    @classmethod
    def setUpClass(cls):
        super(LoginTest, cls).setUpClass()
        cls.username = 'root'
        cls.password = 'lyj271271'
        cls.user = DefaultUser.objects.create(username=cls.username)
        cls.user.set_password(cls.password)
        cls.user.save()

    def setUp(self):
        self.client = Client()

    def test(self):

        #初始没有登录的状态
        response = self.client.get('/api/a/login')
        self.assertEqual(response.json()['code'], 3)

        #错误登录
        response = self.client.post('/api/a/login', {"username": self.username + 'wrong', "password": self.password + 'wrong'})
        self.assertEqual(response.json()['code'], 3)

        #登录的状态
        response = self.client.get('/api/a/login')
        self.assertEqual(response.json()['code'], 3)

        #正确登录
        response = self.client.post('/api/a/login', {"username": self.username, "password": self.password})
        self.assertEqual(response.json()['code'], 0)

        #登录的状态
        response = self.client.get('/api/a/login')
        self.assertEqual(response.json()['code'], 0)

        #重复正确登录
        response = self.client.post('/api/a/login', {"username": self.username, "password": self.password})
        self.assertEqual(response.json()['code'], 0)

        #登录的状态
        response = self.client.get('/api/a/login')
        self.assertEqual(response.json()['code'], 0)

        #正确登录后的错误登录
        response = self.client.post('/api/a/login', {"username": self.username + 'wrong', "password": self.password + 'wrong'})
        self.assertEqual(response.json()['code'], 3)

        #登录的状态
        response = self.client.get('/api/a/login')
        self.assertEqual(response.json()['code'], 0)




