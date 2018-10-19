from codex.baseerror import *
from codex.baseview import APIView

from django.contrib import auth
from wechat import models
from wechat.models import Activity, Ticket
from django.utils import timezone
from wechat.views import CustomWeChatView
import uuid

from WeChatTicket import settings
import os
import datetime
import urllib.parse
from datetime import timedelta
import urllib.parse


class Login(APIView):
    def get(self):
        if not self.request.user.is_authenticated():
            raise ValidateError("Please login!")

    def post(self):
        self.check_input("username", "password")
        username = self.input["username"]
        password = self.input["password"]
        user = auth.authenticate(request=self.request, username=username, password=password)
        if not user:
            raise ValidateError("Either username or password is wrong, please login again!")

        auth.login(self.request, user)


class Logout(APIView):
    def post(self):
        if not self.request.user.is_authenticated():
            raise ValidateError("Logout failed, you must login first!")
        auth.logout(self.request)


class ActivityList(APIView):
    def get(self):
        if not self.request.user.is_authenticated():
            raise ValidateError("Fetch failed, you must login first!")
        # select status >= 0
        activity_list = models.Activity.objects.exclude(status__lt=0)

        # add activity_details and return
        activity_details = []
        for activity in activity_list:
            activity_details.append({
                "id": activity.id,
                "name": activity.name,
                "description": activity.description,
                "startTime": activity.start_time.timestamp(),
                "endTime": activity.end_time.timestamp(),
                "place": activity.place,
                "bookStart": activity.book_start.timestamp(),
                "bookEnd": activity.book_end.timestamp(),
                "currentTime": timezone.now().timestamp(),
                "status": activity.status
            })

        return activity_details


class ActivityDelete(APIView):
    def post(self):
        if not self.request.user.is_authenticated():
            raise ValidateError("You have not rights to delete activity, please login!")
        self.check_input("id")
        activity_id = self.input["id"]
        if not models.Activity.objects.filter(id=activity_id).update(status=models.Activity.STATUS_DELETED):
            raise LogicError("Delete failed, activity not found!")


class ActivityCreate(APIView):
    def post(self):
        if not self.request.user.is_authenticated():
            raise ValidateError("You have not rights to create activity, please login!")
        self.check_input("name", "key", "place", "description", "picUrl", "startTime",
                         "endTime", "bookStart", "bookEnd", "totalTickets", "status")
        name = self.input["name"]
        key = self.input["key"]
        place = self.input["place"]
        description = self.input["description"]
        picUrl = self.input["picUrl"]
        startTime = self.input["startTime"]
        endTime = self.input["endTime"]
        bookStart = self.input["bookStart"]
        bookEnd = self.input["bookEnd"]
        totalTickets = self.input["totalTickets"]
        status = self.input["status"]
        remainTickets = totalTickets

        new_activity = models.Activity.objects.create(
            name=name, key=key, place=place, description=description, pic_url=picUrl,
            start_time=startTime, end_time=endTime, book_start=bookStart, book_end=bookEnd,
            total_tickets=totalTickets, status=status, remain_tickets=remainTickets)

        if not new_activity:
            raise InputError("Fail to create a activity!")


class ActivityDetails(APIView):
    def get(self):
        if not self.request.user.is_authenticated():
            raise ValidateError("You have not rights to get activity list, please login!")
        self.check_input("id")
        activity_id = self.input["id"]
        try:
            activity = models.Activity.objects.get(id=activity_id)
        except models.Activity.DoesNotExist:
            raise LogicError("Activity not found!")

        bookedTickets = activity.total_tickets - activity.remain_tickets
        usedTickets = models.Ticket.objects.filter(status=models.Ticket.STATUS_USED, activity=activity)
        usedTickets = len(usedTickets)
        activity_details = {
            "name": activity.name,
            "key": activity.key,
            "description": activity.description,
            "startTime": activity.start_time.timestamp(),
            "endTime": activity.end_time.timestamp(),
            "place": activity.place,
            "bookStart": activity.book_start.timestamp(),
            "bookEnd": activity.book_end.timestamp(),
            "totalTickets": activity.total_tickets,
            "picUrl": activity.pic_url,
            "bookedTickets": bookedTickets,
            "usedTickets": usedTickets,
            "currentTime": timezone.now().timestamp(),
            "status": activity.status
        }
        return activity_details

    def post(self):
        if not self.request.user.is_authenticated():
            raise ValidateError("You have not rights to get activity list, please login!")
        self.check_input("id", "name", "place", "description", "picUrl", "startTime",
                         "endTime", "bookStart", "bookEnd", "totalTickets", "status")
        activity_id = self.input["id"]
        name = self.input["name"]
        place = self.input["place"]
        description = self.input["description"]
        picUrl = self.input["picUrl"]
        startTime = self.input["startTime"]
        endTime = self.input["endTime"]
        bookStart = self.input["bookStart"]
        bookEnd = self.input["bookEnd"]
        totalTickets = self.input["totalTickets"]
        status = self.input["status"]
        try:
            activity = models.Activity.objects.get(id=activity_id)
        except models.Activity.DoesNotExist:
            raise LogicError("Activity not found!")
        activity.description = description
        activity.pic_url = picUrl
        if activity.status != models.Activity.STATUS_PUBLISHED:
            activity.name = name
            activity.place = place
            activity.book_start = bookStart
            activity.status = status
        elif status == 1:
            activity.status = status

        if activity.end_time > timezone.now():
            activity.start_time = startTime
            activity.end_time = endTime
            activity.save()
            activity = models.Activity.objects.get(id=activity_id)

        if activity.start_time > timezone.now():
            activity.book_end = bookEnd

        if activity.book_start > timezone.now():
            activity.total_tickets = totalTickets
        activity.save()


class UploadImg(APIView):

    def post(self):
        if not self.request.user.is_authenticated():
            raise ValidateError("Please login!")
        self.check_input("image")
        try:
            image = self.input["image"][0]
            name = str(uuid.uuid1()) + image.name
            file = open('./static/uimg/' + name, 'wb')
            for chunk in image.chunks():
                file.write(chunk)
            file.close()
            path = 'uimg/' + name
            url = urllib.parse.urljoin(settings.CONFIGS["SITE_DOMAIN"], path)
            return url
        except:
            raise ValidateError("failed to save Image")


class ActivityMenu(APIView):

    def get(self):
        if not self.request.user.is_authenticated():
            raise ValidateError("Please login!")
        current_menu = CustomWeChatView.lib.get_wechat_menu()
        existed_buttons = list()
        for btn in current_menu:
            if btn['name'] == '抢票':
                existed_buttons += btn.get('sub_button', list())
        activity_ids = list()
        for btn in existed_buttons:
            if 'key' in btn:
                activity_id = btn['key']
                if activity_id.startswith(CustomWeChatView.event_keys['book_header']):
                    activity_id = activity_id[len(CustomWeChatView.event_keys['book_header']):]
                if activity_id and activity_id.isdigit():
                    activity_ids.append(int(activity_id))
        actList = Activity.objects.filter(status=Activity.STATUS_PUBLISHED, book_end__gt=timezone.now(),
                                          book_start__lt=timezone.now())
        # print(activity_ids)
        infos = []
        for act in actList:
            info = {"id": act.id, "name": act.name, "menuIndex": 0}
            infos.append(info)
        for info in infos:
            if info['id'] in activity_ids:
                # print('here')
                info['menuIndex'] = activity_ids.index(info['id'])+1
        return infos

    def post(self):
        if not self.request.user.is_authenticated():
            raise ValidateError("Please login!")
        idList = self.input
        for i in Activity.objects.filter(status=Activity.STATUS_PUBLISHED):
            i.status = 0
        activityList = []
        for id in idList:
            try:
                act = Activity.objects.get(id=id)
                act.status = 1
                act.save()
                activityList.append(act)
            except:
                raise ValidateError("no such activity")
        # print(activityList)
        CustomWeChatView.update_menu(activityList)


class CheckIn(APIView):
    def post(self):
        if not self.request.user.is_authenticated():
            raise ValidateError("Please login!")
        self.check_input("actId")
        studentId = self.input.get("studentId")
        unique_id = self.input.get("ticket")
        if studentId == None and unique_id == None:
            raise ValidateError("info loss")
        if studentId != None and unique_id != None:
            raise ValidateError("shadiao geiduole")
        ticket = None
        try:
            if studentId != None:
                ticket = Ticket.objects.get(studentId=studentId)
            else:
                ticket = Ticket.objects.get(unique_id=unique_id)
        except:
            raise ValidateError("invalid Ticket")
        if ticket.status == Ticket.STATUS_USED:
            raise ValidateError("ticket Used!")
        if ticket.status == Ticket.STATUS_CANCELLED:
            raise ValidateError("ticket Canceled!")
        ticket.status = Ticket.STATUS_USED
        ticket.save()
        info = {"ticket": ticket.unique_id, "studentId": ticket.student_id}
        return info

