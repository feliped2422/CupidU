from django.urls import path

from .views import (
    FeedView,
    ProfileProtectedView,
    SignupView,
    LoginView,
    VerifyOtpView,
    ResendOtpView,
    PerfilCreateView,
    PerfilMeView,
    RejeitarView,
    CurtirView,
    CurtidasRecebidasView,
    MatchesView,
    MensagensView,

     # FlecharView,   # descomente quando a view do flechar estiver no views.py
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
    path("feed/curtir/", CurtirView.as_view(), name="feed-curtir"),
    path("feed/rejeitar/", RejeitarView.as_view(), name="feed-rejeitar"),
    path("feed/curtidas/recebidas/", CurtidasRecebidasView.as_view(), name="curtidas-recebidas"),
    path("feed/matches/", MatchesView.as_view(), name="matches"),
    path("feed/canais/<str:canal_id>/mensagens/", MensagensView.as_view(), name="mensagens"),
    # path("flechar/", FlecharView.as_view(), name="flechar"),
]
