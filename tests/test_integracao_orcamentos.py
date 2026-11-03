"""Teste ponta a ponta: orçamento + materiais + serviços."""
from datetime import date, timedelta

import pytest


def cadastrar_usuario(client, nome, email):
    r = client.post("/usuarios/",
                    json={"nome": nome, "email": email, "senha": "SenhaSegura123!"})
    assert r.status_code == 201, r.text
    return r.json()


def obter_token(client, email):
    r = client.post(
        "/auth/login",
        json={"email": email, "senha": "SenhaSegura123!"},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def cadastrar_cliente(client, token):
    r = client.post("/clientes/",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"nome": "Cliente Integração",
                          "telefone": "11999990000",
                          "ativo": True})
    assert r.status_code == 201, r.text
    return r.json()


def cadastrar_categoria(client, token):
    r = client.post("/categorias/", headers={"Authorization": f"Bearer {token}"},
                    json={"descricao": "Categoria Integração"})
    assert r.status_code == 201, r.text
    return r.json()


def cadastrar_material(client, token, categoria_id):
    r = client.post("/materiais/", headers={"Authorization": f"Bearer {token}"},
                    json={"descricao": "Tinta Integração", "valor": 25.50,
                          "unidade_medida": "un", "categorias_id": categoria_id})
    assert r.status_code == 201, r.text
    return r.json()


def cadastrar_servico(client, token, categoria_id):
    r = client.post("/servicos/", headers={"Authorization": f"Bearer {token}"},
                    json={"descricao": "Pintura Integração", "valor": 100.00,
                          "categorias_id": categoria_id})
    assert r.status_code == 201, r.text
    return r.json()


def criar_orcamento(client, token, cliente_id):
    r = client.post("/orcamentos/", headers={"Authorization": f"Bearer {token}"},
                    json={"validade": (date.today() + timedelta(days=15)).isoformat(),
                          "status": True, "clientes_id": cliente_id})
    assert r.status_code == 201, r.text
    return r.json()


@pytest.fixture
def contexto_integracao(client):
    email = "integracao@example.com"
    cadastrar_usuario(client, "Usuário Integração", email)
    token = obter_token(client, email)
    cliente = cadastrar_cliente(client, token)
    categoria = cadastrar_categoria(client, token)
    material = cadastrar_material(client,
                                  token, categoria["idcategorias"])
    servico = cadastrar_servico(client,
                                token, categoria["idcategorias"])
    orcamento = criar_orcamento(
        client, token, cliente["idclientes"])
    return {"token": token,
            "material": material,
            "servico": servico,
            "orcamento": orcamento}


def test_fluxo_completo_orcamento_materiais_e_servicos(client,
                                                       contexto_integracao):
    ctx = contexto_integracao
    token = ctx["token"]
    oid = ctx["orcamento"]["idorcamentos"]
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post(f"/orcamentos/{oid}/materiais", headers=headers,
                    json={"materiais_id": ctx["material"]["idmateriais"],
                          "quantidade": 3})
    assert r.status_code in (200, 201), r.text

    r = client.post(f"/orcamentos/{oid}/servicos", headers=headers,
                    json={"servicos_id": ctx["servico"]["idservicos"],
                          "quantidade": 2})
    assert r.status_code in (200, 201), r.text

    r = client.get(f"/orcamentos/{oid}/materiais", headers=headers)
    assert r.status_code == 200, r.text
    materiais = r.json()
    assert any(
        x["materiais_id"] == ctx["material"]["idmateriais"]
        and x["quantidade"] == 3
               for x in materiais)

    r = client.get(f"/orcamentos/{oid}/servicos", headers=headers)
    assert r.status_code == 200, r.text
    servicos = r.json()
    assert any(x["servicos_id"] == ctx["servico"]["idservicos"] and x["quantidade"] == 2
               for x in servicos)

    r = client.get(f"/orcamentos/{oid}", headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["idorcamentos"] == oid


def test_usuario_nao_acessa_itens_de_orcamento_alheio(client,
                                                      contexto_integracao):
    ctx = contexto_integracao
    email = "outro-integracao@example.com"
    cadastrar_usuario(client, "Outro Usuário", email)
    outro_token = obter_token(client, email)
    oid = ctx["orcamento"]["idorcamentos"]

    r = client.get(f"/orcamentos/{oid}/materiais",
                   headers={"Authorization": f"Bearer {outro_token}"})
    assert r.status_code in (403, 404), r.text

    r = client.post(f"/orcamentos/{oid}/servicos",
                    headers={"Authorization": f"Bearer {outro_token}"},
                    json={"servicos_id": ctx["servico"]["idservicos"], "quantidade": 1})
    assert r.status_code in (403, 404), r.text
