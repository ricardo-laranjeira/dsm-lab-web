
import sys

from alembic import command
from alembic.config import Config


def main() -> None:
    config = Config("alembic.ini")

    mensagem = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "atualizar modelo do banco"
    )

    # Gera uma migration com base nas diferenças detectadas.
    command.revision(
        config,
        message=mensagem,
        autogenerate=True,
    )

    # Aplica as migrations pendentes.
    command.upgrade(config, "head")

    print("Migrations geradas e aplicadas com sucesso!")


if __name__ == "__main__":
    main()
