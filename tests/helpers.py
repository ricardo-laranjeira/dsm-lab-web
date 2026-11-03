SENHA = "SenhaSegura123!"


def criar_usuario_e_headers(client, sufixo: str) -> dict[str, str]:
    email = f"{sufixo}@example.com"
    cadastro = client.post(
        "/usuarios/",
        json={"nome": f"Usuário {sufixo}", "email": email, "senha": SENHA},
    )
    assert cadastro.status_code == 201, cadastro.text

    login = client.post(
        "/auth/login",
        json={"email": email, "senha": SENHA},
    )
    if login.status_code == 422:
        login = client.post(
            "/auth/login",
            data={"username": email, "password": SENHA},
        )
    assert login.status_code == 200, login.text

    token = login.json().get("access_token")
    assert token, login.json()
    return {"Authorization": f"Bearer {token}"}
