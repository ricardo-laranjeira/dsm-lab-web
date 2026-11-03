def criar_usuario_e_token(client, sufixo):
    resposta = client.post(
        "/usuarios/",
        json={
            "nome": f"Usuário {sufixo}",
            "email": f"{sufixo}@example.com",
            "senha": "SenhaSegura123!",
        },
    )
    assert resposta.status_code == 201
    login = client.post(
        "/auth/login",
        json={
            "email": f"{sufixo}@example.com",
            "senha": "SenhaSegura123!",
        },
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def payload_cliente(nome="Cliente Teste"):
    return {"nome": nome, "telefone": "11999998888", "ativo": True}


def payload_endereco():
    return {
        "cep": "01001-000",
        "endereco": "Praça da Sé",
        "numero": "100",
        "complemento": None,
        "bairro": "Sé",
        "cidade": "São Paulo",
        "estado": "SP",
    }


def test_criar_listar_atualizar_excluir_cliente(client):
    headers = criar_usuario_e_token(client, "cliente-crud")
    criado = client.post("/clientes/", json=payload_cliente(), headers=headers)
    assert criado.status_code == 201
    cliente = criado.json()
    assert cliente["nome"] == "Cliente Teste"
    assert cliente["usuarios_id"] > 0
    assert cliente["data_cadastro"]

    lista = client.get("/clientes/", headers=headers)
    assert lista.status_code == 200
    assert any(item["idclientes"] == cliente["idclientes"] for item in lista.json())

    atualizado = client.patch(
        f"/clientes/{cliente['idclientes']}",
        json={"nome": "Nome atualizado"},
        headers=headers,
    )
    assert atualizado.status_code == 200
    assert atualizado.json()["nome"] == "Nome atualizado"

    excluido = client.delete(f"/clientes/{cliente['idclientes']}", headers=headers)
    assert excluido.status_code == 204
    assert client.get(f"/clientes/{cliente['idclientes']}",
                      headers=headers).status_code == 404


def test_usuario_nao_acessa_cliente_de_outro_usuario(client):
    dono = criar_usuario_e_token(client, "dono-cliente")
    outro = criar_usuario_e_token(client, "outro-cliente")
    resposta = client.post("/clientes/", json=payload_cliente(), headers=dono)
    idcliente = resposta.json()["idclientes"]

    assert client.get(f"/clientes/{idcliente}", headers=outro).status_code == 404
    assert client.patch(
        f"/clientes/{idcliente}", json={"nome": "Intrusão"}, headers=outro
    ).status_code == 404
    assert client.delete(f"/clientes/{idcliente}", headers=outro).status_code == 404


def test_criar_listar_atualizar_excluir_endereco(client):
    headers = criar_usuario_e_token(client, "endereco-crud")
    cliente = client.post("/clientes/", json=payload_cliente(), headers=headers).json()
    base = f"/clientes/{cliente['idclientes']}/enderecos"

    criado = client.post(base + "/", json=payload_endereco(), headers=headers)
    assert criado.status_code == 201
    endereco = criado.json()
    assert endereco["cliente_id"] == cliente["idclientes"]
    assert endereco["data_cadastro"]

    lista = client.get(base + "/", headers=headers)
    assert lista.status_code == 200
    assert len(lista.json()) == 1

    buscado = client.get(
        f"{base}/{endereco['idenderecos']}",
        headers=headers,
    )
    assert buscado.status_code == 200
    assert buscado.json()["idenderecos"] == endereco["idenderecos"]

    atualizado = client.patch(
        f"{base}/{endereco['idenderecos']}",
        json={"cidade": "Campinas"},
        headers=headers,
    )
    assert atualizado.status_code == 200
    assert atualizado.json()["cidade"] == "Campinas"

    excluido = client.delete(f"{base}/{endereco['idenderecos']}",
                             headers=headers)
    assert excluido.status_code == 204
    assert client.get(f"{base}/{endereco['idenderecos']}",
                      headers=headers).status_code == 404


def test_nao_acessa_endereco_de_cliente_de_outro_usuario(client):
    dono = criar_usuario_e_token(client, "dono-endereco")
    outro = criar_usuario_e_token(client, "outro-endereco")
    cliente = client.post("/clientes/", json=payload_cliente(), headers=dono).json()
    base = f"/clientes/{cliente['idclientes']}/enderecos"
    endereco = client.post(base + "/", json=payload_endereco(), headers=dono).json()

    caminho = f"{base}/{endereco['idenderecos']}"
    assert client.get(caminho, headers=outro).status_code == 404
    assert client.patch(caminho,
                        json={"cidade": "Invasão"}, headers=outro).status_code == 404
    assert client.delete(caminho, headers=outro).status_code == 404


def test_rotas_exigem_autenticacao(client):
    assert client.get("/clientes/").status_code == 401
    assert client.get("/clientes/1/enderecos/").status_code == 401


def test_complemento_pode_ser_nulo_e_campos_obrigatorios(client):
    headers = criar_usuario_e_token(client, "endereco-validacao")
    cliente = client.post("/clientes/", json=payload_cliente(), headers=headers).json()
    base = f"/clientes/{cliente['idclientes']}/enderecos"

    resposta = client.post(base + "/", json=payload_endereco(), headers=headers)
    assert resposta.status_code == 201
    invalido = payload_endereco()
    del invalido["cep"]
    assert client.post(base + "/", json=invalido, headers=headers).status_code == 422


def test_operacoes_com_endereco_inexistente(client):
    headers = criar_usuario_e_token(client, "endereco-inexistente")
    cliente = client.post(
        "/clientes/",
        json=payload_cliente(),
        headers=headers,
    ).json()

    base = f"/clientes/{cliente['idclientes']}/enderecos"
    id_inexistente = 999999

    buscar = client.get(
        f"{base}/{id_inexistente}",
        headers=headers,
    )
    assert buscar.status_code == 404
    assert buscar.json()["detail"] == "Endereço não encontrado."

    atualizar = client.patch(
        f"{base}/{id_inexistente}",
        json={"cidade": "Campinas"},
        headers=headers,
    )
    assert atualizar.status_code == 404
    assert atualizar.json()["detail"] == "Endereço não encontrado."

    excluir = client.delete(
        f"{base}/{id_inexistente}",
        headers=headers,
    )
    assert excluir.status_code == 404
    assert excluir.json()["detail"] == "Endereço não encontrado."
