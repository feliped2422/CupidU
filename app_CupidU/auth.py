import jwt
from jwt import PyJWKClient
from jwt.exceptions import PyJWKClientError, InvalidTokenError, ExpiredSignatureError
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from datetime import datetime
from django.utils import timezone


JWKS_URL = "https://sgcoqululbosblwicmwz.supabase.co/auth/v1/.well-known/jwks.json"
_jwks_client = PyJWKClient(JWKS_URL, cache_keys=True)
print("JWKS URL:", JWKS_URL)


class SupabaseUser(dict):
    """Payload do JWT que o DRF aceita como usuário autenticado."""
    is_authenticated = True
    is_anonymous = False


class SupabaseJWTAuthentication(BaseAuthentication):
        
    
    def authenticate_header(self, request):
        return "Bearer"
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ", 1)[1].strip()

        payload = jwt.decode(
        token,
        options={"verify_signature": False}
        )

        print("IAT:", payload["iat"])
        print("IAT DATA:", datetime.fromtimestamp(payload["iat"]))
        print("AGORA:", datetime.now())

        try:
            signing_key = _jwks_client.get_signing_key_from_jwt(token)
            print("HEADER:", jwt.get_unverified_header(token))
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["ES256"],
                audience="authenticated",
                leeway=60,
            )
        except ExpiredSignatureError:
            raise AuthenticationFailed("Token expirado")
        except Exception as e:
            print("ERRO REAL:", repr(e))
            raise AuthenticationFailed(str(e))
        
        
        if not payload.get("sub"):
            raise AuthenticationFailed("Token sem UUID")

        return (SupabaseUser(payload), None)