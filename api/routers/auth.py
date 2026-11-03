from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.core.security import criar_access_token, verificar_senha
from api.repositories import usuario_repository
from api.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenResponse)
def login(
    dados: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    usuario = usuario_repository.buscar_por_email(db, str(dados.email))

    if (
        usuario is None
        or not verificar_senha(dados.senha, usuario.senha)
        or not usuario.ativo
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = criar_access_token(str(usuario.idusuarios))

    return TokenResponse(access_token=token)
