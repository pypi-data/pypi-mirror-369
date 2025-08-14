import argparse
from pathlib import Path
from rpa_arc.estrutura import criar_estrutura

def main():
    parser = argparse.ArgumentParser(
        description="🚀 Cria a estrutura base de um projeto RPA em Python."
    )
    parser.add_argument(
        "nome_projeto",
        nargs="?",            # torna opcional
        default=None,
        type=str,
        help="(opcional) Nome da pasta onde o projeto será criado"
    )
    args = parser.parse_args()

    # se veio nome, cria subpasta; se não, usa o cwd
    if args.nome_projeto:
        caminho_projeto = Path.cwd() / args.nome_projeto
        if caminho_projeto.exists():
            print(f"⚠️  A pasta '{args.nome_projeto}' já existe. Abortando para não sobrescrever nada.")
            return
        caminho_projeto.mkdir(parents=True)
    else:
        caminho_projeto = Path.cwd()

    criar_estrutura(caminho_projeto)

    if args.nome_projeto:
        print(f"\n🎉 Projeto '{args.nome_projeto}' criado com sucesso!")
    else:
        print("\n🎉 Estrutura criada na raiz do projeto com sucesso!")
    print(f"📂 Local: {caminho_projeto.resolve()}")

if __name__ == "__main__":
    main()