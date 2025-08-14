import os
from pathlib import Path
from .conteudos import *


# Estrutura base que será criada
ESTRUTURA_PROJETO = {
    "src": {
        "app": ["app.py"],
        "core": ["logger.py", "driver.py"],
        "integracoes": [],
        "utils": {
            "helpers": []
        },
        "api": ["Api.py"]
    },
    "config": [],
    "dados": [],
    "logs": [],
    "tests": [],
    "root_files": [
        "requirements.txt",
        ".env",
        "Dockerfile",
        "README.md",
        "main.py",
        ".gitignore",
        ".dockerignore"
    ]
}

def criar_estrutura(base_path: Path):
    print(f"🛠️  Criando estrutura em: {base_path.resolve()}")

    # Criar pastas de primeiro nível
    for pasta in ["config", "dados", "logs", "tests"]:
        caminho = base_path / pasta
        caminho.mkdir(parents=True, exist_ok=True)
        print(f"📁 Criado: {caminho}")

    # Criar arquivos na raiz
    for arquivo in ESTRUTURA_PROJETO["root_files"]:
        caminho = base_path / arquivo
        if arquivo == "requirements.txt":
            caminho.write_text(REQUIREMENTS_CONTENT.strip() + "\n", encoding="utf-8")
        if arquivo == "Dockerfile":
            caminho.write_text(DOCKERFILE_CONTENT.strip() + "\n", encoding="utf-8")
        elif arquivo == ".gitignore":
            caminho.write_text(GITIGNORE_CONTENT.strip(), encoding="utf-8")
        elif arquivo == ".dockerignore":
            caminho.write_text(DOCKERIGNORE_CONTENT.strip(), encoding="utf-8")
        elif arquivo == ".env":
            caminho.write_text(ENV_CONTENT.strip(), encoding="utf-8")
        else:
            caminho.touch(exist_ok=True)
        print(f"📄 Criado: {caminho}")

    # Criar estrutura dentro de src/
    src_path = base_path / "src"
    src_path.mkdir(exist_ok=True)

    for pasta, conteudo in ESTRUTURA_PROJETO["src"].items():
        caminho_pasta = src_path / pasta

        if pasta == "core":
            caminho_pasta.mkdir(parents=True, exist_ok=True)
            for arquivo in conteudo:
                caminho_arquivo = caminho_pasta / arquivo
                if arquivo == "logger.py":
                    caminho_arquivo.write_text(LOGGER_CONTENT.strip(), encoding="utf-8")
                elif arquivo == "driver.py":
                    caminho_arquivo.write_text(DRIVER_CONTENT.strip(), encoding="utf-8")
                else:
                    caminho_arquivo.touch()
                print(f"📄 Criado: {caminho_arquivo}")

        if pasta == "api":
            caminho_pasta.mkdir(parents=True, exist_ok=True)
            for arquivo in conteudo:
                caminho_arquivo = caminho_pasta / arquivo
                if arquivo == "Api.py":
                    caminho_arquivo.write_text(API_CONTENT.strip(), encoding="utf-8")
                else:
                    caminho_arquivo.touch()
                print(f"📄 Criado: {caminho_arquivo}")

        elif isinstance(conteudo, list):
            caminho_pasta.mkdir(parents=True, exist_ok=True)
            for arquivo in conteudo:
                (caminho_pasta / arquivo).touch()
                print(f"📄 Criado: {caminho_pasta / arquivo}")

        # elif isinstance(conteudo, dict):  # como utils/helpers
        #     for subpasta, arquivos in conteudo.items():
        #         caminho_sub = caminho_pasta / subpasta
        #         caminho_sub.mkdir(parents=True, exist_ok=True)
        #         for arquivo in arquivos:
        #             caminho_arquivo = caminho_sub / arquivo
        #             if arquivo == "_enviar_s3.py":
        #                 caminho_arquivo.write_text(ENVIAR_S3_CONTENT.strip(), encoding="utf-8")
        #             elif arquivo == "_get_token.py":
        #                 caminho_arquivo.write_text(GET_TOKEN_CONTENT.strip(), encoding="utf-8")
        #             else:
        #                 caminho_arquivo.touch()
        #             print(f"📄 Criado: {caminho_arquivo}")

        else:
            caminho_pasta.mkdir(parents=True, exist_ok=True)

    print("✅ Estrutura criada com sucesso!\n")
