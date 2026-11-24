from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q


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

    # id do usuário no Supabase Auth (campo "sub" do token JWT)
    user_id = models.UUIDField(unique=True, editable=False)
    nome = models.CharField(max_length=100)
    idade = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(18), MaxValueValidator(120)]
    )
    curso = models.CharField(max_length=100)
    campus = models.CharField(max_length=100)
    orientacao = models.CharField(max_length=20, choices=Orientacao.choices)
    estado_civil = models.CharField(max_length=20, choices=EstadoCivil.choices)
    bio = models.TextField(blank=True, default="")
    fotos = models.JSONField(default=list)  # lista de URLs das fotos
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "perfis"

    def __str__(self):
        return self.nome


class Curtida(models.Model):
    """Registra a ação de um usuário sobre outro (like/dislike) e o estado do match."""

    class Tipo(models.TextChoices):
        LIKE = "LIKE", "Like"
        DISLIKE = "DISLIKE", "Dislike"

    # UUIDs dos usuários (mesmo valor de Perfil.user_id / "sub" do JWT)
    autor_id = models.UUIDField(db_index=True)
    alvo_id = models.UUIDField(db_index=True)
    tipo = models.CharField(max_length=7, choices=Tipo.choices, default=Tipo.LIKE)

    # True nas DUAS linhas (A->B e B->A) quando há curtida recíproca
    match = models.BooleanField(default=False)

    # ID do canal no Stream Chat (preenchido quando há match)
    canal_id = models.CharField(max_length=64, blank=True, default="")

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "curtidas"
        constraints = [
            models.UniqueConstraint(
                fields=["autor_id", "alvo_id"], name="curtida_unica_por_par"
            ),
            models.CheckConstraint(
                condition=~Q(autor_id=F("alvo_id")),
                name="curtida_nao_em_si_mesmo",
            ),
        ]

    def __str__(self):
        return f"{self.autor_id} -> {self.alvo_id} ({self.tipo}, match={self.match})"

class Mensagem(models.Model):
    """Mensagem trocada entre duas pessoas que têm match (identificadas pelo canal_id)."""

    canal_id = models.CharField(max_length=64, db_index=True)
    autor_id = models.UUIDField()
    texto = models.TextField(max_length=2000)
    lida = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mensagens"
        ordering = ["id"]
        indexes = [models.Index(fields=["canal_id", "id"])]

    def __str__(self):
        return f"{self.autor_id} @ {self.canal_id}"