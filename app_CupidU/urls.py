from rest_framework import routers

from django.urls import path
from .views import ProfileProtectedView

urlpatterns = [
   path("api/profiles/", ProfileProtectedView.as_view(), name="profiles"),
]
