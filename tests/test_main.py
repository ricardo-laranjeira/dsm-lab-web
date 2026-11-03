def test_home(client):
    resposta = client.get("/")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "mensagem": "API de Orçamentos funcionando."
    }
