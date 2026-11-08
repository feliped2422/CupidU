from django.urls import path

from .views import (
    ProfileProtectedView,
    SignupView,
    LoginView,
    VerifyOtpView,
    ResendOtpView,
    PerfilCreateView,
    PerfilMeView,
    FeedView,
    RejeitarView,
)

urlpatterns = [
    path("api/profiles/", ProfileProtectedView.as_view(), name="profiles"),
    path("auth/signup", SignupView.as_view(), name="signup"),
    path("auth/login", LoginView.as_view(), name="login"),
    path("auth/verify-otp", VerifyOtpView.as_view(), name="verify-otp"),
    path("auth/resend-otp", ResendOtpView.as_view(), name="resend-otp"),
    path("perfis/", PerfilCreateView.as_view(), name="perfil-criar"),
    path("perfis/me/", PerfilMeView.as_view(), name="perfil-me"),
    path("feed/", FeedView.as_view(), name="feed"),
    path("rejeitar/", RejeitarView.as_view(), name="rejeitar"),
]