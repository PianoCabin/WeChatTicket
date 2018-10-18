from django.test import TestCase, Client
from wechat.models import Activity
from django.contrib.auth import get_user_model
from .views import *

DefaultUser = get_user_model()

class Test_login(TestCase):

    """test for api 4"""

    @classmethod
    def setUpClass(cls):
        super(Test_login, cls).setUpClass()
        cls.username = 'root'
        cls.password = 'lyj271271'
        cls.user = DefaultUser.objects.create(username=cls.username)
        cls.user.set_password(cls.password)
        cls.user.save()

    def setUp(self):
        self.client = Client()

    def test_login(self):

        # 初始没有登录的状态
        response = self.client.get('/api/a/login')
        self.assertEqual(response.json()['code'], 3)

        # 错误登录
        response = self.client.post('/api/a/login', {"username": self.username + 'wrong', "password": self.password + 'wrong'})
        self.assertEqual(response.json()['code'], 3)

        # 登录的状态
        response = self.client.get('/api/a/login')
        self.assertEqual(response.json()['code'], 3)

        # 正确登录
        response = self.client.post('/api/a/login', {"username": self.username, "password": self.password})
        self.assertEqual(response.json()['code'], 0)

        # 登录的状态
        response = self.client.get('/api/a/login')
        self.assertEqual(response.json()['code'], 0)

        # 重复正确登录
        response = self.client.post('/api/a/login', {"username": self.username, "password": self.password})
        self.assertEqual(response.json()['code'], 0)

        # 登录的状态
        response = self.client.get('/api/a/login')
        self.assertEqual(response.json()['code'], 0)

        # 正确登录后的错误登录
        response = self.client.post('/api/a/login', {"username": self.username + 'wrong', "password": self.password + 'wrong'})
        self.assertEqual(response.json()['code'], 3)

        # 登录的状态
        response = self.client.get('/api/a/login')
        self.assertEqual(response.json()['code'], 0)

class Test_logout(TestCase):

    """test for api 5"""

    @classmethod
    def setUpClass(cls):
        super(Test_logout, cls).setUpClass()
        cls.username = 'root'
        cls.password = 'lyj271271'
        cls.user = DefaultUser.objects.create(username=cls.username)
        cls.user.set_password(cls.password)
        cls.user.save()

    def setUp(self):
        self.client = Client()

    def test_logout(self):

        # 未登录就退出
        response = self.client.post('/api/a/logout', content_type='application/json')
        self.assertEqual(response.json()['code'], 3)

        # 正确登录
        response = self.client.post('/api/a/login', {"username": self.username, "password": self.password})
        self.assertEqual(response.json()['code'], 0)

        # 登录后退出
        response = self.client.post('/api/a/logout', content_type='application/json')
        self.assertEqual(response.json()['code'], 0)


class Test_activity_list(TestCase):

    """test for api 6"""

    @classmethod
    def setUpClass(cls):
        super(Test_activity_list, cls).setUpClass()
        cls.username = 'root'
        cls.password = 'lyj271271'
        cls.user = DefaultUser.objects.create(username=cls.username)
        cls.user.set_password(cls.password)
        cls.user.save()
        # 假定存入数据库的数据逻辑上正确
        Activity.objects.create(
            name='1', key='1', place='1', description='1', pic_url='',
            start_time='2011-05-18 16:28:07.198690+00:00', end_time='2011-10-18 16:28:07.198690+00:00',
            book_start='2011-06-18 16:28:07.198690+00:00', book_end='2011-09-18 16:28:07.198690+00:00',
            total_tickets=100, status=-1, remain_tickets=100)
        Activity.objects.create(
            name='2', key='2', place='2', description='2', pic_url='',
            start_time='2012-05-18 16:28:07.198690+00:00', end_time='2012-10-18 16:28:07.198690+00:00',
            book_start='2012-06-18 16:28:07.198690+00:00', book_end='2012-09-18 16:28:07.198690+00:00',
            total_tickets=200, status=0, remain_tickets=200)
        Activity.objects.create(
            name='3', key='3', place='3', description='3', pic_url='',
            start_time='2013-05-18 16:28:07.198690+00:00', end_time='2013-10-18 16:28:07.198690+00:00',
            book_start='2013-06-18 16:28:07.198690+00:00', book_end='2013-09-18 16:28:07.198690+00:00',
            total_tickets=300, status=1, remain_tickets=300)

    def setUp(self):
        self.client = Client()

    def test_activity_list(self):

        # 正确登录
        self.client.post('/api/a/login', {"username": self.username, "password": self.password})

        response = self.client.get('/api/a/activity/list')

        for i in response.json()['data']:
            self.assertGreaterEqual(i["status"], 0)

class Test_activity_delete(TestCase):

    """test for api 7"""

    @classmethod
    def setUpClass(cls):
        super(Test_activity_delete, cls).setUpClass()
        cls.username = 'root'
        cls.password = 'lyj271271'
        cls.user = DefaultUser.objects.create(username=cls.username)
        cls.user.set_password(cls.password)
        cls.user.save()
        # 假定存入数据库的数据逻辑上正确
        Activity.objects.create(
            name='1', key='1', place='1', description='1', pic_url='',
            start_time='2011-05-18 16:28:07.198690+00:00', end_time='2011-10-18 16:28:07.198690+00:00',
            book_start='2011-06-18 16:28:07.198690+00:00', book_end='2011-09-18 16:28:07.198690+00:00',
            total_tickets=100, status=-1, remain_tickets=100)
        Activity.objects.create(
            name='2', key='2', place='2', description='2', pic_url='',
            start_time='2012-05-18 16:28:07.198690+00:00', end_time='2012-10-18 16:28:07.198690+00:00',
            book_start='2012-06-18 16:28:07.198690+00:00', book_end='2012-09-18 16:28:07.198690+00:00',
            total_tickets=200, status=0, remain_tickets=200)
        Activity.objects.create(
            name='3', key='3', place='3', description='3', pic_url='',
            start_time='2013-05-18 16:28:07.198690+00:00', end_time='2013-10-18 16:28:07.198690+00:00',
            book_start='2013-06-18 16:28:07.198690+00:00', book_end='2013-09-18 16:28:07.198690+00:00',
            total_tickets=300, status=1, remain_tickets=300)

    def setUp(self):
        self.client = Client()

    def test_activity_delete(self):

        # 正确登录
        self.client.post('/api/a/login', {"username": self.username, "password": self.password})

        responses = self.client.get('/api/a/activity/list')

        for i in responses.json()['data']:
            # 删除存在的记录
            response = self.client.post('/api/a/activity/delete', {"id": i['id']})
            self.assertEqual(response.json()['code'], 0)

        # 删除不存在的记录
        response = self.client.post('/api/a/activity/delete', {"id": 100})
        self.assertEqual(response.json()['code'], 2)

class Test_activity_create(TestCase):

    """test for api 8"""

    @classmethod
    def setUpClass(cls):
        super(Test_activity_create, cls).setUpClass()
        cls.username = 'root'
        cls.password = 'lyj271271'
        cls.user = DefaultUser.objects.create(username=cls.username)
        cls.user.set_password(cls.password)
        cls.user.save()

    def setUp(self):
        self.client = Client()

    def test_activity_create(self):

        # 正确登录
        self.client.post('/api/a/login', {"username": self.username, "password": self.password})

        # 正确创建活动
        new_activity_1 = {"name": "a", "key": "a", "place": "a", "description": "a", "picUrl": "/uimg/1.jpg", "totalTickets": "100",
                          "status": 1, "startTime": "2018-10-31T16:00:00.000Z", "endTime": "2018-11-01T16:00:00.000Z",
                          "bookStart": "2018-10-25T16:00:00.000Z", "bookEnd": "2018-10-26T16:00:00.000Z"}

        response = self.client.post('/api/a/activity/create', new_activity_1)
        self.assertEqual(response.json()['code'], 0)

        # 错误创建活动，格式不对,缺status
        new_activity_2 = {'name': '4', 'key': '4', 'place': '4', 'description': '4', 'pic_url': '/uimg1.jpg',
                          'start_time': '2019-05-18T16:28:00.070Z',
                          'end_time': '2019-10-18T16:28:00.070Z',
                          'book_start': '2019-03-18T16:28:00.070Z',
                          'book_end': '2019-04-18T16:28:00.070Z',
                          'total_tickets': '400'}

        response = self.client.post('/api/a/activity/create', new_activity_2)
        self.assertEqual(response.json()['code'], 1)


class Test_activity_detail(TestCase):

    """test for api 10"""

    @classmethod
    def setUpClass(cls):
        super(Test_activity_detail, cls).setUpClass()
        cls.username = 'root'
        cls.password = 'lyj271271'
        cls.user = DefaultUser.objects.create(username=cls.username)
        cls.user.set_password(cls.password)
        cls.user.save()
        Activity.objects.create(
                        name='1', key='1', place='1', description='1', pic_url='',
                        start_time='2011-05-18 16:28:07.198690+00:00', end_time='2011-10-18 16:28:07.198690+00:00',
                        book_start='2011-06-18 16:28:07.198690+00:00', book_end='2011-09-18 16:28:07.198690+00:00',
                        total_tickets=100, status=-1, remain_tickets=100)
        Activity.objects.create(
                        name='2', key='2', place='2', description='2', pic_url='',
                        start_time='2012-05-18 16:28:07.198690+00:00', end_time='2012-10-18 16:28:07.198690+00:00',
                        book_start='2012-06-18 16:28:07.198690+00:00', book_end='2012-09-18 16:28:07.198690+00:00',
                        total_tickets=200, status=0, remain_tickets=200)
        Activity.objects.create(
                        name='3', key='3', place='3', description='3', pic_url='',
                        start_time='2013-05-18 16:28:07.198690+00:00', end_time='2013-10-18 16:28:07.198690+00:00',
                        book_start='2013-06-18 16:28:07.198690+00:00', book_end='2013-09-18 16:28:07.198690+00:00',
                        total_tickets=300, status=1, remain_tickets=300)

    def setUp(self):
        self.client = Client()

    def test_activity_detail(self):

        # 正确登录
        self.client.post('/api/a/login', {"username": self.username, "password": self.password})

        # 获取已有活动详情
        response = self.client.get('/api/a/activity/detail', {"id": 6})
        self.assertEqual(response.json()['code'], 0)

        # 获取未有活动详情
        response = self.client.get('/api/a/activity/detail', {"id": 100})
        self.assertEqual(response.json()['code'], 2)

        # 修改未发布，未开始，未结束的活动详情
        activity2 = {"id": 6, "name": "22", "place": "22", "description": "22", "picUrl": "",
                     "totalTickets": "100", "status": 1, "startTime": "1337358487.19869",
                     "endTime": "1350577687.19869", "bookStart": "1340036887.19869",
                     "bookEnd": "1347985687.19869"}

        response = self.client.post('/api/a/activity/detail', activity2)
        self.assertEqual(response.json()['code'], -1)

        # 修改规则已在前端写好




