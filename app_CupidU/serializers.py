from rest_framework import serializers

from .models import Perfil

DOMINIO_PERMITIDO = "sempreunama.com.br"


def _valida_dominio(value):
    """Aceita só e-mails do domínio institucional e devolve o e-mail normalizado."""
    email = value.strip().lower()
    if email.rsplit("@", 1)[-1] != DOMINIO_PERMITIDO:
        raise serializers.ValidationError(
            "Use seu e-mail institucional @sempreunama.com.br."
        )
    return email


class ProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)

    def validate_email(self, value):
        return _valida_dominio(value)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.RegexField(
        regex=r"^\d{6}$",
        error_messages={"invalid": "O código deve ter 6 dígitos."},
    )

    def validate_email(self, value):
        return _valida_dominio(value)


class ResendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return _valida_dominio(value)


class PerfilSerializer(serializers.ModelSerializer):
    fotos = serializers.ListField(
        child=serializers.URLField(), min_length=1, max_length=6
    )

    class Meta:
        model = Perfil
        fields = [
            "id", "nome", "idade", "curso", "campus",
            "orientacao", "estado_civil", "fotos",
        ]
        read_only_fields = ["id"]