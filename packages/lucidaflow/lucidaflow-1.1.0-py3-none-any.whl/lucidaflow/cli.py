# src/lucidaflow/cli.py

import sys
from lucidaflow.lucida_lexer import Lexer
from lucidaflow.lucida_parser import Parser
from lucidaflow.lucida_analyzer import SemanticAnalyzer
from lucidaflow.lucida_interpreter import Interpreter
from lucidaflow.lucida_errors import LucidaError
from lucidaflow.lucida_ast import ProgramNode

# --- Funções de Execução ---

def run_code(source_code):
    """Função que executa um trecho de código da Lucida-Flow."""
    # Cada execução tem seu próprio ambiente limpo
    analyzer = SemanticAnalyzer()
    interpreter = Interpreter()
    
    lexer = Lexer(source_code)
    parser = Parser(lexer)
    ast = parser.parse()
    
    analyzer.visit(ast)
    result = interpreter.visit(ast)
    return result

def run_file(filename):
    """Lê e executa um ficheiro .lf."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source_code = f.read()
        run_code(source_code)
    except FileNotFoundError:
        print(f"Erro: O ficheiro '{filename}' não foi encontrado.")
    except LucidaError as e:
        print("--- OCORREU UM ERRO NA LUCIDA-FLOW ---")
        print(e)
    except Exception as e:
        print("--- OCORREU UM ERRO INESPERADO NO SISTEMA ---")
        print(e)

def start_repl():
    """Inicia o modo interativo (REPL)."""
    print("Lucida-Flow REPL v1.0 (Instalado via pip)")
    print("Digite 'exit' ou 'sair' para terminar.")
    
    analyzer = SemanticAnalyzer()
    interpreter = Interpreter()
    analyzer.visit(ProgramNode([]))
    
    while True:
        try:
            line = input("lf> ")
            if line.strip().lower() in ('exit', 'sair'): break
            if not line.strip(): continue
            
            # Reutiliza o mesmo analyzer e interpreter para manter o estado no REPL
            lexer = Lexer(line)
            parser = Parser(lexer)
            ast = parser.parse()
            analyzer.visit(ast)
            result = interpreter.visit(ast)
            
            if result is not None:
                print(result)
        except LucidaError as e:
            print(e)
        except Exception as e:
            print(f"Erro de sistema: {e}")

# --- Ponto de Entrada Principal ---

def main():
    """Verifica os argumentos e decide se executa um ficheiro ou inicia o REPL."""
    # sys.argv é a lista de argumentos da linha de comando.
    # sys.argv[0] é o nome do script, o resto são os argumentos.
    if len(sys.argv) > 1:
        # Se um argumento foi passado, assumimos que é um nome de ficheiro
        script_file = sys.argv[1]
        run_file(script_file)
    else:
        # Se nenhum argumento foi passado, inicia o REPL
        start_repl()

if __name__ == '__main__':
    main()