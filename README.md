# API de Orçamentos

API REST para cadastro e gerenciamento de usuários, clientes, serviços, materiais, orçamentos e agendamentos. Foi desenvolvida com FastAPI, SQLAlchemy e SQLite.

## Requisitos

- Python 3.10 ou superior.
- PowerShell no Windows (os comandos abaixo usam esse terminal).

## Instalação e execução

1. Abra o PowerShell na pasta raiz do projeto:

   ```powershell
   cd "C:\Users\rc_la\Workspace\Pycharm\DSM\lab\api-orcamento"
   ```

   Se o projeto estiver em outro local, ajuste o caminho.

2. Crie e ative um ambiente virtual:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   Se a política do PowerShell impedir a ativação, consulte a política da sua máquina ou use o interpretador do ambiente virtual diretamente.

3. Instale as dependências listadas no projeto:

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente em `.env`, na raiz do projeto. Preserve as demais configurações que já existirem no arquivo e defina pelo menos uma chave secreta para os tokens:

   ```env
   JWT_SECRET_KEY=COLOQUE_AQUI_UMA_CHAVE_ALEATORIA
   DATABASE_URL=sqlite:///./orcamento.db
   ```

   Para gerar uma chave aleatória no PowerShell:

   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

   Copie o valor gerado para `JWT_SECRET_KEY`. Não compartilhe nem versione o arquivo `.env`. A aplicação usa SQLite por padrão e cria/usa `orcamento.db` na pasta atual.

5. Aplique as migrações do banco:

   ```powershell
   python -m alembic upgrade head
   ```

6. Inicie o servidor local:

   ```powershell
   python -m uvicorn api.main:app --reload
   ```

   A API ficará disponível em `http://127.0.0.1:8000`. Mantenha esse terminal aberto enquanto utilizar o serviço. Para interromper, pressione `Ctrl+C`.

## Documentação interativa

Com o servidor em execução, abra:

- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

Na Swagger UI, selecione uma operação para ver os campos obrigatórios, formatos, parâmetros e respostas. Use **Authorize** para informar o token Bearer antes de chamar operações protegidas.

## Primeiro uso: cadastrar, autenticar e chamar a API

Os exemplos abaixo usam PowerShell. Primeiro, cadastre um usuário (a senha deve ter pelo menos 8 caracteres):

```powershell
$baseUrl = "http://127.0.0.1:8000"

$cadastro = @{
    nome = "Ana"
    email = "ana@example.com"
    senha = "Senha-forte-123"
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
    -Uri "$baseUrl/usuarios/" `
    -ContentType "application/json" `
    -Body $cadastro
```

Obtenha um token com o e-mail e a senha cadastrados:

```powershell
$credenciais = @{
    email = "ana@example.com"
    senha = "Senha-forte-123"
} | ConvertTo-Json

$autenticacao = Invoke-RestMethod -Method Post `
    -Uri "$baseUrl/auth/login" `
    -ContentType "application/json" `
    -Body $credenciais

$token = $autenticacao.access_token
$headers = @{ Authorization = ('Bearer ' + $token) }
```

Nas operações protegidas, envie o cabeçalho `Authorization` com o esquema `Bearer` seguido do token. Por exemplo, para consultar o próprio perfil:

```powershell
Invoke-RestMethod -Method Get `
    -Uri "$baseUrl/usuarios/me" `
    -Headers $headers
```

O token expira após 30 minutos por padrão. Se receber `401 Unauthorized`, autentique-se novamente para obter outro.

## Endpoints disponíveis

Exceto pelo cadastro `POST /usuarios/` e pelo login `POST /auth/login`, as operações abaixo exigem autenticação Bearer. Os dados e parâmetros completos estão descritos em `/docs`.

| Recurso | Operações |
|---|---|
| Geral | `GET /` — verificar se a API está funcionando |
| Autenticação | `POST /auth/login` |
| Usuários | `POST /usuarios/`, `GET /usuarios/me`, `PATCH /usuarios/me`, `PATCH /usuarios/me/senha`, `GET /usuarios/{idusuarios}`, `PATCH /usuarios/{idusuarios}`, `DELETE /usuarios/{idusuarios}` |
| Clientes | `POST /clientes/`, `GET /clientes/`, `GET /clientes/{idclientes}`, `PATCH /clientes/{idclientes}`, `DELETE /clientes/{idclientes}` |
| Endereços | `POST /clientes/{idclientes}/enderecos/`, `GET /clientes/{idclientes}/enderecos/`, `GET /clientes/{idclientes}/enderecos/{idenderecos}`, `PATCH /clientes/{idclientes}/enderecos/{idenderecos}`, `DELETE /clientes/{idclientes}/enderecos/{idenderecos}` |
| Categorias | `POST /categorias/`, `GET /categorias/`, `GET /categorias/{idcategorias}`, `PATCH /categorias/{idcategorias}`, `DELETE /categorias/{idcategorias}` |
| Materiais | `POST /materiais/`, `GET /materiais/`, `GET /materiais/{idmateriais}`, `PATCH /materiais/{idmateriais}`, `DELETE /materiais/{idmateriais}` |
| Serviços | `POST /servicos/`, `GET /servicos/`, `GET /servicos/{idservicos}`, `PATCH /servicos/{idservicos}`, `DELETE /servicos/{idservicos}` |
| Orçamentos | `POST /orcamentos/`, `GET /orcamentos/`, `GET /orcamentos/{idorcamentos}`, `PATCH /orcamentos/{idorcamentos}`, `DELETE /orcamentos/{idorcamentos}` |
| Materiais do orçamento | `POST /orcamentos/{idorcamentos}/materiais/`, `GET /orcamentos/{idorcamentos}/materiais/`, `PATCH /orcamentos/{idorcamentos}/materiais/{materiais_id}`, `DELETE /orcamentos/{idorcamentos}/materiais/{materiais_id}` |
| Serviços do orçamento | `POST /orcamentos/{idorcamentos}/servicos/`, `GET /orcamentos/{idorcamentos}/servicos/`, `PATCH /orcamentos/{idorcamentos}/servicos/{servicos_id}`, `DELETE /orcamentos/{idorcamentos}/servicos/{servicos_id}` |
| Agendamentos | `POST /agendamentos/`, `GET /agendamentos/`, `GET /agendamentos/{idagendamentos}`, `PATCH /agendamentos/{idagendamentos}`, `DELETE /agendamentos/{idagendamentos}` |

`GET /usuarios/` existe, mas retorna `403 Forbidden`: a listagem geral de usuários está desabilitada por falta de autorização administrativa.

As listagens paginadas aceitam `offset` (padrão `0`) e `limit` (padrão `100`, máximo `100`). Envie ambos como parâmetros de consulta, por exemplo: `/clientes/?offset=0&limit=20`.

## Respostas e erros comuns

- `200 OK`: consulta ou atualização concluída.
- `201 Created`: recurso criado.
- `204 No Content`: exclusão ou operação sem corpo de resposta.
- `401 Unauthorized`: token ausente, inválido ou expirado; ou credenciais de login inválidas.
- `403 Forbidden`: operação não permitida para o usuário.
- `404 Not Found`: recurso inexistente ou que não pertence ao usuário autenticado.
- `409 Conflict`: conflito, como e-mail já cadastrado ou agendamento duplicado.
- `422 Unprocessable Entity`: dados enviados não atendem à validação do schema.

As respostas de erro incluem um campo `detail` com informações sobre o problema.

## Banco de dados e migrações

O banco padrão é o arquivo `orcamento.db`. Para apontar para outro banco, altere `DATABASE_URL` em `.env` usando uma URL compatível com SQLAlchemy.

Após baixar atualizações que incluam migrações, aplique-as com:

```powershell
python -m alembic upgrade head
```

Para consultar a revisão atual:

```powershell
python -m alembic current
```
