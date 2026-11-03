
from api.core.security import verificar_senha
from api.repositories import usuario_repository
from api.schemas.usuario import UsuarioCreate, UsuarioUpdate


def criar_dados_usuario(
    nome="Maria Silva",
    email="maria.repository@example.com",
    senha="SenhaSegura123!",
):
    return UsuarioCreate(
        nome=nome,
        email=email,
        senha=senha,
    )


def test_buscar_usuario_por_id(db_session):
    dados = criar_dados_usuario()
    usuario = usuario_repository.criar(db_session, dados)

    encontrado = usuario_repository.buscar_por_id(
        db_session,
        usuario.idusuarios,
    )

    assert encontrado is not None
    assert encontrado.email == str(dados.email)


def test_buscar_usuario_por_id_inexistente(db_session):
    encontrado = usuario_repository.buscar_por_id(db_session, 99999)

    assert encontrado is None


def test_buscar_usuario_por_email(db_session):
    dados = criar_dados_usuario()
    usuario_repository.criar(db_session, dados)

    encontrado = usuario_repository.buscar_por_email(
        db_session,
        str(dados.email),
    )

    assert encontrado is not None
    assert encontrado.nome == dados.nome


def test_buscar_email_inexistente(db_session):
    encontrado = usuario_repository.buscar_por_email(
        db_session,
        "nao.existe@example.com",
    )

    assert encontrado is None


def test_listar_usuarios(db_session):
    usuario_repository.criar(
        db_session,
        criar_dados_usuario(
            nome="Maria",
            email="maria.lista@example.com",
        ),
    )
    usuario_repository.criar(
        db_session,
        criar_dados_usuario(
            nome="João",
            email="joao.lista@example.com",
        ),
    )

    usuarios = usuario_repository.listar(db_session)

    assert len(usuarios) == 2


def test_listar_usuarios_com_paginacao(db_session):
    for numero in range(3):
        usuario_repository.criar(
            db_session,
            criar_dados_usuario(
                nome=f"Usuario {numero}",
                email=f"usuario{numero}.lista@example.com",
            ),
        )

    usuarios = usuario_repository.listar(
        db_session,
        offset=1,
        limit=1,
    )

    assert len(usuarios) == 1


def test_criar_usuario_armazena_senha_com_hash(db_session):
    dados = criar_dados_usuario()
    usuario = usuario_repository.criar(db_session, dados)

    assert usuario.senha != dados.senha
    assert verificar_senha(dados.senha, usuario.senha)


def test_atualizar_nome_usuario(db_session):
    usuario = usuario_repository.criar(
        db_session,
        criar_dados_usuario(),
    )

    atualizado = usuario_repository.atualizar(
        db_session,
        usuario,
        UsuarioUpdate(nome="Maria Souza"),
    )

    assert atualizado.nome == "Maria Souza"


def test_excluir_usuario(db_session):
    usuario = usuario_repository.criar(
        db_session,
        criar_dados_usuario(),
    )
    idusuario = usuario.idusuarios

    usuario_repository.excluir(db_session, usuario)

    encontrado = usuario_repository.buscar_por_id(
        db_session,
        idusuario,
    )

    assert encontrado is None
