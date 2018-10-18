from codex.baseerror import *
from codex.baseview import APIView

from wechat.models import User, Activity, Ticket
import datetime
import re


class UserBind(APIView):

    def validate_user(self):
        if (re.match(r'[0-9]{10}', self.input["student_id"]) == None):
            raise ValidateError("invalid Student_id")
        pass
        # raise NotImplementedError('You should implement UserBind.validate_user method')

    def get(self):
        self.check_input('openid')
        return str(User.get_by_openid(self.input['openid']).student_id or '')

    def post(self):
        self.check_input('openid', 'student_id', 'password')
        user = User.get_by_openid(self.input['openid'])
        self.validate_user()
        user.student_id = self.input['student_id']
        user.save()


class UserActivity(APIView):
    def get(self):
        self.check_input("id")
        try:
            id = self.input["id"]
            activity = Activity.objects.get(id=id, status=Activity.STATUS_PUBLISHED)
            info = {"name": activity.name, "key": activity.key, "description": activity.description,
                    "startTime": activity.start_time.timestamp(), "endTime": activity.end_time.timestamp(),
                    "place": activity.place, "bookStart": activity.book_start.timestamp(),
                    "bookEnd": activity.book_end.timestamp(), "totalTickets": activity.total_tickets,
                    'remainTickets': activity.remain_tickets,
                    "picUrl": activity.pic_url, "currentTime": datetime.datetime.now().timestamp()}
            return info
        except:
            raise ValidateError("no such Activity")


class UserTicket(APIView):
    def get(self):
        self.check_input("openid", "ticket")
        try:
            student = User.objects.get(open_id=self.input["openid"])
            ticket = Ticket.objects.get(student_id=student.student_id, unique_id=self.input["ticket"])
            activity = Activity.objects.get(id=ticket.activity_id)
            info = {"activityName": activity.name, "place": activity.place, "activityKey": activity.key,
                    "uniqueId": ticket.unique_id, "startTime": activity.start_time.timestamp(),
                    "endTime": activity.end_time.timestamp(), "currentTime": datetime.datetime.now().timestamp(),
                    "status": ticket.status}
            return info
        except:
            raise ValidateError("no such Ticket!")