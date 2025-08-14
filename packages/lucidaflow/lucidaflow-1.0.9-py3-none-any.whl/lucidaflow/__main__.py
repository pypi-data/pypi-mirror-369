# src/lucidaflow/__main__.py
import sys
from .cli import run_file, start_repl

def main():
    """
    Verifica os argumentos da linha de comando e decide se executa
    um ficheiro ou inicia o REPL.
    """
    # sys.argv é a lista de argumentos da linha de comando.
    # sys.argv[0] é o nome do módulo, o resto são os argumentos.
    if len(sys.argv) > 1:
        # Se um argumento foi passado, assumimos que é um nome de ficheiro
        script_file = sys.argv[1]
        run_file(script_file)
    else:
        # Se nenhum argumento foi passado, inicia o REPL
        start_repl()

if __name__ == "__main__":
    main()