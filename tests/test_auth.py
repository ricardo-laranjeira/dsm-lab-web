from api.core.security import criar_access_token
from api.models.usuario import Usuario
from tests.helpers import criar_usuario_e_headers
from unittest.mock import Mock, patch


def criar_usuario(client):
    return client.post(
        "/usuarios/",
        json={
            "nome": "João Teste",
            "email": "joao.teste@example.com",
            "senha": "SenhaSegura123!",
        },
    )


def test_login_com_credenciais_validas(client):
    cadastro = criar_usuario(client)
    assert cadastro.status_code == 201

    resposta = client.post(
        "/auth/login",
        json={
            "email": "joao.teste@example.com",
            "senha": "SenhaSegura123!",
        },
    )

    assert resposta.status_code == 200

    dados = resposta.json()
    assert "access_token" in dados
    assert dados["token_type"] == "bearer"
    assert isinstance(dados["access_token"], str)
    assert len(dados["access_token"]) > 0


def test_login_com_senha_incorreta(client):
    cadastro = criar_usuario(client)
    assert cadastro.status_code == 201

    resposta = client.post(
        "/auth/login",
        json={
            "email": "joao.teste@example.com",
            "senha": "SenhaErrada123!",
        },
    )

    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "E-mail ou senha inválidos."


def test_login_com_email_inexistente(client):
    resposta = client.post(
        "/auth/login",
        json={
            "email": "inexistente@example.com",
            "senha": "SenhaSegura123!",
        },
    )

    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "E-mail ou senha inválidos."


def test_acessar_rota_protegida_sem_token(client):
    cadastro = criar_usuario(client)
    assert cadastro.status_code == 201

    idusuario = cadastro.json()["idusuarios"]

    resposta = client.get(f"/usuarios/{idusuario}")

    assert resposta.status_code == 401
    assert (
        resposta.json()["detail"]
        == "Token ausente, inválido ou expirado."
    )


def test_acessar_rota_protegida_com_token_invalido(client):
    cadastro = criar_usuario(client)
    assert cadastro.status_code == 201

    idusuario = cadastro.json()["idusuarios"]

    resposta = client.get(
        f"/usuarios/{idusuario}",
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert resposta.status_code == 401
    assert (
        resposta.json()["detail"]
        == "Token ausente, inválido ou expirado."
    )


def test_acessar_proprio_usuario_com_token_valido(client):
    cadastro = criar_usuario(client)
    assert cadastro.status_code == 201

    idusuario = cadastro.json()["idusuarios"]

    login = client.post(
        "/auth/login",
        json={
            "email": "joao.teste@example.com",
            "senha": "SenhaSegura123!",
        },
    )

    assert login.status_code == 200
    token = login.json()["access_token"]

    resposta = client.get(
        f"/usuarios/{idusuario}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 200
    assert resposta.json()["idusuarios"] == idusuario


def test_token_com_identificador_invalido(client):
    token = criar_access_token("abc")

    resposta = client.get(
        "/usuarios/1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 401
    assert (
        resposta.json()["detail"]
        == "Token ausente, inválido ou expirado."
    )


def test_usuario_inativo_nao_pode_fazer_login(
    client,
    db_session,
):
    cadastro = client.post(
        "/usuarios/",
        json={
            "nome": "Usuario Inativo",
            "email": "inativo@example.com",
            "senha": "SenhaSegura123!",
        },
    )

    assert cadastro.status_code == 201

    idusuario = cadastro.json()["idusuarios"]
    usuario = db_session.get(Usuario, idusuario)

    assert usuario is not None

    usuario.ativo = False
    db_session.commit()

    resposta = client.post(
        "/auth/login",
        json={
            "email": "inativo@example.com",
            "senha": "SenhaSegura123!",
        },
    )

    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "E-mail ou senha inválidos."

def test_token_com_usuario_inexistente(client):
    token = criar_access_token("999999")

    resposta = client.get(
        "/usuarios/1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 401
    assert resposta.json()["detail"] == (
        "Token ausente, inválido ou expirado."
    )


def test_usuario_inativo_nao_pode_acessar_rota_protegida(
    client,
    db_session,
):
    cadastro = criar_usuario(client)
    assert cadastro.status_code == 201

    idusuario = cadastro.json()["idusuarios"]
    usuario = db_session.get(Usuario, idusuario)

    assert usuario is not None

    usuario.ativo = False
    db_session.commit()

    token = criar_access_token(str(idusuario))

    resposta = client.get(
        f"/usuarios/{idusuario}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 401
    assert resposta.json()["detail"] == (
        "Token ausente, inválido ou expirado."
    )

def test_criar_usuario_e_headers_com_fallback(client):
    resposta_cadastro = Mock(status_code=201, text="")
    resposta_login_inicial = Mock(status_code=422, text="Formato inválido")
    resposta_login_fallback = Mock(
        status_code=200,
        text="",
    )
    resposta_login_fallback.json.return_value = {
        "access_token": "token-de-teste",
    }

    with patch.object(client, client.post.__name__) as post_mock:
        post_mock.side_effect = [
            resposta_cadastro,
            resposta_login_inicial,
            resposta_login_fallback,
        ]

        headers = criar_usuario_e_headers(client, "fallback")

    assert headers == {
        "Authorization": "Bearer token-de-teste",
    }

    assert post_mock.call_count == 3

    chamada_login_fallback = post_mock.call_args_list[2]
    assert chamada_login_fallback.kwargs["data"] == {
        "username": "fallback@example.com",
        "password": "SenhaSegura123!",
    }
