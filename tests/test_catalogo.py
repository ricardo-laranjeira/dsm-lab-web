from decimal import Decimal

import pytest

from tests.helpers import criar_usuario_e_headers


def criar_categoria(client, headers, descricao="Materiais de construção"):
    resposta = client.post(
        "/categorias/", json={"descricao": descricao}, headers=headers
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def criar_material(client, headers, categorias_id, descricao="Cimento"):
    resposta = client.post(
        "/materiais/",
        json={
            "descricao": descricao,
            "valor": "39.90",
            "unidade_medida": "saco",
            "categorias_id": categorias_id,
        },
        headers=headers,
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def criar_servico(client, headers, categorias_id, descricao="Pintura"):
    resposta = client.post(
        "/servicos/",
        json={
            "descricao": descricao,
            "valor": "250.00",
            "categorias_id": categorias_id,
        },
        headers=headers,
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def test_rotas_do_catalogo_exigem_autenticacao(client):
    casos = [
        ("get", "/categorias/"),
        ("post", "/categorias/", {"descricao": "Teste"}),
        ("get", "/materiais/"),
        ("post", "/materiais/", {
            "descricao": "Cimento", "valor": "10.00",
            "unidade_medida": "saco", "categorias_id": 1,
        }),
        ("get", "/servicos/"),
        ("post", "/servicos/", {
            "descricao": "Pintura", "valor": "100.00", "categorias_id": 1,
        }),
    ]
    for metodo, url, *body in casos:
        kwargs = {"json": body[0]} if body else {}
        resposta = getattr(client, metodo)(url, **kwargs)
        assert resposta.status_code in (401, 403), (
            metodo, url, resposta.status_code, resposta.text
        )


def test_crud_categoria(client):
    headers = criar_usuario_e_headers(client, "crud-categoria")
    criada = criar_categoria(client, headers)
    categoria_id = criada["idcategorias"]

    assert criada["descricao"] == "Materiais de construção"
    assert "data_cadastro" in criada

    lista = client.get("/categorias/", headers=headers)
    assert lista.status_code == 200
    assert any(item["idcategorias"] == categoria_id for item in lista.json())

    busca = client.get(f"/categorias/{categoria_id}", headers=headers)
    assert busca.status_code == 200
    assert busca.json()["idcategorias"] == categoria_id

    atualizada = client.patch(
        f"/categorias/{categoria_id}",
        json={"descricao": "Materiais e ferramentas"},
        headers=headers,
    )
    assert atualizada.status_code == 200
    assert atualizada.json()["descricao"] == "Materiais e ferramentas"

    excluida = client.delete(f"/categorias/{categoria_id}", headers=headers)
    assert excluida.status_code == 204
    assert client.get(f"/categorias/{categoria_id}", headers=headers).status_code == 404


def test_categoria_inexistente_e_validacao(client):
    headers = criar_usuario_e_headers(client, "validacao-categoria")

    assert client.get("/categorias/999999", headers=headers).status_code == 404
    assert client.patch(
        "/categorias/999999", json={"descricao": "Nova"}, headers=headers
    ).status_code == 404
    assert client.delete("/categorias/999999", headers=headers).status_code == 404

    assert client.post(
        "/categorias/", json={"descricao": ""}, headers=headers
    ).status_code == 422
    assert client.post(
        "/categorias/", json={"descricao": "x" * 46}, headers=headers
    ).status_code == 422


def test_crud_material(client):
    headers = criar_usuario_e_headers(client, "crud-material")
    categoria = criar_categoria(client, headers, "Materiais")
    categoria_id = categoria["idcategorias"]

    criado = criar_material(client, headers, categoria_id)
    material_id = criado["idmateriais"]
    assert criado["descricao"] == "Cimento"
    assert Decimal(str(criado["valor"])) == Decimal("39.90")
    assert criado["categorias_id"] == categoria_id

    lista = client.get("/materiais/?offset=0&limit=10", headers=headers)
    assert lista.status_code == 200
    assert any(item["idmateriais"] == material_id for item in lista.json())

    busca = client.get(f"/materiais/{material_id}", headers=headers)
    assert busca.status_code == 200
    assert busca.json()["idmateriais"] == material_id

    atualizada = client.patch(
        f"/materiais/{material_id}",
        json={"descricao": "Cimento CP-II", "valor": "42.50"},
        headers=headers,
    )
    assert atualizada.status_code == 200
    assert atualizada.json()["descricao"] == "Cimento CP-II"
    assert Decimal(str(atualizada.json()["valor"])) == Decimal("42.50")

    excluida = client.delete(f"/materiais/{material_id}", headers=headers)
    assert excluida.status_code == 204
    assert client.get(f"/materiais/{material_id}", headers=headers).status_code == 404


def test_material_validacoes_e_nao_encontrado(client):
    headers = criar_usuario_e_headers(client, "validacao-material")

    assert client.get("/materiais/999999", headers=headers).status_code == 404
    assert client.patch(
        "/materiais/999999", json={"descricao": "Alterado"}, headers=headers
    ).status_code == 404
    assert client.delete("/materiais/999999", headers=headers).status_code == 404

    payload = {
        "descricao": "Cimento",
        "valor": "10.00",
        "unidade_medida": "saco",
        "categorias_id": 999999,
    }
    assert client.post("/materiais/", json=payload, headers=headers).status_code == 404

    categoria = criar_categoria(client, headers, "Categoria válida")
    material = criar_material(client, headers, categoria["idcategorias"])
    assert client.patch(
        f"/materiais/{material['idmateriais']}",
        json={"categorias_id": 999999},
        headers=headers,
    ).status_code == 404

    payload["categorias_id"] = categoria["idcategorias"]
    payload["valor"] = "-1.00"
    assert client.post("/materiais/", json=payload, headers=headers).status_code == 422

    payload["valor"] = "10.00"
    payload["descricao"] = "x" * 151
    assert client.post("/materiais/", json=payload, headers=headers).status_code == 422


def test_crud_servico(client):
    headers = criar_usuario_e_headers(client, "crud-servico")
    categoria = criar_categoria(client, headers, "Serviços")
    categoria_id = categoria["idcategorias"]

    criado = criar_servico(client, headers, categoria_id)
    servico_id = criado["idservicos"]
    assert criado["descricao"] == "Pintura"
    assert Decimal(str(criado["valor"])) == Decimal("250.00")
    assert criado["categorias_id"] == categoria_id

    lista = client.get("/servicos/?offset=0&limit=10", headers=headers)
    assert lista.status_code == 200
    assert any(item["idservicos"] == servico_id for item in lista.json())

    busca = client.get(f"/servicos/{servico_id}", headers=headers)
    assert busca.status_code == 200
    assert busca.json()["idservicos"] == servico_id

    atualizada = client.patch(
        f"/servicos/{servico_id}",
        json={"descricao": "Pintura interna", "valor": "275.50"},
        headers=headers,
    )
    assert atualizada.status_code == 200
    assert atualizada.json()["descricao"] == "Pintura interna"
    assert Decimal(str(atualizada.json()["valor"])) == Decimal("275.50")

    excluida = client.delete(f"/servicos/{servico_id}", headers=headers)
    assert excluida.status_code == 204
    assert client.get(f"/servicos/{servico_id}", headers=headers).status_code == 404


def test_servico_validacoes_e_nao_encontrado(client):
    headers = criar_usuario_e_headers(client, "validacao-servico")

    assert client.get("/servicos/999999", headers=headers).status_code == 404
    assert client.patch(
        "/servicos/999999", json={"descricao": "Alterado"}, headers=headers
    ).status_code == 404
    assert client.delete("/servicos/999999", headers=headers).status_code == 404

    payload = {
        "descricao": "Instalação",
        "valor": "100.00",
        "categorias_id": 999999,
    }
    assert client.post("/servicos/", json=payload, headers=headers).status_code == 404

    categoria = criar_categoria(client, headers, "Categoria de serviços")
    servico = criar_servico(client, headers, categoria["idcategorias"])
    assert client.patch(
        f"/servicos/{servico['idservicos']}",
        json={"categorias_id": 999999},
        headers=headers,
    ).status_code == 404

    payload["categorias_id"] = categoria["idcategorias"]
    payload["valor"] = "-0.01"
    assert client.post("/servicos/", json=payload, headers=headers).status_code == 422

    payload["valor"] = "100.00"
    payload["descricao"] = "x" * 151
    assert client.post("/servicos/", json=payload, headers=headers).status_code == 422


def test_catalogo_compartilhado_entre_usuarios(client):
    headers_a = criar_usuario_e_headers(client, "catalogo-usuario-a")
    headers_b = criar_usuario_e_headers(client, "catalogo-usuario-b")

    categoria = criar_categoria(client, headers_a, "Categoria compartilhada")
    categoria_id = categoria["idcategorias"]

    # O segundo usuário autenticado pode consultar e alterar a mesma categoria.
    resposta = client.get(f"/categorias/{categoria_id}", headers=headers_b)
    assert resposta.status_code == 200
    assert resposta.json()["descricao"] == "Categoria compartilhada"

    alterada = client.patch(
        f"/categorias/{categoria_id}",
        json={"descricao": "Alterada por outro usuário"},
        headers=headers_b,
    )
    assert alterada.status_code == 200
    assert alterada.json()["descricao"] == "Alterada por outro usuário"

    material = criar_material(client, headers_a, categoria_id)
    servico = criar_servico(client, headers_a, categoria_id)

    assert client.get(
        f"/materiais/{material['idmateriais']}", headers=headers_b
    ).status_code == 200
    assert client.get(
        f"/servicos/{servico['idservicos']}", headers=headers_b
    ).status_code == 200

    assert client.patch(
        f"/materiais/{material['idmateriais']}",
        json={"valor": "44.00"},
        headers=headers_b,
    ).status_code == 200
    assert client.patch(
        f"/servicos/{servico['idservicos']}",
        json={"valor": "300.00"},
        headers=headers_b,
    ).status_code == 200


@pytest.mark.parametrize(
    "endpoint",
    [
        "/categorias/",
        "/materiais/",
        "/servicos/",
    ],
)
def test_validacoes_de_paginacao(client, endpoint):
    headers = criar_usuario_e_headers(client, "paginacao-" + endpoint.strip("/"))
    # Os endpoints de listagem devem rejeitar limit fora de 1..100 e offset negativo.
    url = endpoint
    assert client.get(url + "?limit=0", headers=headers).status_code == 422
    assert client.get(url + "?limit=101", headers=headers).status_code == 422
    assert client.get(url + "?offset=-1", headers=headers).status_code == 422
