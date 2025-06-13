from django.urls import path
from . import views

urlpatterns = [
    path('', views.nasa_apod, name='nasa_apod'),
]
