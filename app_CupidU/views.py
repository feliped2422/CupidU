import os

from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from supabase import create_client

from supabase_client import url, key
from .models import Perfil
from .serializers import (
    SignupSerializer,
    LoginSerializer,
    VerifyOtpSerializer,
    ResendOtpSerializer,
    PerfilSerializer,
)


class ProfileProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "Acesso autorizado!",
            "user_uuid": request.user.get("sub"),
            "claims": request.user
        })


def novo_cliente():
    return create_client(url, key)


def cliente_admin():
    return create_client(url, os.environ["SUPABASE_SERVICE_KEY"])


class SignupView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # domínio errado -> 400

        try:
            response = novo_cliente().auth.sign_up({
                "email": serializer.validated_data["email"],
                "password": serializer.validated_data["password"],
            })

            return Response(
                {
                    "detail": "Cadastro realizado com sucesso.",
                    "data": str(response)
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            print("ERRO SIGNUP:", e)

            return Response(
            {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
    )


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            resposta = novo_cliente().auth.sign_in_with_password({
                "email": serializer.validated_data["email"],
                "password": serializer.validated_data["password"],
            })
        except Exception:
            return Response(
                {"detail": "E-mail ou senha inválidos."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response({
            "access_token": resposta.session.access_token,
            "refresh_token": resposta.session.refresh_token,
        })


class VerifyOtpView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        token = serializer.validated_data["token"]

        resposta = None
        for tipo in ("email", "signup"):
            try:
                resposta = novo_cliente().auth.verify_otp(
                    {"email": email, "token": token, "type": tipo}
                )
            except Exception:
                resposta = None
                continue
            if resposta.session is not None:
                break

        if resposta is None or resposta.session is None:
            return Response(
                {"detail": "Código inválido ou expirado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({
            "access_token": resposta.session.access_token,
            "refresh_token": resposta.session.refresh_token,
        })


class ResendOtpView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = ResendOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            response = novo_cliente().auth.resend({
                "type": "signup",
                "email": serializer.validated_data["email"],
            })

        except Exception as e:
            print("ERRO RESEND:", e)

            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PerfilCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.user.get("sub")

        if Perfil.objects.filter(user_id=user_id).exists():
            return Response(
                {"detail": "Você já possui um perfil."},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = PerfilSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user_id=user_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PerfilMeView(APIView):
    permission_classes = [IsAuthenticated]

    def _perfil(self, request):
        return Perfil.objects.filter(user_id=request.user.get("sub")).first()

    def get(self, request):
        perfil = self._perfil(request)
        if perfil is None:
            return Response(
                {"detail": "Perfil não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(PerfilSerializer(perfil).data)

    def put(self, request):
        perfil = self._perfil(request)
        if perfil is None:
            return Response(
                {"detail": "Perfil não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = PerfilSerializer(perfil, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request):
        perfil = self._perfil(request)
        if perfil is None:
            return Response(
                {"detail": "Perfil não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        user_id = request.user.get("sub")
        try:
            with transaction.atomic():
                perfil.delete()
                cliente_admin().auth.admin.delete_user(user_id)
        except Exception:
            return Response(
                {"detail": "Não foi possível excluir a conta."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)