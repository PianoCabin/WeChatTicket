from codex.baseerror import *
from codex.baseview import APIView

from wechat.models import User, Activity, Ticket
import datetime
import re


class UserBind(APIView):

    def validate_user(self):
        if(re.match(r'[0-9]{10}', self.input["student_id"]) == None):
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
            activity = Activity.objects.get(id=id)
            info = {}
            info["name"]=activity.name
            info["key"]=activity.key
            info["description"]=activity.description
            info["startTime"]=activity.start_time.timestamp()
            info["endTime"]=activity.end_time.timestamp()
            info["place"]=activity.place
            info["bookStart"]=activity.book_start.timestamp()
            info["bookEnd"]=activity.book_end.timestamp()
            info["totalTickets"]=activity.total_tickets
            info["picUrl"]=activity.pic_url
            info["currentTime"]=datetime.datetime.now().timestamp()
            return info
        except Exception as e:
            raise ValidateError("no such Activity")


class UserTicket(APIView):
    def get(self):
        self.check_input("openid","ticket")
        try:
            student = User.objects.get(open_id=self.input["openid"])
            ticket = Ticket.objects.get(student_id=student.student_id,unique_id=self.input["ticket"])
            activity = Activity.objects.get(id=ticket.activity_id)
            info={}
            info["activityName"]=activity.name
            info["place"]=activity.place
            info["activityKey"]=activity.key
            info["uniqueId"]=ticket.unique_id
            info["startTime"]=activity.start_time.timestamp()
            info["endTime"]=activity.end_time.timestamp()
            info["currentTime"]=datetime.datetime.now().timestamp()
            info["status"]=ticket.status
            return info
        except Exception as e:
            raise ValidateError("no such Ticket!")