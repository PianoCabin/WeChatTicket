from codex.baseerror import *
from codex.baseview import APIView

from django.contrib import auth


class Login(APIView):

    def get(self):
        if not self.request.user.is_authenticated():
            raise ValidateError("Please Login!")

    def post(self):
        self.check_input("username", "password")
        username = self.input["username"]
        password = self.input["password"]
        user = auth.authenticate(request=self.request, username=username, password=password)
        if user:
            raise ValidateError("Error input, please input again!")
        auth.login(self.request, user)
