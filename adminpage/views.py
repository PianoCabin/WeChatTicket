from codex.baseerror import *
from codex.baseview import APIView

from django.contrib import auth
from wechat import models
from django.utils import timezone


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
            name=name, key=key, place=place, description=description,pic_url=picUrl,
            start_time=startTime, end_time=endTime, book_start=bookStart, book_end=bookEnd,
            total_tickets=totalTickets, status=status,remain_tickets=remainTickets)

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
        usedTickets = models.Ticket.objects.filter(status=models.Ticket.STATUS_USED)
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
        if activity.end_time.timestamp() > timezone.now().timestamp():
            activity.start_time = startTime
            activity.end_time = endTime
        if activity.start_time.timestamp() > timezone.now().timestamp():
            activity.book_end = bookEnd
        if activity.book_start.timestamp() > timezone.now().timestamp():
            activity.total_tickets = totalTickets
        activity.save()

