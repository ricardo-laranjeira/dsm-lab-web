
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.core.security import decodificar_access_token
from api.models.usuario import Usuario
from api.repositories import usuario_repository


bearer_scheme = HTTPBearer(auto_error=False)


def get_usuario_atual(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    erro_autenticacao = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token ausente, inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise erro_autenticacao

    try:
        payload = decodificar_access_token(credentials.credentials)
        subject = payload.get("sub")

        if not isinstance(subject, str) or not subject.isdigit():
            raise erro_autenticacao

        idusuario = int(subject)

    except (jwt.InvalidTokenError, ValueError):
        raise erro_autenticacao from None

    usuario = usuario_repository.buscar_por_id(db, idusuario)

    if usuario is None or not usuario.ativo:
        raise erro_autenticacao

    return usuario
