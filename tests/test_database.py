
from unittest.mock import MagicMock, patch

from api.core import database


def test_criar_engine_sqlite_configura_check_same_thread():
    with patch("api.core.database.create_engine") as create_engine:
        resultado = database._criar_engine("sqlite:///./teste.db")

        create_engine.assert_called_once_with(
            "sqlite:///./teste.db",
            connect_args={"check_same_thread": False},
        )

        assert resultado is create_engine.return_value


def test_criar_engine_nao_sqlite_sem_argumento_especifico():
    # URL fictícia: o engine é simulado, nenhuma conexão é realizada.
    with patch("api.core.database.create_engine") as create_engine:
        resultado = database._criar_engine("outro://teste")

        create_engine.assert_called_once_with(
            "outro://teste",
            connect_args={},
        )

        assert resultado is create_engine.return_value


def test_get_db_fecha_sessao():
    sessao = MagicMock()

    with patch.object(database, "SessionLocal", return_value=sessao):
        gerador = database.get_db()

        assert next(gerador) is sessao

        gerador.close()

        sessao.close.assert_called_once()
