import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Perfil(models.Model):
    class Orientacao(models.TextChoices):
        HETEROSSEXUAL = "heterossexual", "Heterossexual"
        HOMOSSEXUAL = "homossexual", "Homossexual"
        BISSEXUAL = "bissexual", "Bissexual"
        OUTRO = "outro", "Outro"
        NAO_INFORMADO = "nao_informado", "Prefiro não dizer"

    class EstadoCivil(models.TextChoices):
        SOLTEIRO = "solteiro", "Solteiro(a)"
        NAMORANDO = "namorando", "Namorando"
        CASADO = "casado", "Casado(a)"
        OUTRO = "outro", "Outro"

    user_id = models.UUIDField(unique=True, editable=False)
    nome = models.CharField(max_length=100)
    idade = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(18), MaxValueValidator(120)]
    )
    curso = models.CharField(max_length=100)
    campus = models.CharField(max_length=100)
    orientacao = models.CharField(max_length=20, choices=Orientacao.choices)
    estado_civil = models.CharField(max_length=20, choices=EstadoCivil.choices)
    fotos = models.JSONField(default=list)  # lista de URLs das fotos
    bio = models.TextField(blank=True, default="")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "perfis"

    def __str__(self):
        return self.nome


class Interacao(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender_id = models.UUIDField()
    receiver_id = models.UUIDField()
    action = models.CharField(max_length=10)  # "flechar" ou "rejeitar"
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "interactions"