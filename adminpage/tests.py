from django.test import TestCase, Client
from wechat.models import *
from .views import *
from django.utils import timezone as datetime
from django.contrib.auth import get_user_model
import json

DefaultUser = get_user_model()


# Create your tests here.
class ImageUploadTest(TestCase):

    # Test for image upload API
    @classmethod
    def setUpTestData(cls):
        cls.username = 'root'
        cls.password = 'root'
        cls.user = DefaultUser.objects.create(username=cls.username)
        cls.user.set_password(cls.password)
        cls.user.save()

    def setUp(self):
        self.client = Client()

    def test_post(self):
        # test administrator not login
        with open('./adminpage/testImg/test.jpg', 'rb') as file:
            response = self.client.post('/api/a/image/upload', {'image': file})
            self.assertNotEqual(response.json()['code'], 0)

        # test correct upload process
        with open('./adminpage/testImg/test.jpg', 'rb') as file:
            self.client.login(username=self.username, password=self.password)
            response = self.client.post('/api/a/image/upload', {'image': file})
            self.assertEqual(response.json()['code'], 0)
            response = self.client.get(response.json()['data'])
            self.assertEqual(response.status_code, 200)

        # test no image field
        response = self.client.post('/api/a/image/upload', {'other': ''})
        self.assertNotEqual(response.json()['code'], 0)

        # test no image
        response = self.client.post('/api/a/image/upload', {'image': ''})
        self.assertNotEqual(response.json()['code'], 0)


class ActivityMenuTest(TestCase):

    # Test for activity menu API
    @classmethod
    def setUpTestData(cls):
        cls.username = 'root'
        cls.password = 'root'
        cls.user = DefaultUser.objects.create(username=cls.username)
        cls.user.set_password(cls.password)
        cls.user.save()

        cls.activitiesInfo = list()
        cls.unpublished = list()
        for i in range(6):
            activity = Activity.objects.create(name='test' + str(i), key='test' + str(i), description='myTest',
                                               start_time='2018-12-02T08:00:00.000Z',
                                               end_time='2018-12-02T10:00:00.000Z', place='github',
                                               book_start='2018-11-02T08:00:00.000Z',
                                               book_end='2018-11-02T10:00:00.000Z',
                                               total_tickets=100, pic_url='xxx', remain_tickets=100, status=0)
            # activate only 4 activities
            if i < 4:
                activity.status = 1
                cls.activitiesInfo.append({'id': activity.id, 'name': activity.name, 'menuIndex': i + 1})
            else:
                cls.unpublished.append(activity)

    def setUp(self):
        self.client = Client()

    def test_get(self):
        # test administrator not login
        response = self.client.get('/api/a/activity/menu')
        self.assertNotEqual(response.json()['code'], 0)

        # test length of activities below 5
        self.client.login(username=self.username, password=self.password)
        response = self.client.get('/api/a/activity/menu')
        self.assertNotEqual(json.dumps(response.json()['data']), json.dumps(self.activitiesInfo))

        # test length of activities equals 5
        activity = self.unpublished[0]
        activity.status = 1
        activity.save()
        self.unpublished.pop(0)
        self.activitiesInfo.append({'id': activity.id, 'name': activity.name, 'menuIndex': 5})
        response = self.client.get('/api/a/activity/menu')
        self.assertNotEqual(json.dumps(response.json()['data']), json.dumps(self.activitiesInfo))

        # test length of activities above 5
        activity = self.unpublished[0]
        activity.status = 1
        activity.save()
        self.unpublished.pop(0)
        self.activitiesInfo.append({'id': activity.id, 'name': activity.name, 'menuIndex': 5})
        self.activitiesInfo[0]['menuIndex'] = 0
        for i in range(1, 6):
            self.activitiesInfo[i]['menuIndex'] = i
        response = self.client.get('/api/a/activity/menu')
        self.assertNotEqual(json.dumps(response.json()['data']), json.dumps(self.activitiesInfo))

    def test_post(self):
        ids = [activity.id for activity in Activity.objects.all()]

        # test administrator not login
        response = self.client.post('/api/a/activity/menu', ids[:5], content_type='application/json')
        self.assertNotEqual(response.json()['code'], 0)

        # test no id array
        self.client.login(username=self.username, password=self.password)
        response = self.client.post('/api/a/activity/menu', {"other": 0})
        self.assertNotEqual(response.json()['code'], 0)

        # test blank id array
        response = self.client.post('/api/a/activity/menu', [], content_type='application/json')
        self.assertEqual(response.json()['code'], 0)
        for activity in Activity.objects.all():
            self.assertEqual(activity.status, 0)

        # test array length below,equals or above 5
        for i in range(4, 7):
            response = self.client.post('/api/a/activity/menu', ids[:i], content_type='application/json')
            self.assertEqual(response.json()['code'], 0)
            for j, activity in enumerate(Activity.objects.all()):
                if j < i:
                    self.assertEqual(activity.status, 1)
                else:
                    self.assertEqual(activity.status, 0)

        # test array contains id out of range
        response = self.client.post('/api/a/activity/menu', [-1, 7], content_type='application/json')
        self.assertNotEqual(response.json()['code'], 0)


class ActivityCheckIn(TestCase):

    # Test for check in API
    @classmethod
    def setUpTestData(cls):
        cls.username = 'root'
        cls.password = 'root'
        cls.user = DefaultUser.objects.create(username=cls.username)
        cls.user.set_password(cls.password)
        cls.user.save()

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
                              status=1)

        Ticket.objects.create(student_id=cls.student_id_2, unique_id=cls.unique_id_2,
                              activity=Activity.objects.get(id=cls.activity.id),
                              status=1)

        cls.activity = Activity.objects.get(id=cls.activity.id)
        cls.ticket_1 = Ticket.objects.get(student_id=cls.student_id_1)
        cls.ticket_1_info = {'actId': cls.ticket_1.activity.id, 'ticket': cls.ticket_1.unique_id}

    def setUp(self):
        self.client = Client()

    def test_post(self):
        # test administrator not login
        response = self.client.post('/api/a/activity/checkin', self.ticket_1_info)
        self.assertNotEqual(response.json()['code'], 0)

        # test nonexistent actId
        self.client.login(username=self.username, password=self.password)
        test_info = self.ticket_1_info.copy()
        test_info.pop('actId')
        response = self.client.post('/api/a/activity/checkin', test_info)
        self.assertNotEqual(response.json()['code'], 0)

        # test nonexistent ticket and studentId
        test_info = self.ticket_1_info.copy()
        test_info.pop('ticket')
        response = self.client.post('/api/a/activity/checkin', test_info)
        self.assertNotEqual(response.json()['code'], 0)

        # test coexistence of ticket and studentId
        test_info = self.ticket_1_info.copy()
        test_info['studentId'] = self.student_id_1
        response = self.client.post('/api/a/activity/checkin', test_info)
        self.assertNotEqual(response.json()['code'], 0)

        # test unmatched actId and ticket
        test_info = self.ticket_1_info.copy()
        test_info['ticket'] = self.ticket_1.id + 1
        response = self.client.post('/api/a/activity/checkin', test_info)
        self.assertNotEqual(response.json()['code'], 0)

        # test unmatched actId and studentId
        test_info = self.ticket_1_info.copy()
        test_info.pop('ticket')
        test_info['actId'] = self.activity.id + 1
        test_info['studentId'] = self.student_id_1
        response = self.client.post('/api/a/activity/checkin', test_info)
        self.assertNotEqual(response.json()['code'], 0)

        # test used or canceled ticket
        test_info = self.ticket_1_info.copy()
        response = self.client.post('/api/a/activity/checkin', test_info)
        test_info = {'ticket': self.ticket_1.unique_id, 'studentId': self.student_id_1}
        self.assertJSONEqual(json.dumps(response.json()['data']), json.dumps(test_info))
        self.assertEqual(Ticket.objects.get(student_id=self.student_id_1).status, Ticket.STATUS_USED)
