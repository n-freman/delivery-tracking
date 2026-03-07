from django.urls import path

from apps.general import views

app_name = "general"

urlpatterns = [
    path("", views.index, name="index"),
]
