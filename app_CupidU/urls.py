from rest_framework import routers

from django.urls import path
from .views import ProfileProtectedView, SignupView, LoginView

urlpatterns = [
   path("api/profiles/", ProfileProtectedView.as_view(), name="profiles"),
   path("auth/signup", SignupView.as_view(), name="signup"),
   path("auth/login", LoginView.as_view(), name="login"),
]
