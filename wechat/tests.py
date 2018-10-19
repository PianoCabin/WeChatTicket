from django.test import TestCase, Client
from wechat.models import *
from django.template.loader import get_template
import xml.etree.ElementTree as ET
from .wrapper import WeChatView
import xmltodict
from django.utils import timezone


class UnBindTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.open_id_1="asdfghjjl"
        cls.student_id_1="2016014234"
        cls.open_id_2="qwertyuiop"
        User.objects.create(open_id=cls.open_id_1,student_id=cls.student_id_1)
        User.objects.create(open_id=cls.open_id_2)
        cls.textMsg = {'ToUserName': 'TestName', 'FromUserName': cls.open_id_1, 'Content': '解绑'}
        pass

    def setUp(self):
        self.client = Client()
        pass

    def test_unbind(self):
        # test user who has bind
        msg = get_template('sendtext.xml').render(self.textMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content'][0:9]
        answer = '学号绑定已经解除。'
        self.assertEqual(content, answer)

        # test user unbind
        msg = get_template('sendtext.xml').render(self.textMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content'][0:9]
        answer = '学号绑定已经解除。'
        self.assertEqual(content, answer)
        pass


class BindTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.open_id_1 = "asdfghjjl"
        cls.student_id_1 = "2016014234"
        cls.open_id_2 = "qwertyuiop"
        User.objects.create(open_id=cls.open_id_1, student_id=cls.student_id_1)
        User.objects.create(open_id=cls.open_id_2)
        cls.clickMsg = {'ToUserName': 'TestName', 'FromUserName': cls.open_id_1, 'EventKey': 'SERVICE_BIND'}
        cls.textMsg = {'ToUserName': 'TestName', 'FromUserName': cls.open_id_1, 'Content': '绑定'}
        pass

    def setUp(self):
        self.client = Client()
        pass

    def test_bind(self):
        # test user unbind with textMsg
        self.textMsg['FromUserName'] = self.open_id_2
        msg = get_template('sendtext.xml').render(self.textMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content'][0:17]
        answer = '抢票等功能必须绑定学号后才能使用。'
        self.assertEqual(content, answer)

        # test user unbind with clickMsg
        self.clickMsg['FromUserName'] = self.open_id_2
        msg = get_template('sendclick.xml').render(self.clickMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content'][0:17]
        answer = '抢票等功能必须绑定学号后才能使用。'
        self.assertEqual(content, answer)

        # test user binded with testMsg
        self.textMsg['FromUserName'] = self.open_id_1
        msg = get_template('sendtext.xml').render(self.textMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content'][0:8]
        answer = '您已经绑定了学号'
        self.assertEqual(content, answer)

        # test user binded with ClickEvent
        self.clickMsg['FromUserName'] = self.open_id_1
        msg = get_template('sendclick.xml').render(self.clickMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content'][0:8]
        answer = '您已经绑定了学号'
        self.assertEqual(content, answer)
        pass


class BookEmptyTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.open_id_1 = "asdfghjjl"
        cls.student_id_1 = "2016014234"
        cls.open_id_2 = "qwertyuiop"
        User.objects.create(open_id=cls.open_id_1, student_id=cls.student_id_1)
        User.objects.create(open_id=cls.open_id_2)
        cls.clickMsg = {'ToUserName': 'TestName', 'FromUserName': cls.open_id_1, 'EventKey': 'BOOKING_EMPTY'}

    def setUp(self):
        self.client = Client()

    def test_book(self):
        #test correct input
        msg = get_template('sendclick.xml').render(self.clickMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        answer = '您好，现在没有推荐的抢票活动哟~'
        self.assertEqual(content, answer)


class BookWhatTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.open_id_1 = "asdfghjjl"
        cls.student_id_1 = "2016014234"
        cls.clickMsg = {'ToUserName': 'TestName', 'FromUserName': cls.open_id_1, 'EventKey': 'SERVICE_BOOK_WHAT'}
        cls.start_time1 = timezone.datetime(year=2018,month=11,day=1,hour=0,minute=0,second=0)
        cls.start_time2 = timezone.datetime(year=2018,month=12,day=1,hour=0,minute=0,second=0)
        cls.book_start = timezone.datetime(year=2018,month=10,day=1,hour=0,minute=0,second=0)
        cls.end_time1 = timezone.datetime(year=2018,month=12,day=1,hour=0,minute=0,second=0)
        cls.end_time2 = timezone.datetime(year=2018,month=12,day=30,hour=0,minute=0,second=0)
        cls.book_end = timezone.datetime(year=2018,month=10,day=25,hour=0,minute=0,second=0)
        act1 = Activity.objects.create(name="test1",key="test1",description="test1",start_time=cls.start_time1,end_time=cls.end_time1,book_start=cls.book_start,book_end=cls.book_end,total_tickets=100,remain_tickets=100,status=Activity.STATUS_PUBLISHED,pic_url="")
        act4 = Activity.objects.create(name="test1",key="test1",description="test1",start_time=cls.start_time2,end_time=cls.end_time2,book_start=cls.book_start,book_end=cls.book_end,total_tickets=100,remain_tickets=100,status=Activity.STATUS_PUBLISHED,pic_url="")
        act2 = Activity.objects.create(name="test1",key="test1",description="test1",start_time=cls.start_time1,end_time=cls.end_time1,book_start=cls.book_start,book_end=cls.book_end,total_tickets=100,remain_tickets=100,status=Activity.STATUS_DELETED,pic_url="")
        act3 = Activity.objects.create(name="test1",key="test1",description="test1",start_time=cls.start_time1,end_time=cls.end_time1,book_start=cls.book_start,book_end=cls.book_end,total_tickets=100,remain_tickets=100,status=Activity.STATUS_SAVED,pic_url="")
        User.objects.create(open_id=cls.open_id_1, student_id=cls.student_id_1)
        pass

    def setUp(self):
        self.client = Client()
        pass

    def test_bookWhat(self):

        # test activities with status != PUBLISHED
        msg = get_template('sendclick.xml').render(self.clickMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']["Articles"]['item']
        return_titles = []
        for article in content:
            return_titles.append(article['Title'])
        published = Activity.objects.filter(status=Activity.STATUS_PUBLISHED)
        published_titles = []
        for art in published:
            published_titles.append(art.name)
        self.assertEqual(return_titles, published_titles)

        # test with no activity
        Activity.objects.all().delete()
        msg = get_template('sendclick.xml').render(self.clickMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '当前活动尚不可抢票')
        pass
# Create your tests here.
class NonFunctionalHandlerTest(TestCase):
    # Test for help handler
    @classmethod
    def setUpTestData(cls):
        cls.open_id_1 = 'oxmsfsdfsaksfmksd'
        cls.open_id_2 = 'oxasfdsfdsafasdfd'
        cls.student_id_1 = '2000000000'
        cls.student_id_2 = '2016013240'
        User.objects.create(open_id=cls.open_id_1, student_id=cls.student_id_1)
        User.objects.create(open_id=cls.open_id_2, student_id=cls.student_id_2)
        cls.clickMsg = {'ToUserName': 'TestName', 'FromUserName': cls.open_id_1, 'EventKey': 'TEST'}
        cls.textMsg = {'ToUserName': 'TestName', 'FromUserName': cls.open_id_1, 'Content': 'TEST'}

    def setUp(self):
        self.client = Client()

    def test_click(self):
        # test default handler
        msg = get_template('sendclick.xml').render(self.clickMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '对不起，没有找到您需要的信息:(')

        # test help handler
        self.clickMsg['EventKey'] = 'SERVICE_HELP'
        msg = get_template('sendclick.xml').render(self.clickMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        title = xmltodict.parse(response.content)['xml']['Articles']['item']['Title']
        self.assertEqual(title, '“紫荆之声”使用指南')

    def test_text(self):
        # test default handler
        msg = get_template('sendtext.xml').render(self.textMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '对不起，没有找到您需要的信息:(')

        # test help handler
        self.textMsg['Content'] = '帮助'
        msg = get_template('sendtext.xml').render(self.textMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        title = xmltodict.parse(response.content)['xml']['Articles']['item']['Title']
        self.assertEqual(title, '“紫荆之声”使用指南')





