
"""Testes dos endpoints de perfil e senha do usuário autenticado."""

SENHA_ATUAL = "SenhaSegura123!"
NOVA_SENHA = "OutraSenhaSegura456!"


def criar_usuario_e_headers(client, sufixo="perfil"):
    """Cria um usuário e retorna seus headers de autenticação."""
    email = f"{sufixo}@example.com"

    cadastro = client.post(
        "/usuarios/",
        json={
            "nome": f"Usuário {sufixo}",
            "email": email,
            "senha": SENHA_ATUAL,
        },
    )
    assert cadastro.status_code == 201, cadastro.text

    login = client.post(
        "/auth/login",
        json={
            "email": email,
            "senha": SENHA_ATUAL,
        },
    )
    assert login.status_code == 200, login.text

    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_obter_me_retorna_usuario_autenticado(client):
    """GET /usuarios/me retorna os dados do usuário autenticado."""
    headers = criar_usuario_e_headers(client)

    resposta = client.get("/usuarios/me", headers=headers)

    assert resposta.status_code == 200, resposta.text
    dados = resposta.json()

    assert dados["nome"] == "Usuário perfil"
    assert dados["email"] == "perfil@example.com"
    assert "idusuarios" in dados
    assert "ativo" in dados
    assert "data_cadastro" in dados
    assert "data_atualizacao" in dados
    assert "senha" not in dados
    assert "senha_hash" not in dados


def test_obter_me_sem_token_retorna_401(client):
    """GET /usuarios/me exige autenticação."""
    resposta = client.get("/usuarios/me")

    assert resposta.status_code == 401


def test_atualizar_me_altera_nome_e_email(client):
    """PATCH /usuarios/me atualiza nome e e-mail."""
    headers = criar_usuario_e_headers(client)

    resposta = client.patch(
        "/usuarios/me",
        headers=headers,
        json={
            "nome": "Nome Atualizado",
            "email": "atualizado@example.com",
        },
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["nome"] == "Nome Atualizado"
    assert resposta.json()["email"] == "atualizado@example.com"

    consulta = client.get("/usuarios/me", headers=headers)

    assert consulta.status_code == 200
    assert consulta.json()["nome"] == "Nome Atualizado"
    assert consulta.json()["email"] == "atualizado@example.com"


def test_atualizar_me_sem_token_retorna_401(client):
    """PATCH /usuarios/me exige autenticação."""
    resposta = client.patch(
        "/usuarios/me",
        json={"nome": "Novo Nome"},
    )

    assert resposta.status_code == 401


def test_atualizar_usuario_nao_permite_trocar_senha_sem_reautenticacao(client):
    headers = criar_usuario_e_headers(client)
    usuario = client.get("/usuarios/me", headers=headers).json()

    resposta = client.patch(
        f"/usuarios/{usuario['idusuarios']}",
        headers=headers,
        json={"senha": NOVA_SENHA},
    )

    assert resposta.status_code == 422

    login = client.post(
        "/auth/login",
        json={
            "email": "perfil@example.com",
            "senha": SENHA_ATUAL,
        },
    )
    assert login.status_code == 200


def test_atualizar_me_sem_campos_retorna_400(client):
    """A atualização exige ao menos um campo."""
    headers = criar_usuario_e_headers(client)

    resposta = client.patch(
        "/usuarios/me",
        headers=headers,
        json={},
    )

    assert resposta.status_code == 400


def test_atualizar_me_com_nome_nulo_retorna_422(client):
    """O nome não pode ser explicitamente nulo."""
    headers = criar_usuario_e_headers(client)

    resposta = client.patch(
        "/usuarios/me",
        headers=headers,
        json={"nome": None},
    )

    assert resposta.status_code == 422


def test_atualizar_me_com_email_nulo_retorna_422(client):
    """O e-mail não pode ser explicitamente nulo."""
    headers = criar_usuario_e_headers(client)

    resposta = client.patch(
        "/usuarios/me",
        headers=headers,
        json={"email": None},
    )

    assert resposta.status_code == 422


def test_atualizar_me_com_email_duplicado_retorna_409(client):
    """O e-mail de outro usuário não pode ser utilizado."""
    headers = criar_usuario_e_headers(client, "primeiro")
    criar_usuario_e_headers(client, "segundo")

    resposta = client.patch(
        "/usuarios/me",
        headers=headers,
        json={"email": "segundo@example.com"},
    )

    assert resposta.status_code == 409


def test_alterar_senha_com_senha_atual_correta(client):
    """PATCH /usuarios/me/senha altera a senha e retorna 204."""
    headers = criar_usuario_e_headers(client)

    resposta = client.patch(
        "/usuarios/me/senha",
        headers=headers,
        json={
            "senha_atual": SENHA_ATUAL,
            "nova_senha": NOVA_SENHA,
        },
    )

    assert resposta.status_code == 204
    assert resposta.content == b""

    login_antigo = client.post(
        "/auth/login",
        json={
            "email": "perfil@example.com",
            "senha": SENHA_ATUAL,
        },
    )
    assert login_antigo.status_code == 401

    login_novo = client.post(
        "/auth/login",
        json={
            "email": "perfil@example.com",
            "senha": NOVA_SENHA,
        },
    )
    assert login_novo.status_code == 200, login_novo.text


def test_alterar_senha_com_senha_atual_incorreta_retorna_400(client):
    """A senha atual precisa ser válida."""
    headers = criar_usuario_e_headers(client)

    resposta = client.patch(
        "/usuarios/me/senha",
        headers=headers,
        json={
            "senha_atual": "SenhaIncorreta123!",
            "nova_senha": NOVA_SENHA,
        },
    )

    assert resposta.status_code == 400


def test_alterar_senha_sem_token_retorna_401(client):
    """PATCH /usuarios/me/senha exige autenticação."""
    resposta = client.patch(
        "/usuarios/me/senha",
        json={
            "senha_atual": SENHA_ATUAL,
            "nova_senha": NOVA_SENHA,
        },
    )

    assert resposta.status_code == 401


def test_alterar_senha_com_nova_senha_igual_retorna_422(client):
    """A nova senha deve ser diferente da atual."""
    headers = criar_usuario_e_headers(client)

    resposta = client.patch(
        "/usuarios/me/senha",
        headers=headers,
        json={
            "senha_atual": SENHA_ATUAL,
            "nova_senha": SENHA_ATUAL,
        },
    )

    assert resposta.status_code == 422


def test_alterar_senha_com_nova_senha_curta_retorna_422(client):
    """A nova senha deve conter ao menos oito caracteres."""
    headers = criar_usuario_e_headers(client)

    resposta = client.patch(
        "/usuarios/me/senha",
        headers=headers,
        json={
            "senha_atual": SENHA_ATUAL,
            "nova_senha": "curta",
        },
    )

    assert resposta.status_code == 422
