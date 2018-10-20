from django.test import TestCase, Client, TransactionTestCase
from wechat.models import *
from django.template.loader import get_template
from .wrapper import WeChatView
import xmltodict
from WeChatTicket.settings import *
import json
from django.utils import timezone
from datetime import timedelta


class UnBindTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.open_id_1 = "asdfghjjl"
        cls.student_id_1 = "2016014234"
        cls.open_id_2 = "qwertyuiop"
        User.objects.create(open_id=cls.open_id_1, student_id=cls.student_id_1)
        User.objects.create(open_id=cls.open_id_2)
        cls.textMsg = {'ToUserName': 'TestName', 'FromUserName': cls.open_id_1, 'Content': '解绑'}

    def setUp(self):
        self.client = Client()

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

    def setUp(self):
        self.client = Client()

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
        # test correct input
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
        cls.start_time1 = timezone.datetime(year=2018, month=11, day=1, hour=0, minute=0, second=0)
        cls.start_time2 = timezone.datetime(year=2018, month=12, day=1, hour=0, minute=0, second=0)
        cls.book_start = timezone.datetime(year=2018, month=10, day=1, hour=0, minute=0, second=0)
        cls.end_time1 = timezone.datetime(year=2018, month=12, day=1, hour=0, minute=0, second=0)
        cls.end_time2 = timezone.datetime(year=2018, month=12, day=30, hour=0, minute=0, second=0)
        cls.book_end = timezone.datetime(year=2018, month=10, day=25, hour=0, minute=0, second=0)
        act1 = Activity.objects.create(name="test1", key="test1", description="test1", start_time=cls.start_time1,
                                       end_time=cls.end_time1, book_start=cls.book_start, book_end=cls.book_end,
                                       total_tickets=100, remain_tickets=100, status=Activity.STATUS_PUBLISHED,
                                       pic_url="")
        act4 = Activity.objects.create(name="test1", key="test1", description="test1", start_time=cls.start_time2,
                                       end_time=cls.end_time2, book_start=cls.book_start, book_end=cls.book_end,
                                       total_tickets=100, remain_tickets=100, status=Activity.STATUS_PUBLISHED,
                                       pic_url="")
        act2 = Activity.objects.create(name="test1", key="test1", description="test1", start_time=cls.start_time1,
                                       end_time=cls.end_time1, book_start=cls.book_start, book_end=cls.book_end,
                                       total_tickets=100, remain_tickets=100, status=Activity.STATUS_DELETED,
                                       pic_url="")
        act3 = Activity.objects.create(name="test1", key="test1", description="test1", start_time=cls.start_time1,
                                       end_time=cls.end_time1, book_start=cls.book_start, book_end=cls.book_end,
                                       total_tickets=100, remain_tickets=100, status=Activity.STATUS_SAVED, pic_url="")
        User.objects.create(open_id=cls.open_id_1, student_id=cls.student_id_1)

    def setUp(self):
        self.client = Client()

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

class CheckTicketTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass
        cls.open_id_1 = "asdfghjjl"
        cls.student_id_1 = "2016014234"
        cls.open_id_2 = "zxcvbn"
        cls.student_id_2 = "2016014235"
        cls.open_id_3 = "dkfjghl"

        cls.clickMsg = {'ToUserName': 'TestName', 'FromUserName': cls.open_id_1, 'EventKey': 'SERVICE_GET_TICKET'}
        cls.start_time1 = timezone.datetime(year=2018, month=11, day=1, hour=0, minute=0, second=0)
        cls.start_time2 = timezone.datetime(year=2018, month=12, day=1, hour=0, minute=0, second=0)
        cls.book_start = timezone.datetime(year=2018, month=10, day=1, hour=0, minute=0, second=0)
        cls.end_time1 = timezone.datetime(year=2018, month=12, day=1, hour=0, minute=0, second=0)
        cls.end_time2 = timezone.datetime(year=2018, month=12, day=30, hour=0, minute=0, second=0)
        cls.book_end = timezone.datetime(year=2018, month=10, day=25, hour=0, minute=0, second=0)
        act1 = Activity.objects.create(name="test1", key="test1", description="test1", start_time=cls.start_time1,
                                       end_time=cls.end_time1, book_start=cls.book_start, book_end=cls.book_end,
                                       total_tickets=100, remain_tickets=100, status=Activity.STATUS_PUBLISHED,
                                       pic_url="")
        act4 = Activity.objects.create(name="test1", key="test1", description="test1", start_time=cls.start_time2,
                                       end_time=cls.end_time2, book_start=cls.book_start, book_end=cls.book_end,
                                       total_tickets=100, remain_tickets=100, status=Activity.STATUS_PUBLISHED,
                                       pic_url="")
        ticket1 = Ticket.objects.create(activity_id=act1.id,student_id=cls.student_id_1,status=Ticket.STATUS_VALID,unique_id="a")
        ticket2 = Ticket.objects.create(activity_id=act4.id,student_id=cls.student_id_1,status=Ticket.STATUS_VALID,unique_id="b")
        User.objects.create(open_id=cls.open_id_1, student_id=cls.student_id_1)
        User.objects.create(open_id=cls.open_id_2,student_id=cls.student_id_2)
        User.objects.create(open_id=cls.open_id_3)

    def setUp(self):
        self.client = Client()

    def test_check(self):
        # test unbind
        # test default handler
        self.clickMsg["FromUserName"] = self.open_id_3
        msg = get_template('sendclick.xml').render(self.clickMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '您还没有绑定，绑定后才可使用该功能')

        # test no Ticket
        self.clickMsg["FromUserName"] = self.open_id_2
        msg = get_template('sendclick.xml').render(self.clickMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '当前没有已购的票, 您可点击菜单栏中“抢啥”查看现有活动')

        # test user with tickets
        self.clickMsg["FromUserName"] = self.open_id_1
        msg = get_template('sendclick.xml').render(self.clickMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']["Articles"]['item']
        return_titles = []
        for article in content:
            return_titles.append(article['Title'])
        tickets = Ticket.objects.filter(status=Ticket.STATUS_VALID,student_id=self.student_id_1)
        an_titles = []
        for tic in tickets:
            an_titles.append(tic.activity.name)
        self.assertEqual(return_titles, an_titles)

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


class TakeTicketHandlerTest(TestCase):
    # Test for take ticket handler
    @classmethod
    def setUpTestData(cls):
        cls.open_id_1 = 'oxmsfsdfsaksfmksd'
        cls.open_id_2 = 'oxasfdsfdsafasdfd'
        cls.student_id_1 = '2000000000'
        cls.student_id_2 = '2016013240'
        cls.unique_id_1 = 'dsafdasfefweksa'
        cls.unique_id_2 = 'kjknknkjnkkkkds'

        User.objects.create(open_id=cls.open_id_1, student_id=cls.student_id_1)

        User.objects.create(open_id=cls.open_id_2)

        cls.activity_1 = Activity.objects.create(name='test', key='test', description='myTest',
                                                 start_time='2018-12-02T08:00:00.000Z',
                                                 end_time=timezone.now() + timedelta(hours=2), place='github',
                                                 book_start='2018-10-02T08:00:00.000Z',
                                                 book_end=timezone.now() + timedelta(hours=1),
                                                 total_tickets=100, pic_url='xxx', remain_tickets=100, status=1)

        cls.activity_2 = Activity.objects.create(name='test2', key='test2', description='myTest2',
                                                 start_time='2018-12-02T08:00:00.000Z',
                                                 end_time=timezone.now() + timedelta(hours=2), place='github',
                                                 book_start='2018-10-02T08:00:00.000Z',
                                                 book_end=timezone.now() + timedelta(hours=1),
                                                 total_tickets=100, pic_url='xxx', remain_tickets=100, status=1)

        cls.ticket_1 = Ticket.objects.create(student_id=cls.student_id_1, unique_id=cls.unique_id_1,
                                             activity=Activity.objects.get(id=cls.activity_1.id),
                                             status=1)

        cls.ticket_2 = Ticket.objects.create(student_id=cls.student_id_2, unique_id=cls.unique_id_2,
                                             activity=Activity.objects.get(id=cls.activity_1.id),
                                             status=1)

        cls.textMsg = {'ToUserName': 'TestName', 'FromUserName': cls.open_id_1, 'Content': '取票 ' + cls.activity_1.key}

    def setUp(self):
        self.client = Client()

    def test_text(self):
        # test unbound studentID and openid
        self.textMsg['FromUserName'] = self.open_id_2
        msg = get_template('sendtext.xml').render(self.textMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '请先绑定姓名学号')

        # test nonexistent openid
        self.textMsg['FromUserName'] = 'testNonexistence'
        msg = get_template('sendtext.xml').render(self.textMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '请先绑定姓名学号')

        # test nonexistent ticket
        self.textMsg['FromUserName'] = self.open_id_1
        self.textMsg['Content'] = '取票 ' + self.activity_2.key
        msg = get_template('sendtext.xml').render(self.textMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '抱歉，您并没有该活动的门票')

        # test ticket past due
        self.activity_1.status = Activity.STATUS_SAVED
        self.activity_1.save()
        self.textMsg['FromUserName'] = self.open_id_1
        self.textMsg['Content'] = '取票 ' + self.activity_1.key
        msg = get_template('sendtext.xml').render(self.textMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '抱歉，您并没有该活动的门票')
        self.activity_1.status = 1
        self.activity_1.save()

        # test ticket used
        self.ticket_1.status = Ticket.STATUS_USED
        self.ticket_1.save()
        self.textMsg['FromUserName'] = self.open_id_1
        self.textMsg['Content'] = '取票 ' + self.activity_1.key
        msg = get_template('sendtext.xml').render(self.textMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '抱歉，您并没有该活动的门票')
        self.ticket_1.status = Ticket.STATUS_VALID
        self.ticket_1.save()

        # test correct request
        self.textMsg['FromUserName'] = self.open_id_1
        self.textMsg['Content'] = '取票 ' + self.activity_1.key
        msg = get_template('sendtext.xml').render(self.textMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        url = xmltodict.parse(response.content)['xml']['Articles']['item']['Url']
        time = xmltodict.parse(response.content)['xml']['Articles']['item']['Description']
        self.assertEqual(time, '开始时间：' + '2018-12-02 16:00:00' + '\n地点：' + self.activity_1.place)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class BookTicketHandlerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.open_id_1 = 'oxmsfsdfsaksfmksd'
        cls.open_id_2 = 'oxasfdsfdsafasdfd'
        cls.student_id_1 = '2000000000'
        cls.student_id_2 = '2016013240'
        cls.unique_id_1 = 'dsafdasfefweksa'
        cls.unique_id_2 = 'kjknknkjnkkkkds'

        User.objects.create(open_id=cls.open_id_1, student_id=cls.student_id_1)

        User.objects.create(open_id=cls.open_id_2)

        cls.activity_1 = Activity.objects.create(name='test', key='test', description='myTest',
                                                 start_time='2018-12-02T08:00:00.000Z',
                                                 end_time=timezone.now() + timedelta(hours=2), place='github',
                                                 book_start='2018-10-02T08:00:00.000Z',
                                                 book_end=timezone.now() + timedelta(hours=1),
                                                 total_tickets=100, pic_url='xxx', remain_tickets=100, status=1)

        cls.activity_2 = Activity.objects.create(name='test2', key='test2', description='myTest2',
                                                 start_time='2018-12-02T08:00:00.000Z',
                                                 end_time=timezone.now() + timedelta(hours=2), place='github',
                                                 book_start='2018-10-02T08:00:00.000Z',
                                                 book_end=timezone.now() + timedelta(hours=1),
                                                 total_tickets=100, pic_url='xxx', remain_tickets=100, status=1)

        cls.ticket_1 = Ticket.objects.create(student_id=cls.student_id_1, unique_id=cls.unique_id_1,
                                             activity=Activity.objects.get(id=cls.activity_1.id),
                                             status=1)

        cls.ticket_2 = Ticket.objects.create(student_id=cls.student_id_2, unique_id=cls.unique_id_2,
                                             activity=Activity.objects.get(id=cls.activity_1.id),
                                             status=1)

        cls.textMsg = {'ToUserName': 'TestName', 'FromUserName': cls.open_id_1, 'Content': '抢票 ' + cls.activity_2.key}
        cls.clickMsg = {'ToUserName': 'TestName', 'FromUserName': cls.open_id_1,
                        'EventKey': 'BOOKING_ACTIVITY_' + str(cls.activity_2.id)}

    def test_click(self):
        # test nonexistent activity
        self.clickMsg['EventKey'] = 'BOOKING_ACTIVITY_123'
        msg = get_template('sendclick.xml').render(self.clickMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '未查询到相关活动')
        self.clickMsg['EventKey'] = 'BOOKING_ACTIVITY_' + str(self.activity_2.id)

        # test unbound user
        self.clickMsg['FromUserName'] = self.open_id_2
        msg = get_template('sendclick.xml').render(self.clickMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '未绑定学号')
        self.clickMsg['FromUserName'] = self.open_id_1

        # test unpublished activity
        self.activity_2.status = Activity.STATUS_SAVED
        self.activity_2.save()
        msg = get_template('sendclick.xml').render(self.clickMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '该活动未发布')
        self.activity_2.status = Activity.STATUS_PUBLISHED
        self.activity_2.save()

        # test booking finished
        self.activity_2.book_end = timezone.now() - timedelta(hours=2)
        self.activity_2.save()
        msg = get_template('sendclick.xml').render(self.clickMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '该活动抢票已截止')
        self.activity_2.book_end = timezone.now() + timedelta(hours=1)
        self.activity_2.save()

        # test booking yet to begin
        self.activity_2.book_start = timezone.now() + timedelta(hours=2)
        self.activity_2.save()
        msg = get_template('sendclick.xml').render(self.clickMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '该活动未开放抢票')
        self.activity_2.book_start = '2018-10-02T08:00:00.000Z'
        self.activity_2.save()

        # test ticket depleted
        ticket = self.activity_2.remain_tickets
        self.activity_2.remain_tickets = 0
        self.activity_2.save()
        msg = get_template('sendclick.xml').render(self.clickMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '该活动已无余票')
        self.activity_2.remain_tickets = ticket
        self.activity_2.save()

        # test already possessed ticket
        self.clickMsg['EventKey'] = 'BOOKING_ACTIVITY_' + str(self.activity_1.id)
        msg = get_template('sendclick.xml').render(self.clickMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '您好，您已经有该活动的票，请点击查票查询电子票详情')
        self.clickMsg['EventKey'] = 'BOOKING_ACTIVITY_' + str(self.activity_2.id)

        # test success booking
        msg = get_template('sendclick.xml').render(self.clickMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Articles']['item']['Title']
        self.assertEqual(content, self.activity_2.name)

    def test_text(self):
        # test illegal string pattern
        self.textMsg['Content'] = '抢票'
        msg = get_template('sendtext.xml').render(self.textMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '请按格式输入：抢票 活动代称')


class RefundHandlerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.open_id_1 = 'oxmsfsdfsaksfmksd'
        cls.open_id_2 = 'oxasfdsfdsafasdfd'
        cls.student_id_1 = '2000000000'
        cls.student_id_2 = '2016013240'
        cls.unique_id_1 = 'dsafdasfefweksa'
        cls.unique_id_2 = 'kjknknkjnkkkkds'

        User.objects.create(open_id=cls.open_id_1, student_id=cls.student_id_1)

        User.objects.create(open_id=cls.open_id_2)

        cls.activity_1 = Activity.objects.create(name='test', key='test', description='myTest',
                                                 start_time='2018-12-02T08:00:00.000Z',
                                                 end_time=timezone.now() + timedelta(hours=2), place='github',
                                                 book_start='2018-10-02T08:00:00.000Z',
                                                 book_end=timezone.now() + timedelta(hours=1),
                                                 total_tickets=100, pic_url='xxx', remain_tickets=100, status=1)

        cls.activity_2 = Activity.objects.create(name='test2', key='test2', description='myTest2',
                                                 start_time='2018-12-02T08:00:00.000Z',
                                                 end_time=timezone.now() + timedelta(hours=2), place='github',
                                                 book_start='2018-10-02T08:00:00.000Z',
                                                 book_end=timezone.now() + timedelta(hours=1),
                                                 total_tickets=100, pic_url='xxx', remain_tickets=100, status=1)

        cls.ticket_1 = Ticket.objects.create(student_id=cls.student_id_1, unique_id=cls.unique_id_1,
                                             activity=Activity.objects.get(id=cls.activity_1.id),
                                             status=1)

        cls.ticket_2 = Ticket.objects.create(student_id=cls.student_id_2, unique_id=cls.unique_id_2,
                                             activity=Activity.objects.get(id=cls.activity_1.id),
                                             status=1)

        cls.textMsg = {'ToUserName': 'TestName', 'FromUserName': cls.open_id_1, 'Content': '退票 ' + cls.activity_1.key}

    def test_text(self):
        # test unbound openid
        self.textMsg['FromUserName'] = self.open_id_2
        msg = get_template('sendtext.xml').render(self.textMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '未绑定学号')
        self.textMsg['FromUserName'] = self.open_id_1

        # test illegal string pattern
        self.textMsg['Content'] = '退票'
        msg = get_template('sendtext.xml').render(self.textMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '请按格式输入：退票 活动代称')
        self.textMsg['Content'] = '退票 ' + self.activity_1.key

        # test nonexistent activity
        self.textMsg['Content'] = '退票 ' + self.activity_1.key + 'test'
        msg = get_template('sendtext.xml').render(self.textMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '未查询到相关活动')
        self.textMsg['Content'] = '退票 ' + self.activity_1.key

        # test no associated activity
        self.textMsg['Content'] = '退票 ' + self.activity_2.key
        msg = get_template('sendtext.xml').render(self.textMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '您没有此活动的票')
        self.textMsg['Content'] = '退票 ' + self.activity_1.key

        # test canceled ticket
        self.ticket_1.status = Ticket.STATUS_CANCELLED
        self.ticket_1.save()
        msg = get_template('sendtext.xml').render(self.textMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '您的票已经取消，不可退票')
        self.ticket_1.status = Ticket.STATUS_VALID
        self.ticket_1.save()

        # test used ticket
        self.ticket_1.status = Ticket.STATUS_USED
        self.ticket_1.save()
        msg = get_template('sendtext.xml').render(self.textMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '您的票已经使用，不可退票')
        self.ticket_1.status = Ticket.STATUS_VALID
        self.ticket_1.save()

        # test pass due
        self.activity_1.start_time = timezone.now()
        self.activity_1.save()
        msg = get_template('sendtext.xml').render(self.textMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '只能在活动开始45分钟前退票')
        self.activity_1.start_time = '2018-12-02T08:00:00.000Z'
        self.activity_1.save()

        # test success refund
        msg = get_template('sendtext.xml').render(self.textMsg)
        response = self.client.post('/wechat', msg, content_type='application/xml')
        self.assertEqual(response.status_code, 200)
        content = xmltodict.parse(response.content)['xml']['Content']
        self.assertEqual(content, '退票成功!')
