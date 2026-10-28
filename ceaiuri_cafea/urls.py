from django.urls import path, re_path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("info", views.info, name="info"),
    path("despre", views.despre, name="despre"),
    path("istoric", views.istoric, name="istoric"),
    path("produse", views.produse, name="produse"),
    path("contact", views.contact, name="contact"),
    path("cos_virtual", views.cos_virtual, name="cos_virtual"),
    path("log", views.log, name="log"),
    path("in_lucru", views.in_lucru, name="in_lucru"),
    re_path(r"^accesare(?P<id>\d+)$", views.accesare, name="accesare"),
]