# -*- coding: utf-8 -*-
#
from wechat.wrapper import WeChatHandler
from wechat.models import Activity, Ticket

from WeChatTicket import settings
from datetime import timedelta
import re
from django.utils import timezone
from django.db import transaction
import uuid

__author__ = "PianoCabin"


class ErrorHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，服务器现在有点忙，暂时不能给您答复 T T')


class DefaultHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，没有找到您需要的信息:(')


class HelpOrSubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('帮助', 'help') or self.is_event('scan', 'subscribe') or \
               self.is_event_click(self.view.event_keys['help'])

    def handle(self):
        return self.reply_single_news({
            'Title': self.get_message('help_title'),
            'Description': self.get_message('help_description'),
            'Url': self.url_help(),
        })


class UnbindOrUnsubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('解绑') or self.is_event('unsubscribe')

    def handle(self):
        self.user.student_id = ''
        self.user.save()
        return self.reply_text(self.get_message('unbind_account'))


class BindAccountHandler(WeChatHandler):

    def check(self):
        return self.is_text('绑定') or self.is_event_click(self.view.event_keys['account_bind'])

    def handle(self):
        return self.reply_text(self.get_message('bind_account'))


class BookEmptyHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['book_empty'])

    def handle(self):
        return self.reply_text(self.get_message('book_empty'))


# begin to add handler
class BookWhatHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['book_what'])

    def handle(self):
        activity_list = Activity.objects.filter(status=Activity.STATUS_PUBLISHED)
        if activity_list.exists():
            articles = []

            for activity in activity_list:
                calibration_begintime = (activity.start_time + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                calibration_endtime = (activity.book_end + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                result = {
                    'Title': activity.name,
                    'Description': '开始时间：' + calibration_begintime + activity.description +
                                   '\n抢票结束时间：' + calibration_endtime,
                    'PicUrl': activity.pic_url,
                    'Url': settings.get_url("/u/activity/", {"id": activity.id}),
                }
                articles.append(result)
            return self.reply_news(articles)
        else:
            return self.reply_text("当前活动尚不可抢票")


class CheckTicketHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['get_ticket'])

    def handle(self):
        if not self.user.student_id:
            return self.reply_text("您还没有绑定，绑定后才可使用该功能")

        ticket_list = Ticket.objects.filter(student_id=self.user.student_id, status=Ticket.STATUS_VALID)

        if not ticket_list.exists():
            return self.reply_text("当前没有已购的票, 您可点击菜单栏中“抢啥”查看现有活动")

        articles = []
        for ticket in ticket_list:
            activity = ticket.activity
            calibration_time = (activity.start_time + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")

            messages = {
                'Title': activity.name,
                'Description': '开始时间：' + calibration_time + '\n地点：' + activity.place,
                'Url': settings.get_url("/u/ticket/", {"openid": self.user.open_id, "ticket": ticket.unique_id}),
            }
            articles.append(messages)

        return self.reply_news(articles)


class BookTicketHandler(WeChatHandler):

    def check(self):
        return self.is_text_command("抢票") or (self.is_msg_type('event') and (self.input['Event'] == 'CLICK') \
                                              and (re.match("BOOKING_ACTIVITY_[0-9]+$", self.input['EventKey'])))

    def handle(self):
        if not self.user.student_id:
            return self.reply_text("未绑定学号")
        with transaction.atomic():
            activity = None
            if self.is_text_command("抢票"):

                key = re.match(r'抢票\s([\s\S]+)', self.input['Content'], re.DOTALL)
                if (key == None):
                    return self.reply_text("请按格式输入：抢票 活动代称")
                key = key.group(1)
                try:
                    activity = Activity.objects.get(key=key)
                except:
                    return self.reply_text("未查询到相关活动")
            else:
                id = re.match("BOOKING_ACTIVITY_([0-9]+)$", self.input['EventKey']).group(1)
                print(id)
                try:
                    activity = Activity.objects.get(id=id)
                except:
                    return self.reply_text("未查询到相关活动")
            if activity.status != Activity.STATUS_PUBLISHED:
                return self.reply_text("该活动未发布")
            if activity.book_end < timezone.now():
                return self.reply_text("该活动抢票已截止")
            if activity.book_start > timezone.now():
                return self.reply_text("该活动未开放抢票")
            if activity.remain_tickets <= 0:
                return self.reply_text("该活动已无余票")
            try:
                ticket = Ticket.objects.get(activity_id=activity.id, student_id=self.user.student_id,
                                            status__gt=Ticket.STATUS_CANCELLED)
                return self.reply_single_news(self.get_ticket_detail(ticket))
            except:
                info = activity.name + self.user.student_id
                unique_id = str(uuid.uuid1()) + info
                ticket = Ticket.objects.create(activity_id=activity.id, student_id=self.user.student_id,
                                               unique_id=unique_id, status=Ticket.STATUS_VALID)
                activity.remain_tickets -= 1
                activity.save()
                return self.reply_single_news(self.get_ticket_detail(ticket))