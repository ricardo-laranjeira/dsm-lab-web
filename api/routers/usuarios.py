
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.core.security import hash_senha, verificar_senha
from api.dependencies.auth import get_usuario_atual
from api.models.usuario import Usuario
from api.repositories import usuario_repository
from api.schemas.senha import SenhaUpdate

from api.schemas.usuario import (
    UsuarioPerfilUpdate,
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
)

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.get("/me", response_model=UsuarioResponse)
def obter_meu_perfil(
    usuario_atual: Usuario = Depends(get_usuario_atual),
) -> Usuario:
    """Retorna os dados do usuário autenticado."""
    return usuario_atual


@router.patch("/me", response_model=UsuarioResponse)
def atualizar_meu_perfil(
    dados: UsuarioPerfilUpdate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
) -> Usuario:
    """Atualiza nome e e-mail do usuário autenticado."""
    alteracoes = dados.model_dump(exclude_unset=True)

    if not alteracoes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Informe pelo menos um campo para atualizar.",
        )

    if "nome" in alteracoes and alteracoes["nome"] is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="O nome não pode ser nulo.",
        )

    if "email" in alteracoes and alteracoes["email"] is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="O e-mail não pode ser nulo.",
        )

    if "email" in alteracoes:
        email = str(alteracoes["email"])
        outro_usuario = usuario_repository.buscar_por_email(db, email)

        if (
            outro_usuario is not None
            and outro_usuario.idusuarios != usuario_atual.idusuarios
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não foi possível concluir a atualização.",
            )

        alteracoes["email"] = email

    for campo, valor in alteracoes.items():
        setattr(usuario_atual, campo, valor)

    try:
        db.commit()
        db.refresh(usuario_atual)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não foi possível atualizar os dados informados.",
        ) from None

    return usuario_atual


@router.patch("/me/senha", status_code=status.HTTP_204_NO_CONTENT)
def atualizar_minha_senha(
    dados: SenhaUpdate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
) -> None:
    """Altera a senha após validar a senha atual."""
    if not verificar_senha(
        dados.senha_atual,
        usuario_atual.senha,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A senha atual está incorreta.",
        )

    usuario_atual.senha = hash_senha(dados.nova_senha)
    db.commit()


@router.post(
    "/",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_usuario(
    dados: UsuarioCreate,
    db: Session = Depends(get_db),
) -> Usuario:
    if usuario_repository.buscar_por_email(db, str(dados.email)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não foi possível concluir o cadastro.",
        )

    try:
        return usuario_repository.criar(db, dados)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não foi possível concluir o cadastro.",
        ) from exc


@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    usuario_atual: Usuario = Depends(get_usuario_atual),
) -> list[UsuarioResponse]:
    # A listagem geral será habilitada quando houver autorização
    # administrativa no modelo de usuários.
    del offset, limit, usuario_atual

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="A listagem geral exige permissão administrativa.",
    )


@router.get("/{idusuarios}", response_model=UsuarioResponse)
def buscar_usuario(
    idusuarios: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
) -> Usuario:
    if idusuarios != usuario_atual.idusuarios:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode consultar o próprio cadastro.",
        )

    usuario = usuario_repository.buscar_por_id(db, idusuarios)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    return usuario


@router.patch("/{idusuarios}", response_model=UsuarioResponse)
def atualizar_usuario(
    idusuarios: int,
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
) -> Usuario:
    if idusuarios != usuario_atual.idusuarios:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode atualizar o próprio cadastro.",
        )

    usuario = usuario_repository.buscar_por_id(db, idusuarios)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    alteracoes = dados.model_dump(exclude_unset=True)

    # O usuário não pode alterar seu próprio status de ativação.
    if "ativo" in alteracoes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não pode alterar o próprio status de ativação.",
        )

    if "email" in alteracoes and alteracoes["email"] is not None:
        email = str(alteracoes["email"])
        existente = usuario_repository.buscar_por_email(db, email)

        if existente is not None and existente.idusuarios != idusuarios:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não foi possível concluir a atualização.",
            )

    try:
        return usuario_repository.atualizar(db, usuario, dados)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflito ao atualizar o usuário.",
        ) from exc

@router.delete(
    "/{idusuarios}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def excluir_usuario(
    idusuarios: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
) -> None:
    if idusuarios != usuario_atual.idusuarios:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode excluir o próprio cadastro.",
        )

    usuario = usuario_repository.buscar_por_id(db, idusuarios)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    usuario_repository.excluir(db, usuario)
