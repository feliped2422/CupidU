from rest_framework import serializers

DOMINIO_PERMITIDO = "sempreunama.com.br"
class ProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)

    def validate_email(self, value):
        email = value.strip().lower()
        if email.rsplit("@", 1)[-1] != DOMINIO_PERMITIDO:
            raise serializers.ValidationError(
                "Use seu e-mail institucional @sempreunama.com.br."
            )
        return email
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
