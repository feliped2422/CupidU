from rest_framework import viewsets, status 
from django.shortcuts import render

from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from supabase import create_client 
from supabase_client import supabase, url, key 
from .serializers import ProfileSerializer, SignupSerializer, LoginSerializer
from rest_framework.permissions import IsAuthenticated

class ProfileProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # request.user agora é o perfil buscado no Supabase
        return Response({
            "message": "Acesso autorizado!",
            "user_uuid": request.user.get("sub"),
            "claims": request.user
        })

def novo_cliente():
    # Um cliente novo por requisição, para não misturar sessões de usuários
    return create_client(url, key)


class SignupView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # domínio errado -> 400

        try:
            novo_cliente().auth.sign_up({
                "email": serializer.validated_data["email"],
                "password": serializer.validated_data["password"],
            })
        except Exception:
            return Response(
                {"detail": "Não foi possível concluir o cadastro."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "Código de 6 dígitos enviado para o seu e-mail."},
            status=status.HTTP_201_CREATED,
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