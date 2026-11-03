from unittest.mock import patch

from sqlalchemy.exc import IntegrityError

from api.repositories.usuario_repository import UsuarioRepository


def test_criar_usuario_com_sucesso(client):
    resposta = client.post(
        "/usuarios/",
        json={
            "nome": "Maria Silva",
            "email": "maria.teste@example.com",
            "senha": "SenhaSegura123!",
        },
    )

    assert resposta.status_code == 201

    dados = resposta.json()
    assert dados["nome"] == "Maria Silva"
    assert dados["email"] == "maria.teste@example.com"
    assert "idusuarios" in dados
    assert "senha" not in dados


def test_criar_usuario_com_email_duplicado(client):
    dados_usuario = {
        "nome": "Maria Silva",
        "email": "maria.teste@example.com",
        "senha": "SenhaSegura123!",
    }

    primeira_resposta = client.post(
        "/usuarios/",
        json=dados_usuario,
    )

    segunda_resposta = client.post(
        "/usuarios/",
        json={
            **dados_usuario,
            "nome": "Maria Souza",
        },
    )

    assert primeira_resposta.status_code == 201
    assert segunda_resposta.status_code == 409
    assert (
        segunda_resposta.json()["detail"]
        == "Não foi possível concluir o cadastro."
    )


def test_criar_usuario_com_email_invalido(client):
    resposta = client.post(
        "/usuarios/",
        json={
            "nome": "Maria Silva",
            "email": "email-invalido",
            "senha": "SenhaSegura123!",
        },
    )

    assert resposta.status_code == 422


def test_criar_usuario_sem_campos_obrigatorios(client):
    resposta = client.post(
        "/usuarios/",
        json={},
    )

    assert resposta.status_code == 422

def test_erro_integridade_ao_criar_usuario(client):
    with patch.object(
            UsuarioRepository,
            UsuarioRepository.criar.__name__,
            side_effect=IntegrityError(
                "INSERT",
                {},
                Exception("Erro simulado"),
            ),
    ):
        resposta = client.post(
            "/usuarios/",
            json={
                "nome": "Usuario Teste",
                "email": "teste@example.com",
                "senha": "SenhaSegura123!",
            },
        )

    assert resposta.status_code == 409
    assert resposta.json()["detail"] == (
        "Não foi possível concluir o cadastro."
    )

def test_erro_integridade_ao_atualizar_usuario(client):
    cadastro = client.post(
        "/usuarios/",
        json={
            "nome": "Usuario Teste",
            "email": "teste.atualizar@example.com",
            "senha": "SenhaSegura123!",
        },
    )
    assert cadastro.status_code == 201

    idusuario = cadastro.json()["idusuarios"]

    login = client.post(
        "/auth/login",
        json={
            "email": "teste.atualizar@example.com",
            "senha": "SenhaSegura123!",
        },
    )
    assert login.status_code == 200

    token = login.json()["access_token"]

    with patch.object(
            UsuarioRepository,
            UsuarioRepository.atualizar.__name__,
            side_effect=IntegrityError(
                "UPDATE",
                {},
                Exception("Erro simulado"),
            ),
    ):
        resposta = client.patch(
            f"/usuarios/{idusuario}",
            json={"nome": "Nome Atualizado"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert resposta.status_code == 409
    assert resposta.json()["detail"] == (
        "Conflito ao atualizar o usuário."
    )


def test_atualizar_usuario_mantendo_o_proprio_email(client):
    email = "manter.email@example.com"
    senha = "SenhaSegura123!"

    cadastro = client.post(
        "/usuarios/",
        json={
            "nome": "Usuario Teste",
            "email": email,
            "senha": senha,
        },
    )
    assert cadastro.status_code == 201

    idusuario = cadastro.json()["idusuarios"]

    login = client.post(
        "/auth/login",
        json={
            "email": email,
            "senha": senha,
        },
    )
    assert login.status_code == 200

    token = login.json()["access_token"]

    resposta = client.patch(
        f"/usuarios/{idusuario}",
        json={"email": email},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 200
    assert resposta.json()["email"] == email
