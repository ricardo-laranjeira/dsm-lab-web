
"""Executa a análise estática do código com o Pylint."""

import sys

from pylint.lint import Run


def main() -> int:
    """Analisa o código da aplicação e retorna o resultado."""
    resultado = Run(
        ["api", "scripts"],
        exit=False,
    )

    return resultado.linter.msg_status


if __name__ == "__main__":
    sys.exit(main())
