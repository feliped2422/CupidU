from rest_framework import viewsets
from django.shortcuts import render

from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from supabase_client import supabase
from .serializers import ProfileSerializer
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