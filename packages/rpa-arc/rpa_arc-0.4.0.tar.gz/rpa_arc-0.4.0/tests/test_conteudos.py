import pytest
from rpa_arc.conteudos import (
    REQUIREMENTS_CONTENT,
    API_CONTENT,
    LOGGER_CONTENT,
    DRIVER_CONTENT,
    DOCKERFILE_CONTENT,
    GITIGNORE_CONTENT,
    DOCKERIGNORE_CONTENT
)


class TestConteudos:
    """Testes para o módulo conteudos da biblioteca rpa-arc."""

    def test_requirements_content_estrutura(self):
        """Testa se o conteúdo do requirements.txt tem a estrutura correta."""
        # Assert
        assert isinstance(REQUIREMENTS_CONTENT, str)
        assert len(REQUIREMENTS_CONTENT) > 0
        
        # Verifica se contém as dependências principais
        dependencias_esperadas = [
            "requests", "python-dotenv", "selenium", 
            "webdriver-manager", "fastapi", "uvicorn"
        ]
        for dependencia in dependencias_esperadas:
            assert dependencia in REQUIREMENTS_CONTENT, f"Dependência {dependencia} não encontrada"

    def test_api_content_estrutura(self):
        """Testa se o conteúdo do Api.py tem a estrutura correta."""
        # Assert
        assert isinstance(API_CONTENT, str)
        assert len(API_CONTENT) > 0
        
        # Verifica se contém elementos principais da classe Api
        elementos_esperados = [
            "class Api:", "def __init__", "def GetToken", 
            "def CheckToken", "def EnviarArquivoS3", "requests"
        ]
        for elemento in elementos_esperados:
            assert elemento in API_CONTENT, f"Elemento {elemento} não encontrado"

    def test_logger_content_estrutura(self):
        """Testa se o conteúdo do logger.py tem a estrutura correta."""
        # Assert
        assert isinstance(LOGGER_CONTENT, str)
        assert len(LOGGER_CONTENT) > 0
        
        # Verifica se contém elementos principais do logger
        elementos_esperados = [
            "class Logger:", "class DailyFileHandler", 
            "logging", "TimedRotatingFileHandler"
        ]
        for elemento in elementos_esperados:
            assert elemento in LOGGER_CONTENT, f"Elemento {elemento} não encontrado"

    def test_driver_content_estrutura(self):
        """Testa se o conteúdo do driver.py tem a estrutura correta."""
        # Assert
        assert isinstance(DRIVER_CONTENT, str)
        assert len(DRIVER_CONTENT) > 0
        
        # Verifica se contém elementos principais do driver
        elementos_esperados = [
            "class GerenciadorNavegador:", "selenium", "webdriver",
            "ChromeDriverManager", "Options"
        ]
        for elemento in elementos_esperados:
            assert elemento in DRIVER_CONTENT, f"Elemento {elemento} não encontrado"

    def test_dockerfile_content_estrutura(self):
        """Testa se o conteúdo do Dockerfile tem a estrutura correta."""
        # Assert
        assert isinstance(DOCKERFILE_CONTENT, str)
        assert len(DOCKERFILE_CONTENT) > 0
        
        # Verifica se contém elementos principais do Dockerfile
        elementos_esperados = [
            "FROM python:3.12-slim", "WORKDIR /app", 
            "COPY requirements.txt", "RUN pip install"
        ]
        for elemento in elementos_esperados:
            assert elemento in DOCKERFILE_CONTENT, f"Elemento {elemento} não encontrado"

    def test_gitignore_content_estrutura(self):
        """Testa se o conteúdo do .gitignore tem a estrutura correta."""
        # Assert
        assert isinstance(GITIGNORE_CONTENT, str)
        assert len(GITIGNORE_CONTENT) > 0
        
        # Verifica se contém elementos principais do .gitignore
        elementos_esperados = [
            "__pycache__/", "*.py[cod]", ".env", "venv/",
            "*.egg-info/", ".pytest_cache/"
        ]
        for elemento in elementos_esperados:
            assert elemento in GITIGNORE_CONTENT, f"Elemento {elemento} não encontrado"

    def test_dockerignore_content_estrutura(self):
        """Testa se o conteúdo do .dockerignore tem a estrutura correta."""
        # Assert
        assert isinstance(DOCKERIGNORE_CONTENT, str)
        assert len(DOCKERIGNORE_CONTENT) > 0
        
        # Verifica se contém elementos principais do .dockerignore
        elementos_esperados = [
            "venv/", "__pycache__/", "*.log", "tests/",
            ".git/", ".idea/", "*.DS_Store"
        ]
        for elemento in elementos_esperados:
            assert elemento in DOCKERIGNORE_CONTENT, f"Elemento {elemento} não encontrado"

    def test_api_content_imports(self):
        """Testa se o Api.py tem os imports necessários."""
        imports_esperados = [
            "import base64", "import os", "import requests",
            "from dotenv import load_dotenv", "from typing import Optional"
        ]
        for import_statement in imports_esperados:
            assert import_statement in API_CONTENT, f"Import {import_statement} não encontrado"

    def test_logger_content_imports(self):
        """Testa se o logger.py tem os imports necessários."""
        imports_esperados = [
            "import logging", "import os", "from datetime import datetime",
            "import time", "from logging.handlers import TimedRotatingFileHandler"
        ]
        for import_statement in imports_esperados:
            assert import_statement in LOGGER_CONTENT, f"Import {import_statement} não encontrado"

    def test_driver_content_imports(self):
        """Testa se o driver.py tem os imports necessários."""
        imports_esperados = [
            "import os", "import platform", "import subprocess",
            "from selenium import webdriver", "from selenium.webdriver.chrome.service import Service",
            "from selenium.webdriver.chrome.options import Options", "from webdriver_manager.chrome import ChromeDriverManager"
        ]
        for import_statement in imports_esperados:
            assert import_statement in DRIVER_CONTENT, f"Import {import_statement} não encontrado"

    def test_api_content_methods(self):
        """Testa se a classe Api tem os métodos principais."""
        metodos_esperados = [
            "def __init__", "def GetToken", "def CheckToken", 
            "def ValidateUser", "def InserirLogApi", "def EnviarArquivoS3"
        ]
        for metodo in metodos_esperados:
            assert metodo in API_CONTENT, f"Método {metodo} não encontrado"

    def test_logger_content_classes(self):
        """Testa se o logger.py tem as classes principais."""
        classes_esperadas = [
            "class DailyFileHandler", "class Logger"
        ]
        for classe in classes_esperadas:
            assert classe in LOGGER_CONTENT, f"Classe {classe} não encontrada"

    def test_driver_content_classes(self):
        """Testa se o driver.py tem as classes principais."""
        classes_esperadas = [
            "class GerenciadorNavegador"
        ]
        for classe in classes_esperadas:
            assert classe in DRIVER_CONTENT, f"Classe {classe} não encontrada"

    def test_requirements_content_formato(self):
        """Testa se o requirements.txt tem formato válido."""
        # Verifica se cada linha é uma dependência válida
        linhas = REQUIREMENTS_CONTENT.strip().split('\n')
        for linha in linhas:
            if linha.strip():  # Ignora linhas vazias
                # Verifica se é uma dependência válida (sem espaços extras, etc.)
                assert ' ' not in linha.strip(), f"Linha inválida no requirements: {linha}"

    def test_dockerfile_content_comandos(self):
        """Testa se o Dockerfile tem os comandos principais."""
        comandos_esperados = [
            "FROM", "WORKDIR", "COPY", "RUN", "CMD"
        ]
        for comando in comandos_esperados:
            assert comando in DOCKERFILE_CONTENT, f"Comando {comando} não encontrado"

    def test_gitignore_content_padroes(self):
        """Testa se o .gitignore tem padrões comuns de Python."""
        padroes_esperados = [
            "__pycache__/", "*.py[cod]", "*.so", "build/",
            "dist/", "*.egg-info/", ".env", "venv/"
        ]
        for padrao in padroes_esperados:
            assert padrao in GITIGNORE_CONTENT, f"Padrão {padrao} não encontrado"

    def test_conteudos_encoding(self):
        """Testa se todos os conteúdos são strings válidas."""
        conteudos = [
            REQUIREMENTS_CONTENT, API_CONTENT, LOGGER_CONTENT,
            DRIVER_CONTENT, DOCKERFILE_CONTENT, GITIGNORE_CONTENT,
            DOCKERIGNORE_CONTENT
        ]
        
        for i, conteudo in enumerate(conteudos):
            assert isinstance(conteudo, str), f"Conteúdo {i} não é string"
            assert len(conteudo) > 0, f"Conteúdo {i} está vazio"
            # Testa se pode ser codificado em UTF-8
            try:
                conteudo.encode('utf-8')
            except UnicodeEncodeError:
                pytest.fail(f"Conteúdo {i} não pode ser codificado em UTF-8")

    def test_api_content_docstring(self):
        """Testa se a classe Api tem docstring."""
        assert '"""' in API_CONTENT, "Classe Api deve ter docstring"
        assert "Camada fininha sobre *requests*" in API_CONTENT, "Docstring da Api não encontrada"

    def test_logger_content_configuracao(self):
        """Testa se o logger tem configuração de formatação."""
        assert "logging.Formatter" in LOGGER_CONTENT, "Logger deve ter formatação configurada"
        assert "%(asctime)s" in LOGGER_CONTENT, "Logger deve ter timestamp"

    def test_driver_content_configuracao_chrome(self):
        """Testa se o driver tem configuração específica do Chrome."""
        assert "ChromeDriverManager" in DRIVER_CONTENT, "Driver deve usar ChromeDriverManager"
        assert "Options()" in DRIVER_CONTENT, "Driver deve configurar opções do Chrome" 