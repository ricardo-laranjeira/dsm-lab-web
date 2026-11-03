from sqlalchemy import select
from sqlalchemy.orm import Session

from api.core.security import hash_senha
from api.models.usuario import Usuario
from api.repositories.base_repository import BaseRepository
from api.schemas.usuario import UsuarioCreate, UsuarioUpdate


class UsuarioRepository(BaseRepository[Usuario]):
    def __init__(self):
        super().__init__(Usuario)

    def buscar_por_email(
        self,
        db: Session,
        email: str,
    ) -> Usuario | None:
        statement = select(Usuario).where(
            Usuario.email == email
        )
        return db.scalar(statement)

    def criar(
            self,
            db: Session,
            dados: UsuarioCreate,
    ) -> Usuario:
        usuario = Usuario(
            nome=dados.nome,
            email=str(dados.email),
            senha=hash_senha(dados.senha),
        )

        return self._salvar(db, usuario)

    def atualizar(
        self,
        db: Session,
        item: Usuario,
        dados: UsuarioUpdate,
    ) -> Usuario:
        alteracoes = dados.model_dump(
            exclude_unset=True
        )

        for campo, valor in alteracoes.items():
            setattr(item, campo, valor)

        db.commit()
        db.refresh(item)

        return item


usuario_repository = UsuarioRepository()
