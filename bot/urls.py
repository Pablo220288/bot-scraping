from django.contrib.auth.views import LogoutView
from django.urls import include, path

from bot.views import *

urlpatterns = [
    path("", index, name="index"),
]