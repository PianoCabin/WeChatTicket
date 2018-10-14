# -*- coding: utf-8 -*-
#
from django.conf.urls import url
from .views import *


__author__ = "Epsirom"


urlpatterns = [
    url(r'^login$', Login.as_view())
]
