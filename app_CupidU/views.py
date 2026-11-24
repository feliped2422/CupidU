import os
import uuid
from django.db.models import Q
from django.db import connection, transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from supabase import create_client
from supabase_client import url, key,supabase
from .models import Curtida, Mensagem, Perfil
from .serializers import (
    SignupSerializer,
    LoginSerializer,
    VerifyOtpSerializer,
    ResendOtpSerializer,
    PerfilSerializer,
    RejeitarSerializer,
    EnviarMensagemSerializer,
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
                resposta = supabase.auth.verify_otp({
                    "email": email,
                    "token": token,
                    "type": tipo,
                })
            except Exception:
                resposta = None
                continue

            if resposta is not None and resposta.session is not None:
                break

        if resposta is None or resposta.session is None:
            return Response(
                {"detail": "Código inválido ou expirado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session = resposta.session

        return Response({
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
        })


class ResendOtpView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = ResendOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            novo_cliente().auth.resend({
                "type": "signup",
                "email": serializer.validated_data["email"],
            })
        except Exception as e:
            print("ERRO RESEND:", e)
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"detail": "Código reenviado."})


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

    def _nao_encontrado(self):
        return Response(
            {"detail": "Perfil não encontrado."},
            status=status.HTTP_404_NOT_FOUND,
        )

    def get(self, request):
        perfil = self._perfil(request)
        if perfil is None:
            return self._nao_encontrado()
        return Response(PerfilSerializer(perfil).data)

    def put(self, request):
        perfil = self._perfil(request)
        if perfil is None:
            return self._nao_encontrado()
        serializer = PerfilSerializer(perfil, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request):
        perfil = self._perfil(request)
        if perfil is None:
            return self._nao_encontrado()
        serializer = PerfilSerializer(perfil, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request):
        perfil = self._perfil(request)
        if perfil is None:
            return self._nao_encontrado()
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

def _travar_par(user_a, user_b):
    """Lock por par de usuários até o fim da transação."""
    chave = "".join(sorted([str(user_a), str(user_b)]))
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", [chave])

class FeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        meu_id = uuid.UUID(request.user.get("sub"))

        meu_perfil = Perfil.objects.filter(user_id=meu_id).first()
        if meu_perfil is None:
            return Response(
                {"detail": "Complete seu perfil para ver o feed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            limite = int(request.query_params.get("limit", 10))
        except ValueError:
            limite = 10
        limite = max(1, min(limite, 30))

        # Todo mundo que eu já flechei ou rejeitei
        ja_avaliados = Curtida.objects.filter(autor_id=meu_id).values("alvo_id")

        perfis = (
            Perfil.objects.filter(campus__iexact=meu_perfil.campus.strip())
            .exclude(user_id=meu_id)
            .exclude(user_id__in=ja_avaliados)
            .order_by("-criado_em")[:limite]
        )

        return Response(PerfilSerializer(perfis, many=True).data)

class RejeitarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RejeitarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        autor_id = uuid.UUID(request.user.get("sub"))

        if not Perfil.objects.filter(user_id=autor_id).exists():
            return Response(
                {"detail": "Complete seu perfil antes de usar o feed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        alvo = Perfil.objects.filter(id=serializer.validated_data["alvo_id"]).first()
        if alvo is None:
            return Response(
                {"detail": "Perfil não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if alvo.user_id == autor_id:
            return Response(
                {"detail": "Você não pode rejeitar o próprio perfil."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            _travar_par(autor_id, alvo.user_id)

            curtida, criada = Curtida.objects.get_or_create(
                autor_id=autor_id,
                alvo_id=alvo.user_id,
                defaults={"tipo": Curtida.Tipo.DISLIKE},
            )

            # Um match existente não pode ser desfeito por um toque de rejeitar
            if not criada and curtida.match:
                return Response(
                    {"rejeitado": False, "detail": "Vocês já têm match."},
                    status=status.HTTP_200_OK,
                )

            if not criada and curtida.tipo != Curtida.Tipo.DISLIKE:
                curtida.tipo = Curtida.Tipo.DISLIKE
                curtida.save(update_fields=["tipo"])

        return Response(
            {"rejeitado": True},
            status=status.HTTP_201_CREATED if criada else status.HTTP_200_OK,
        )

class CurtirView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RejeitarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        autor_id = uuid.UUID(request.user.get("sub"))

        if not Perfil.objects.filter(user_id=autor_id).exists():
            return Response(
                {"detail": "Complete seu perfil antes de usar o feed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        alvo = Perfil.objects.filter(
            id=serializer.validated_data["alvo_id"]
        ).first()

        if alvo is None:
            return Response(
                {"detail": "Perfil não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if alvo.user_id == autor_id:
            return Response(
                {"detail": "Você não pode curtir o próprio perfil."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        canal_id = None

        with transaction.atomic():
            _travar_par(autor_id, alvo.user_id)

            curtida, criada = Curtida.objects.get_or_create(
                autor_id=autor_id,
                alvo_id=alvo.user_id,
                defaults={"tipo": Curtida.Tipo.LIKE},
            )
            if not criada and curtida.tipo != Curtida.Tipo.LIKE:
                curtida.tipo = Curtida.Tipo.LIKE
                curtida.save(update_fields=["tipo"])

            curtida_reciproca = Curtida.objects.filter(
                autor_id=alvo.user_id,
                alvo_id=autor_id,
                tipo=Curtida.Tipo.LIKE,
            ).first()

            match = curtida_reciproca is not None

        if match:
            # Mesmo canal para os dois lados (determinístico, sem depender de ordem)
            a, b = sorted([str(autor_id), str(alvo.user_id)])
            canal_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"canal:{a}:{b}"))

            Curtida.objects.filter(
            Q(autor_id=autor_id, alvo_id=alvo.user_id)
            | Q(autor_id=alvo.user_id, alvo_id=autor_id)
            ).update(match=True, canal_id=canal_id)

        resposta = {"curtido": True, "match": match}
        if match:
            resposta["canal_id"] = canal_id
            resposta["perfil"] = PerfilSerializer(alvo).data    
        return Response(
            resposta,
            status=status.HTTP_201_CREATED if criada else status.HTTP_200_OK,
        )

class CurtidasRecebidasView(APIView):
    """Perfis que curtiram o usuário logado e que ele ainda não respondeu."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        meu_id = uuid.UUID(request.user.get("sub"))

        ja_respondi = Curtida.objects.filter(autor_id=meu_id).values("alvo_id")

        autores = (
            Curtida.objects.filter(alvo_id=meu_id, tipo=Curtida.Tipo.LIKE)
            .exclude(autor_id__in=ja_respondi)
            .values("autor_id")
        )

        perfis = Perfil.objects.filter(user_id__in=autores).order_by("-criado_em")
        return Response(PerfilSerializer(perfis, many=True).data)


class MatchesView(APIView):
    """Matches/conversas do usuário logado, com última mensagem e não lidas."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        meu_id = uuid.UUID(request.user.get("sub"))

        matches = list(
            Curtida.objects.filter(autor_id=meu_id, match=True).exclude(canal_id="")
        )

        perfis = {
            p.user_id: p
            for p in Perfil.objects.filter(user_id__in=[m.alvo_id for m in matches])
        }

        itens = []
        for m in matches:
            perfil = perfis.get(m.alvo_id)
            if perfil is None:
                continue

            ultima = Mensagem.objects.filter(canal_id=m.canal_id).order_by("-id").first()
            nao_lidas = (
                Mensagem.objects.filter(canal_id=m.canal_id, lida=False)
                .exclude(autor_id=meu_id)
                .count()
            )

            texto_ultima = None
            if ultima is not None:
                prefixo = "Você: " if ultima.autor_id == meu_id else ""
                texto_ultima = prefixo + ultima.texto

            ordem = ultima.criado_em if ultima else m.criado_em
            itens.append(
                (
                    ordem,
                    {
                        "canal_id": m.canal_id,
                        "nome": perfil.nome,
                        "curso": perfil.curso,
                        "foto": perfil.fotos[0] if perfil.fotos else None,
                        "ultima_mensagem": texto_ultima,
                        "nao_lidas": nao_lidas,
                        "perfil": PerfilSerializer(perfil).data,
                    },
                )
            )

        itens.sort(key=lambda t: t[0], reverse=True)
        return Response([dados for _, dados in itens])


def _formatar_mensagem(m, meu_id):
    return {
        "id": m.id,
        "texto": m.texto,
        "enviada_por_mim": m.autor_id == meu_id,
        "criado_em": m.criado_em.isoformat(),
    }


class MensagensView(APIView):
    """Histórico e envio de mensagens de um canal. Só quem tem o match acessa."""

    permission_classes = [IsAuthenticated]

    def _tem_acesso(self, meu_id, canal_id):
        return Curtida.objects.filter(
            autor_id=meu_id, canal_id=canal_id, match=True
        ).exists()

    def get(self, request, canal_id):
        meu_id = uuid.UUID(request.user.get("sub"))

        if not self._tem_acesso(meu_id, canal_id):
            return Response(
                {"detail": "Conversa não encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Abrir a conversa marca as mensagens do outro lado como lidas
        Mensagem.objects.filter(canal_id=canal_id, lida=False).exclude(
            autor_id=meu_id
        ).update(lida=True)

        depois = request.query_params.get("depois")
        if depois and depois.isdigit():
            # Polling: só o que chegou depois da última mensagem conhecida
            mensagens = Mensagem.objects.filter(
                canal_id=canal_id, id__gt=int(depois)
            ).order_by("id")
        else:
            # Carga inicial: últimas 100, em ordem cronológica
            mensagens = list(
                Mensagem.objects.filter(canal_id=canal_id).order_by("-id")[:100]
            )[::-1]

        return Response([_formatar_mensagem(m, meu_id) for m in mensagens])

    def post(self, request, canal_id):
        meu_id = uuid.UUID(request.user.get("sub"))

        if not self._tem_acesso(meu_id, canal_id):
            return Response(
                {"detail": "Conversa não encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EnviarMensagemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mensagem = Mensagem.objects.create(
            canal_id=canal_id,
            autor_id=meu_id,
            texto=serializer.validated_data["texto"],
        )
        return Response(
            _formatar_mensagem(mensagem, meu_id), status=status.HTTP_201_CREATED
        )