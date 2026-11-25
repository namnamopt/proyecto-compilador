import sys
from pathlib import Path

from lexer import Lexer
from parser import Parser, evaluate, format_number
from errors import MiniCalcError


DEMO = """x = 10;
y = 5;
resultado = (x + y) * 2;
promedio = resultado / 3;
"""


def run(source):
    print("\n========== MINI-CALC ==========")

    # 1. Análisis léxico.
    tokens = Lexer(source).tokenize()
    print("\n--- ANÁLISIS LÉXICO: TOKENS ---")
    for token in tokens:
        print(token)

    # 2. Análisis sintáctico.
    statements = Parser(tokens).parse()
    print("\n--- ANÁLISIS SINTÁCTICO ---")
    print(f"Correcto: {len(statements)} instrucción(es) cumplen la gramática.")

    # 3. Evaluación.
    variables = {}
    print("\n--- EJECUCIÓN ---")
    for statement in statements:
        value = evaluate(statement.expression, variables)
        variables[statement.name] = value
        print(f"{statement.name} = {format_number(value)}")

    print("\nAnálisis finalizado correctamente.")


def main():
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        try:
            source = path.read_text(encoding="utf-8")
        except OSError as error:
            print(f"No se pudo leer el archivo: {error}")
            raise SystemExit(1)
    else:
        print("No se indicó un archivo. Se ejecutará el ejemplo incluido.")
        source = DEMO

    try:
        run(source)
    except MiniCalcError as error:
        print(f"\n[ERROR] {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
