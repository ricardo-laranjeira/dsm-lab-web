from datetime import date, timedelta

from sqlalchemy.exc import IntegrityError
from api.repositories.base_repository import BaseRepository

SENHA = "SenhaSegura123!"


def criar_usuario(client, nome, email):
    resposta = client.post(
        "/usuarios/",
        json={"nome": nome, "email": email, "senha": SENHA},
    )
    assert resposta.status_code == 201, resposta.text


def obter_token(client, email):
    resposta = client.post(
        "/auth/login",
        json={"email": email, "senha": SENHA},
    )
    assert resposta.status_code == 200, resposta.text
    return resposta.json()["access_token"]


def criar_cliente(client, token):
    resposta = client.post(
        "/clientes/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nome": "Cliente Agendamento",
            "telefone": "11999990000",
            "ativo": True,
        },
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def criar_orcamento(client, token, cliente_id):
    resposta = client.post(
        "/orcamentos/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "validade": (date.today() + timedelta(days=20)).isoformat(),
            "status": True,
            "clientes_id": cliente_id,
        },
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def preparar(client, sufixo="agendamento"):
    email = f"{sufixo}@example.com"
    criar_usuario(client, "Usuário Agendamento", email)
    token = obter_token(client, email)
    cliente = criar_cliente(client, token)
    orcamento = criar_orcamento(client, token, cliente["idclientes"])
    return token, orcamento


def payload_agendamento(orcamento):
    return {
        "data": (date.today() + timedelta(days=5)).isoformat(),
        "hora": "14:30:00",
        "orcamentos_id": orcamento["idorcamentos"],
    }


def test_crud_agendamento(client):
    token, orcamento = preparar(client)
    headers = {"Authorization": f"Bearer {token}"}
    resposta = client.post(
        "/agendamentos/",
        headers=headers,
        json=payload_agendamento(orcamento)
    )
    assert resposta.status_code == 201, resposta.text
    item = resposta.json()

    resposta = client.get("/agendamentos/",
                          headers=headers)
    assert resposta.status_code == 200, resposta.text
    assert any(x["idagendamentos"] == item["idagendamentos"] for x in resposta.json())

    resposta = client.patch(
        f"/agendamentos/{item['idagendamentos']}",
        headers=headers,
        json={"hora": "15:00:00"},
    )
    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["hora"] == "15:00:00"

    resposta = client.delete(
        f"/agendamentos/{item['idagendamentos']}",
        headers=headers
    )
    assert resposta.status_code == 204, resposta.text


def test_agendamentos_exigem_autenticacao(client):
    resposta = client.get("/agendamentos/")
    assert resposta.status_code == 401


def test_usuario_nao_acessa_agendamento_de_outro_usuario(client):
    token_a, orcamento = preparar(client, "usuario-a")
    resposta = client.post(
        "/agendamentos/",
        headers={"Authorization": f"Bearer {token_a}"},
        json=payload_agendamento(orcamento),
    )
    assert resposta.status_code == 201, resposta.text
    id_item = resposta.json()["idagendamentos"]

    criar_usuario(client, "Usuário B",
                  "usuario-b@example.com")
    token_b = obter_token(client,
                          "usuario-b@example.com")
    resposta = client.get(
        f"/agendamentos/{id_item}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resposta.status_code == 404


def test_nao_cria_agendamento_para_orcamento_inexistente(client):
    criar_usuario(client, "Usuário",
                  "sem-orcamento@example.com")
    token = obter_token(client,
                        "sem-orcamento@example.com")
    resposta = client.post(
        "/agendamentos/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "data": (date.today() + timedelta(days=5)).isoformat(),
            "hora": "14:30:00",
            "orcamentos_id": 99999,
        },
    )
    assert resposta.status_code == 404


def test_orcamento_nao_pode_ter_dois_agendamentos(client):
    token, orcamento = preparar(client, "unico-agendamento")
    headers = {"Authorization": f"Bearer {token}"}
    primeiro = client.post(
        "/agendamentos/",
        headers=headers,
        json=payload_agendamento(orcamento)
    )
    assert primeiro.status_code == 201, primeiro.text

    segundo_payload = payload_agendamento(orcamento)
    segundo_payload["hora"] = "16:00:00"
    segundo = client.post("/agendamentos/",
                          headers=headers,
                          json=segundo_payload)
    assert segundo.status_code == 409, segundo.text


def test_validacao_de_campos_obrigatorios(client):
    criar_usuario(client, "Usuário",
                  "validacao-agendamento@example.com")
    token = obter_token(client,
                        "validacao-agendamento@example.com")
    resposta = client.post(
        "/agendamentos/",
        headers={"Authorization": f"Bearer {token}"},
        json={"hora": "14:30:00", "orcamentos_id": 1},
    )
    assert resposta.status_code == 422

def test_obter_agendamento_inexistente(client):
    criar_usuario(client, "Usuário", "agendamento-inexistente@example.com")
    token = obter_token(client, "agendamento-inexistente@example.com")

    resposta = client.get(
        "/agendamentos/99999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Agendamento não encontrado"


def test_listar_agendamentos_sem_orcamentos(client):
    criar_usuario(client,
                  "Usuário",
                  "sem-agendamentos@example.com")
    token = obter_token(client,
                        "sem-agendamentos@example.com")

    resposta = client.get(
        "/agendamentos/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 200
    assert resposta.json() == []


def test_integrity_error_ao_criar_agendamento(client, monkeypatch):
    token, orcamento = preparar(client, "integrity-agendamento")

    def falhar_criacao(self, db, dados):
        raise IntegrityError(
            "INSERT INTO agendamentos",
            {},
            Exception("integrity error simulado"),
        )

    monkeypatch.setattr(
        BaseRepository,
        "criar",
        falhar_criacao,
    )

    resposta = client.post(
        "/agendamentos/",
        headers={"Authorization": f"Bearer {token}"},
        json=payload_agendamento(orcamento),
    )

    assert resposta.status_code == 409
    assert resposta.json()["detail"] == (
        "Este orçamento já possui um agendamento"
    )
