from django.urls import path
from datamodel import views

urlpatterns = [
    path('', views.index, name="index")
]
