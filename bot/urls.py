from django.contrib.auth.views import LogoutView
from django.urls import include, path

from bot.views import *

urlpatterns = [
    path("", index, name="index"),
    path("home/", home, name="home"),
    path("logout/", logout_view, name="logout"),
    path("result/", result, name="result"),
]