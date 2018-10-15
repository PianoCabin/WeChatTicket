from codex.baseerror import *
from codex.baseview import APIView

from django.contrib import auth


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
    def post(self):
        pass