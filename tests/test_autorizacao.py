from unittest.mock import patch, Mock

from sqlalchemy.exc import IntegrityError

from api.repositories import usuario_repository
from api.repositories.base_repository import BaseRepository
from api.repositories.usuario_repository import UsuarioRepository


def simular_usuario_inexistente(buscar_original, id_usuario):
    chamadas = 0

    def buscar(db, idusuarios):
        nonlocal chamadas

        if idusuarios == id_usuario:
            chamadas += 1
            if chamadas == 2:
                return None

        return buscar_original(db, idusuarios)

    return buscar


def cadastrar_usuario(client, nome, email):
    resposta = client.post(
        "/usuarios/",
        json={
            "nome": nome,
            "email": email,
            "senha": "SenhaSegura123!",
        },
    )

    assert resposta.status_code == 201
    return resposta.json()


def obter_token(client, email):
    resposta = client.post(
        "/auth/login",
        json={
            "email": email,
            "senha": "SenhaSegura123!",
        },
    )

    assert resposta.status_code == 200
    return resposta.json()["access_token"]


def criar_dois_usuarios(client):
    usuario_a = cadastrar_usuario(
        client,
        "Usuario A",
        "usuario.a@example.com",
    )
    usuario_b = cadastrar_usuario(
        client,
        "Usuario B",
        "usuario.b@example.com",
    )

    token_a = obter_token(client, "usuario.a@example.com")

    return usuario_a, usuario_b, token_a


def test_nao_pode_consultar_outro_usuario(client):
    usuario_a, usuario_b, token_a = criar_dois_usuarios(client)

    resposta = client.get(
        f"/usuarios/{usuario_b['idusuarios']}",
        headers={"Authorization": f"Bearer {token_a}"},
    )

    assert usuario_a["idusuarios"] != usuario_b["idusuarios"]
    assert resposta.status_code == 403


def test_nao_pode_atualizar_outro_usuario(client):
    _, usuario_b, token_a = criar_dois_usuarios(client)

    resposta = client.patch(
        f"/usuarios/{usuario_b['idusuarios']}",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"nome": "Nome alterado indevidamente"},
    )

    assert resposta.status_code == 403


def test_nao_pode_excluir_outro_usuario(client):
    _, usuario_b, token_a = criar_dois_usuarios(client)

    resposta = client.delete(
        f"/usuarios/{usuario_b['idusuarios']}",
        headers={"Authorization": f"Bearer {token_a}"},
    )

    assert resposta.status_code == 403


def test_nao_pode_alterar_proprio_status_ativo(client):
    usuario_a, _, token_a = criar_dois_usuarios(client)

    resposta = client.patch(
        f"/usuarios/{usuario_a['idusuarios']}",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"ativo": False},
    )

    assert resposta.status_code == 403


def test_listagem_geral_exige_permissao_administrativa(client):
    _, _, token_a = criar_dois_usuarios(client)

    resposta = client.get(
        "/usuarios/",
        headers={"Authorization": f"Bearer {token_a}"},
    )

    assert resposta.status_code == 403


def test_pode_atualizar_proprio_nome(client):
    usuario_a, _, token_a = criar_dois_usuarios(client)

    resposta = client.patch(
        f"/usuarios/{usuario_a['idusuarios']}",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"nome": "Nome atualizado"},
    )

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Nome atualizado"


def test_nao_pode_atualizar_email_de_outro_usuario(client):
    usuario_a, usuario_b, token_a = criar_dois_usuarios(client)

    resposta = client.patch(
        f"/usuarios/{usuario_a['idusuarios']}",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"email": usuario_b["email"]},
    )

    assert resposta.status_code == 409


def test_pode_excluir_proprio_usuario(client):
    usuario_a, _, token_a = criar_dois_usuarios(client)

    resposta = client.delete(
        f"/usuarios/{usuario_a['idusuarios']}",
        headers={"Authorization": f"Bearer {token_a}"},
    )

    assert resposta.status_code == 204
    assert resposta.content == b""


def test_buscar_proprio_usuario_inexistente(client):
    usuario_a, _, token_a = criar_dois_usuarios(client)

    buscar_original = usuario_repository.buscar_por_id

    with patch.object(
            BaseRepository,
            "buscar_por_id",
            side_effect=simular_usuario_inexistente(
                buscar_original,
                usuario_a["idusuarios"],
            ),
    ):
        resposta = client.get(
            f"/usuarios/{usuario_a['idusuarios']}",
            headers={"Authorization": f"Bearer {token_a}"},
        )

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Usuário não encontrado."


def test_atualizar_proprio_usuario_inexistente(client):
    usuario_a, _, token_a = criar_dois_usuarios(client)

    buscar_original = usuario_repository.buscar_por_id

    with patch.object(
            BaseRepository,
            "buscar_por_id",
            side_effect=simular_usuario_inexistente(
                buscar_original,
                usuario_a["idusuarios"],
            ),
    ):
        resposta = client.patch(
            f"/usuarios/{usuario_a['idusuarios']}",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"nome": "Novo Nome"},
        )

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Usuário não encontrado."


def test_excluir_proprio_usuario_inexistente(client):
    usuario_a, _, token_a = criar_dois_usuarios(client)

    buscar_original = usuario_repository.buscar_por_id

    with patch.object(
            BaseRepository,
            "buscar_por_id",
            side_effect=simular_usuario_inexistente(
                buscar_original,
                usuario_a["idusuarios"],
            ),
    ):
        resposta = client.delete(
            f"/usuarios/{usuario_a['idusuarios']}",
            headers={"Authorization": f"Bearer {token_a}"},
        )

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Usuário não encontrado."


def test_erro_integridade_ao_atualizar_usuario(client):
    usuario_a, _, token_a = criar_dois_usuarios(client)

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
            f"/usuarios/{usuario_a['idusuarios']}",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"nome": "Novo Nome"},
        )

    assert resposta.status_code == 409
    assert resposta.json()["detail"] == "Conflito ao atualizar o usuário."

def test_simular_usuario_inexistente_para_outro_id(db_session):
    buscar_original = Mock(return_value="usuario_encontrado")

    buscar = simular_usuario_inexistente(
        buscar_original,
        id_usuario=1,
    )

    resultado = buscar(db_session, 2)

    assert resultado == "usuario_encontrado"
    buscar_original.assert_called_once_with(db_session, 2)
