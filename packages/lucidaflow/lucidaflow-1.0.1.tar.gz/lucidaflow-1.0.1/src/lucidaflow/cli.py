# src/lucidaflow/cli.py

import sys
from .lucida_lexer import Lexer
from .lucida_parser import Parser
from .lucida_analyzer import SemanticAnalyzer
from .lucida_interpreter import Interpreter
from .lucida_errors import LucidaError
from .lucida_ast import ProgramNode

def run_code(source_code, analyzer, interpreter):
    lexer = Lexer(source_code)
    parser = Parser(lexer)
    ast = parser.parse()
    analyzer.visit(ast)
    result = interpreter.visit(ast)
    return result

def start_repl():
    print("Lucida-Flow REPL v1.0 (Instalado via pip)")
    print("Digite 'exit' ou 'sair' para terminar.")

    analyzer = SemanticAnalyzer()
    interpreter = Interpreter()
    analyzer.visit(ProgramNode([]))

    while True:
        try:
            line = input("lf> ")
            if line.strip().lower() in ('exit', 'sair'):
                break

            if not line.strip():
                continue

            result = run_code(line, analyzer, interpreter)

            if result is not None:
                print(result)
        except LucidaError as e:
            print(e)
        except Exception as e:
            print(f"Erro de sistema: {e}")

def main():
    # Por agora, a nossa ferramenta de linha de comando só inicia o REPL.
    start_repl()

if __name__ == '__main__':
    main()