from django.test import TestCase, Client
from wechat.models import *
from django.template.loader import get_template
import xml.etree.ElementTree as ET
from .wrapper import WeChatView
import xmltodict
from django.utils import timezone


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





