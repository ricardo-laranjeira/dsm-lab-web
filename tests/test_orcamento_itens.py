from datetime import date, timedelta

SENHA = "SenhaSegura123!"


def headers_usuario(client, suffix):
    email = f"{suffix}@example.com"
    r = client.post("/usuarios/",
                    json={"nome": suffix,
                          "email": email,
                          "senha": SENHA})
    assert r.status_code == 201, r.text
    r = client.post("/auth/login",
                    json={"email": email,
                          "senha": SENHA})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def criar_cliente(client, h, s):
    r = client.post("/clientes/",
                    json={"nome": s,
                          "telefone": "11999990000",
                          "ativo": True},
                    headers=h)
    assert r.status_code == 201, r.text
    return r.json()


def preparar(client, s):
    h = headers_usuario(client, s)
    c = criar_cliente(client, h, s)
    r = client.post("/categorias/",
                    json={"descricao": "Categoria "+s},
                    headers=h)
    assert r.status_code == 201, r.text
    cat = r.json()["idcategorias"]
    r = client.post("/materiais/",
                    json={"descricao": "Cimento",
                          "valor": "25.50",
                          "unidade_medida": "saco",
                          "categorias_id": cat},
                    headers=h)
    assert r.status_code == 201, r.text
    mat = r.json()
    r = client.post("/servicos/",
                    json={"descricao": "Pintura",
                          "valor": "150.00",
                          "categorias_id": cat},
                    headers=h)
    assert r.status_code == 201, r.text
    serv = r.json()
    r = client.post("/orcamentos/",
                    json={"validade": (date.today()+timedelta(days=30)).isoformat(),
                          "status": True,
                          "clientes_id": c["idclientes"]},
                    headers=h)
    assert r.status_code == 201, r.text
    return h, r.json(), mat, serv


def test_crud_materiais_do_orcamento(client):
    h, o, m, _ = preparar(client, "itens-mat")
    base = f"/orcamentos/{o['idorcamentos']}/materiais/"
    mid = m["idmateriais"]
    r = client.post(base,
                    json={"materiais_id": mid, "quantidade": 3},
                    headers=h)
    assert r.status_code == 201, r.text
    assert r.json()["quantidade"] == 3
    assert len(client.get(base, headers=h).json()) == 1
    r = client.patch(base+str(mid),
                     json={"quantidade": 5},
                     headers=h)
    assert r.status_code == 200
    assert r.json()["quantidade"] == 5
    assert client.delete(base+str(mid), headers=h).status_code == 204
    assert client.get(base, headers=h).json() == []


def test_crud_servicos_do_orcamento(client):
    h, o, _, s = preparar(client, "itens-serv")
    base = f"/orcamentos/{o['idorcamentos']}/servicos/"
    sid = s["idservicos"]
    r = client.post(base,
                    json={"servicos_id": sid,
                          "quantidade": 2},
                    headers=h)
    assert r.status_code == 201, r.text
    assert len(client.get(base, headers=h).json()) == 1
    r = client.patch(base+str(sid),
                     json={"quantidade": 4},
                     headers=h)
    assert r.status_code == 200
    assert r.json()["quantidade"] == 4
    assert client.delete(base+str(sid), headers=h).status_code == 204
    assert client.get(base, headers=h).json() == []


def test_itens_exigem_autenticacao(client):
    assert client.get("/orcamentos/1/materiais/").status_code in (401, 403)
    assert client.get("/orcamentos/1/servicos/").status_code in (401, 403)


def test_validacoes_e_itens_inexistentes(client):
    h, o, m, s = preparar(client, "itens-invalidos")
    oid = o["idorcamentos"]
    assert client.get("/orcamentos/999999/materiais/",
                      headers=h).status_code == 404
    assert client.get("/orcamentos/999999/servicos/",
                      headers=h).status_code == 404
    assert client.post(f"/orcamentos/{oid}/materiais/",
                       json={"materiais_id": 999999, "quantidade": 1},
                       headers=h).status_code == 404
    assert client.post(f"/orcamentos/{oid}/servicos/",
                       json={"servicos_id": 999999, "quantidade": 1},
                       headers=h).status_code == 404
    assert client.post(f"/orcamentos/{oid}/materiais/",
                       json={"materiais_id": m["idmateriais"], "quantidade": 0},
                       headers=h).status_code == 422
    assert client.post(f"/orcamentos/{oid}/servicos/",
                       json={"servicos_id": s["idservicos"], "quantidade": -1},
                       headers=h).status_code == 422


def test_usuario_nao_acessa_itens_de_orcamento_alheio(client):
    _, o, m, s = preparar(client, "dono-itens")
    h2 = headers_usuario(client, "outro-dono-itens")
    oid = o["idorcamentos"]
    assert client.get(f"/orcamentos/{oid}/materiais/",
                      headers=h2).status_code == 404
    assert client.get(f"/orcamentos/{oid}/servicos/",
                      headers=h2).status_code == 404
    assert client.post(f"/orcamentos/{oid}/materiais/",
                       json={"materiais_id": m["idmateriais"], "quantidade": 1},
                       headers=h2).status_code == 404
    assert client.post(f"/orcamentos/{oid}/servicos/",
                       json={"servicos_id": s["idservicos"], "quantidade": 1},
                       headers=h2).status_code == 404


def test_atualizar_e_excluir_material_fora_do_orcamento(client):
    headers, orcamento, _, _ = preparar(client, "material-fora-orcamento")
    base = f"/orcamentos/{orcamento['idorcamentos']}/materiais/999999"

    atualizar = client.patch(
        base,
        json={"quantidade": 3},
        headers=headers,
    )
    assert atualizar.status_code == 404
    assert atualizar.json()["detail"] == "Material não está no orçamento."

    excluir = client.delete(base, headers=headers)
    assert excluir.status_code == 404
    assert excluir.json()["detail"] == "Material não está no orçamento."


def test_atualizar_e_excluir_servico_fora_do_orcamento(client):
    headers, orcamento, _, _ = preparar(client, "servico-fora-orcamento")
    base = f"/orcamentos/{orcamento['idorcamentos']}/servicos/999999"

    atualizar = client.patch(
        base,
        json={"quantidade": 3},
        headers=headers,
    )
    assert atualizar.status_code == 404
    assert atualizar.json()["detail"] == "Serviço não está no orçamento."

    excluir = client.delete(base, headers=headers)
    assert excluir.status_code == 404
    assert excluir.json()["detail"] == "Serviço não está no orçamento."
