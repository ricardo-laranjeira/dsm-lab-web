
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from api.core.config import settings


password_hash = PasswordHash.recommended()


def hash_senha(senha: str) -> str:
    return password_hash.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return password_hash.verify(senha, senha_hash)


def criar_access_token(subject: str) -> str:
    """Cria um token JWT para o usuário informado."""
    agora = datetime.now(timezone.utc)
    expiracao = agora + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": subject,
        "iat": agora,
        "exp": expiracao,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )


def decodificar_access_token(token: str) -> dict:
    """Valida o token JWT e retorna suas informações."""
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithms=[settings.JWT_ALGORITHM],
    )
