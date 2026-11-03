from datetime import date, timedelta

from tests.helpers import criar_usuario_e_headers


def criar_cliente(client, headers, sufixo="cliente"):
    resposta = client.post(
        "/clientes/",
        json={
            "nome": f"Cliente {sufixo}",
            "telefone": "11999990000",
            "ativo": True,
        },
        headers=headers,
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def criar_orcamento(client, headers, clientes_id, **extras):
    payload = {
        "validade": (date.today() + timedelta(days=30)).isoformat(),
        "status": True,
        "clientes_id": clientes_id,
    }
    payload.update(extras)
    resposta = client.post("/orcamentos/", json=payload, headers=headers)
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def test_rotas_orcamentos_exigem_autenticacao(client):
    resposta = client.get("/orcamentos/")
    assert resposta.status_code in (401, 403)


def test_crud_orcamento(client):
    headers = criar_usuario_e_headers(client, "crud-orcamento")
    cliente = criar_cliente(client, headers, "crud")
    clientes_id = cliente["idclientes"]

    criado = criar_orcamento(client, headers, clientes_id)
    orcamento_id = criado["idorcamentos"]

    assert criado["validade"] == (date.today() + timedelta(days=30)).isoformat()
    assert criado["status"] is True
    assert criado["clientes_id"] == clientes_id
    assert criado["usuarios_id"]
    assert "data_cadastro" in criado

    lista = client.get("/orcamentos/?offset=0&limit=10", headers=headers)
    assert lista.status_code == 200
    assert any(item["idorcamentos"] == orcamento_id for item in lista.json())

    busca = client.get(f"/orcamentos/{orcamento_id}", headers=headers)
    assert busca.status_code == 200
    assert busca.json()["idorcamentos"] == orcamento_id

    nova_validade = (date.today() + timedelta(days=60)).isoformat()
    atualizada = client.patch(
        f"/orcamentos/{orcamento_id}",
        json={"validade": nova_validade, "status": False},
        headers=headers,
    )
    assert atualizada.status_code == 200
    assert atualizada.json()["validade"] == nova_validade
    assert atualizada.json()["status"] is False

    excluida = client.delete(f"/orcamentos/{orcamento_id}", headers=headers)
    assert excluida.status_code == 204
    assert client.get(
        f"/orcamentos/{orcamento_id}", headers=headers
    ).status_code == 404


def test_orcamento_inexistente(client):
    headers = criar_usuario_e_headers(client, "orcamento-inexistente")
    assert client.get("/orcamentos/999999", headers=headers).status_code == 404
    assert client.patch(
        "/orcamentos/999999", json={"status": False}, headers=headers
    ).status_code == 404
    assert client.delete("/orcamentos/999999", headers=headers).status_code == 404


def test_nao_permite_criar_orcamento_para_cliente_inexistente(client):
    headers = criar_usuario_e_headers(client, "cliente-inexistente-orcamento")
    resposta = client.post(
        "/orcamentos/",
        json={
            "validade": (date.today() + timedelta(days=30)).isoformat(),
            "status": True,
            "clientes_id": 999999,
        },
        headers=headers,
    )
    assert resposta.status_code == 404


def test_usuario_nao_acessa_orcamento_de_outro_usuario(client):
    headers_a = criar_usuario_e_headers(client, "orcamento-dono-a")
    headers_b = criar_usuario_e_headers(client, "orcamento-dono-b")

    cliente_a = criar_cliente(client, headers_a, "dono-a")
    orcamento = criar_orcamento(client, headers_a, cliente_a["idclientes"])
    orcamento_id = orcamento["idorcamentos"]

    assert client.get(
        f"/orcamentos/{orcamento_id}", headers=headers_b
    ).status_code == 404
    assert client.patch(
        f"/orcamentos/{orcamento_id}",
        json={"status": False},
        headers=headers_b,
    ).status_code == 404
    assert client.delete(
        f"/orcamentos/{orcamento_id}", headers=headers_b
    ).status_code == 404

    lista_b = client.get("/orcamentos/", headers=headers_b)
    assert lista_b.status_code == 200
    assert all(item["idorcamentos"] != orcamento_id for item in lista_b.json())


def test_nao_permite_usar_cliente_de_outro_usuario(client):
    headers_a = criar_usuario_e_headers(client, "cliente-proprietario-a")
    headers_b = criar_usuario_e_headers(client, "cliente-proprietario-b")
    cliente_a = criar_cliente(client, headers_a, "privado-a")

    resposta = client.post(
        "/orcamentos/",
        json={
            "validade": (date.today() + timedelta(days=30)).isoformat(),
            "status": True,
            "clientes_id": cliente_a["idclientes"],
        },
        headers=headers_b,
    )
    assert resposta.status_code == 404


def test_nao_permite_alterar_orcamento_para_cliente_de_outro_usuario(client):
    headers_a = criar_usuario_e_headers(client, "alteracao-cliente-a")
    headers_b = criar_usuario_e_headers(client, "alteracao-cliente-b")
    cliente_a = criar_cliente(client, headers_a, "cliente-a")
    cliente_b = criar_cliente(client, headers_b, "cliente-b")
    orcamento = criar_orcamento(client, headers_a, cliente_a["idclientes"])

    resposta = client.patch(
        f"/orcamentos/{orcamento['idorcamentos']}",
        json={"clientes_id": cliente_b["idclientes"]},
        headers=headers_a,
    )
    assert resposta.status_code == 404


def test_validacoes_do_orcamento(client):
    headers = criar_usuario_e_headers(client, "validacoes-orcamento")
    cliente = criar_cliente(client, headers, "validacoes")

    base_payload = {
        "validade": (date.today() + timedelta(days=30)).isoformat(),
        "status": True,
        "clientes_id": cliente["idclientes"],
    }

    payload = {**base_payload, "validade": "data-invalida"}
    assert client.post(
        "/orcamentos/", json=payload, headers=headers
    ).status_code == 422

    payload = {**base_payload, "clientes_id": 0}
    assert client.post(
        "/orcamentos/", json=payload, headers=headers
    ).status_code == 422

    payload = {**base_payload, "status": "nao"}
    assert client.post(
        "/orcamentos/", json=payload, headers=headers
    ).status_code == 422


def test_paginacao_orcamentos(client):
    headers = criar_usuario_e_headers(client, "paginacao-orcamentos")
    assert client.get("/orcamentos/?limit=0", headers=headers).status_code == 422
    assert client.get("/orcamentos/?limit=101", headers=headers).status_code == 422
    assert client.get("/orcamentos/?offset=-1", headers=headers).status_code == 422
