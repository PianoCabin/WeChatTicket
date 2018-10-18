from django.test import TestCase, Client
from wechat.models import *
from .views import *
from django.utils import timezone as datetime
import json


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
        self.assertNotEqual(response.json()['code'], 0)

    def test_post(self):
        # no openid
        response = self.client.post('/api/u/user/bind', {'student_id': self.student_id_1, 'password': '123'})
        self.assertNotEqual(response.json()['code'], 0)

        # no student_id
        response = self.client.post('/api/u/user/bind', {'openid': self.open_id_1, 'password': '123'})
        self.assertNotEqual(response.json()['code'], 0)

        # no password
        response = self.client.post('/api/u/user/bind', {'student_id': self.student_id_1, 'openid': self.open_id_1})
        self.assertNotEqual(response.json()['code'], 0)

        # wrong student_id
        response = self.client.post('/api/u/user/bind', {'student_id': 'sfds2112fw', 'openid': self.open_id_1})
        self.assertNotEqual(response.json()['code'], 0)


class ActivityDeTailTest(TestCase):

    # Test for activity detail API
    @classmethod
    def setUpTestData(cls):
        cls.activity = Activity.objects.create(name='test', key='test', description='myTest',
                                               start_time='2018-12-02T08:00:00.000Z',
                                               end_time='2018-12-02T10:00:00.000Z', place='github',
                                               book_start='2018-11-02T08:00:00.000Z',
                                               book_end='2018-11-02T10:00:00.000Z',
                                               total_tickets=100, pic_url='xxx', remain_tickets=100, status=0)
        cls.activity = Activity.objects.get(id=cls.activity.id)
        cls.activityInfo = {"name": cls.activity.name, "key": cls.activity.key, "description": cls.activity.description,
                            "startTime": cls.activity.start_time.timestamp(),
                            "endTime": cls.activity.end_time.timestamp(),
                            "place": cls.activity.place, "bookStart": cls.activity.book_start.timestamp(),
                            "bookEnd": cls.activity.book_end.timestamp(), "totalTickets": cls.activity.total_tickets,"remainTickets":cls.activity.remain_tickets,
                            "picUrl": cls.activity.pic_url, "currentTime": datetime.now().timestamp()}

    def setUp(self):
        self.client = Client()

    def test_get(self):
        # test no id argument
        response = self.client.get('/api/u/activity/detail')
        self.assertNotEqual(response.json()['code'], 0)

        # test id doesn't exist
        response = self.client.get('/api/u/activity/detail', {'id': 2})
        self.assertNotEqual(response.json()['code'], 0)

        # test activity not issued
        response = self.client.get('/api/u/activity/detail', {'id': self.activity.id})
        self.assertNotEqual(response.json()['code'], 0)

        # test issued activity
        self.activity.status = 1
        self.activity.save()
        response = self.client.get('/api/u/activity/detail', {'id': self.activity.id})
        self.activityInfo['currentTime'] = response.json()['data']['currentTime']
        self.assertJSONEqual(json.dumps(response.json()['data']), json.dumps(self.activityInfo))


class TicketDetailActivity(TestCase):

    # Test for ticket detail API
    @classmethod
    def setUpTestData(cls):
        cls.open_id_1 = 'oxmsfsdfsaksfmksd'
        cls.open_id_2 = 'oxasfdsfdsafasdfd'
        cls.student_id_1 = '2000000000'
        cls.student_id_2 = '2016013240'
        cls.unique_id_1 = 'dsafdasfefweksa'
        cls.unique_id_2 = 'kjknknkjnkkkkds'

        User.objects.create(open_id=cls.open_id_1, student_id=cls.student_id_1)

        User.objects.create(open_id=cls.open_id_2, student_id=cls.student_id_2)

        cls.activity = Activity.objects.create(name='test', key='test', description='myTest',
                                               start_time='2018-12-02T08:00:00.000Z',
                                               end_time='2018-12-02T10:00:00.000Z', place='github',
                                               book_start='2018-11-02T08:00:00.000Z',
                                               book_end='2018-11-02T10:00:00.000Z',
                                               total_tickets=100, pic_url='xxx', remain_tickets=100, status=0)

        Ticket.objects.create(student_id=cls.student_id_1, unique_id=cls.unique_id_1,
                              activity=Activity.objects.get(id=cls.activity.id),
                              status=0)

        Ticket.objects.create(student_id=cls.student_id_2, unique_id=cls.unique_id_2,
                              activity=Activity.objects.get(id=cls.activity.id),
                              status=0)

        cls.activity = Activity.objects.get(id=cls.activity.id)
        cls.ticket_1 = Ticket.objects.get(student_id=cls.student_id_1)
        cls.ticket_1_info = {"activityName": cls.activity.name, "place": cls.activity.place,
                             "activityKey": cls.activity.key,
                             "uniqueId": cls.ticket_1.unique_id, "startTime": cls.activity.start_time.timestamp(),
                             "endTime": cls.activity.end_time.timestamp(),
                             "currentTime": datetime.datetime.now().timestamp(),
                             "status": cls.ticket_1.status}

    def setUp(self):
        self.client = Client()

    def test_get(self):
        # test no openid
        response = self.client.get('/api/u/ticket/detail', {'ticket': self.unique_id_1})
        self.assertNotEqual(response.json()['code'], 0)

        # test no ticket
        response = self.client.get('/api/u/ticket/detail', {'openid': self.open_id_1})
        self.assertNotEqual(response.json()['code'], 0)

        # test nonexistent openid
        response = self.client.get('/api/u/ticket/detail', {'openid': 'sdfsdafsdfs', 'ticket': self.unique_id_1})
        self.assertNotEqual(response.json()['code'], 0)

        # test nonexistent ticket
        response = self.client.get('/api/u/ticket/detail', {'openid': self.open_id_1, 'ticket': 'dfsafsdfsd'})
        self.assertNotEqual(response.json()['code'], 0)

        # test unmatched openid and ticket
        response = self.client.get('/api/u/ticket/detail', {'openid': self.open_id_1, 'ticket': self.unique_id_2})
        self.assertNotEqual(response.json()['code'], 0)

        # test correct response
        response = self.client.get('/api/u/ticket/detail', {'openid': self.open_id_1, 'ticket': self.unique_id_1})
        self.ticket_1_info['currentTime'] = response.json()['data']['currentTime']
        self.assertJSONEqual(json.dumps(response.json()['data']), json.dumps(self.ticket_1_info))
