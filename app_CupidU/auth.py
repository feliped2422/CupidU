import jwt
from jwt import PyJWKClient
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import os
from supabase import create_client

JWKS_URL = "https://sgcoqululbosblwicmwz.supabase.co.supabase.co/auth/v1/jwks"

class SupabaseJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]

        try:
            # Busca a chave pública correta no JWKS
            jwks_client = PyJWKClient(JWKS_URL)
            signing_key = jwks_client.get_signing_key_from_jwt(token)

            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["ES256"]  # Supabase usa ECC (ES256)
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expirado")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Token inválido")

        # O UUID do usuário vem no campo 'sub'
        user_uuid = payload.get("sub")
        if not user_uuid:
            raise AuthenticationFailed("Token sem UUID")

        # Conecta ao Supabase
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        supabase = create_client(url, key)

        # Busca o perfil correspondente
        profile = supabase.table("profiles").select("*").eq("uuid", user_uuid).execute()

        if not profile.data:
            raise AuthenticationFailed("Perfil não encontrado")

        # Retorna o perfil como "usuário"
        return (profile.data[0], None)
