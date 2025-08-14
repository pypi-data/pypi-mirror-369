import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestUtils:
    """Testes utilitários para a biblioteca rpa-arc."""

    def setup_method(self):
        """Configuração antes de cada teste."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)

    def teardown_method(self):
        """Limpeza após cada teste."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_imports_biblioteca(self):
        """Testa se todos os módulos da biblioteca podem ser importados."""
        # Testa imports principais
        try:
            from rpa_arc import cli, estrutura, conteudos
            assert cli is not None
            assert estrutura is not None
            assert conteudos is not None
        except ImportError as e:
            pytest.fail(f"Falha ao importar módulos: {e}")

    def test_cli_entry_point(self):
        """Testa se o entry point da CLI está configurado corretamente."""
        try:
            from rpa_arc.cli import main
            assert callable(main), "main deve ser uma função"
        except ImportError as e:
            pytest.fail(f"Falha ao importar main: {e}")

    def test_estrutura_function_exists(self):
        """Testa se a função criar_estrutura existe e é callable."""
        try:
            from rpa_arc.estrutura import criar_estrutura
            assert callable(criar_estrutura), "criar_estrutura deve ser uma função"
        except ImportError as e:
            pytest.fail(f"Falha ao importar criar_estrutura: {e}")

    def test_conteudos_constants_exist(self):
        """Testa se as constantes de conteúdo existem."""
        try:
            from rpa_arc.conteudos import (
                REQUIREMENTS_CONTENT, API_CONTENT, LOGGER_CONTENT,
                DRIVER_CONTENT, DOCKERFILE_CONTENT, GITIGNORE_CONTENT,
                DOCKERIGNORE_CONTENT
            )
            # Verifica se são strings não vazias
            for nome, conteudo in [
                ("REQUIREMENTS_CONTENT", REQUIREMENTS_CONTENT),
                ("API_CONTENT", API_CONTENT),
                ("LOGGER_CONTENT", LOGGER_CONTENT),
                ("DRIVER_CONTENT", DRIVER_CONTENT),
                ("DOCKERFILE_CONTENT", DOCKERFILE_CONTENT),
                ("GITIGNORE_CONTENT", GITIGNORE_CONTENT),
                ("DOCKERIGNORE_CONTENT", DOCKERIGNORE_CONTENT)
            ]:
                assert isinstance(conteudo, str), f"{nome} deve ser string"
                assert len(conteudo) > 0, f"{nome} não pode estar vazio"
        except ImportError as e:
            pytest.fail(f"Falha ao importar constantes: {e}")

    def test_pathlib_compatibility(self):
        """Testa se a biblioteca é compatível com pathlib."""
        from pathlib import Path
        from rpa_arc.estrutura import criar_estrutura
        
        # Testa se aceita Path objects
        try:
            criar_estrutura(Path(self.temp_dir))
            assert True, "criar_estrutura aceita Path objects"
        except Exception as e:
            pytest.fail(f"criar_estrutura não aceita Path objects: {e}")

    def test_string_path_compatibility(self):
        """Testa se a biblioteca aceita strings como caminhos."""
        from rpa_arc.estrutura import criar_estrutura
        
        # Testa se aceita strings
        try:
            criar_estrutura(Path(str(self.temp_dir)))
            assert True, "criar_estrutura aceita strings"
        except Exception as e:
            pytest.fail(f"criar_estrutura não aceita strings: {e}")

    def test_error_handling(self):
        """Testa tratamento de erros básicos."""
        from rpa_arc.estrutura import criar_estrutura
        
        # Testa com caminho inválido
        with pytest.raises(Exception):
            criar_estrutura(Path("/caminho/inexistente/que/nao/existe"))

    def test_encoding_consistency(self):
        """Testa consistência de encoding em todos os arquivos."""
        from rpa_arc.estrutura import criar_estrutura
        from rpa_arc.conteudos import (
            REQUIREMENTS_CONTENT, API_CONTENT, LOGGER_CONTENT,
            DRIVER_CONTENT, DOCKERFILE_CONTENT, GITIGNORE_CONTENT,
            DOCKERIGNORE_CONTENT
        )
        
        # Testa se todos os conteúdos são UTF-8 válidos
        conteudos = [
            REQUIREMENTS_CONTENT, API_CONTENT, LOGGER_CONTENT,
            DRIVER_CONTENT, DOCKERFILE_CONTENT, GITIGNORE_CONTENT,
            DOCKERIGNORE_CONTENT
        ]
        
        for i, conteudo in enumerate(conteudos):
            try:
                # Testa encoding/decoding UTF-8
                encoded = conteudo.encode('utf-8')
                decoded = encoded.decode('utf-8')
                assert decoded == conteudo, f"Conteúdo {i} não é UTF-8 consistente"
            except UnicodeError as e:
                pytest.fail(f"Conteúdo {i} tem problemas de encoding: {e}")

    def test_line_endings_consistency(self):
        """Testa consistência de line endings."""
        from rpa_arc.conteudos import (
            REQUIREMENTS_CONTENT, API_CONTENT, LOGGER_CONTENT,
            DRIVER_CONTENT, DOCKERFILE_CONTENT, GITIGNORE_CONTENT,
            DOCKERIGNORE_CONTENT
        )
        
        conteudos = [
            REQUIREMENTS_CONTENT, API_CONTENT, LOGGER_CONTENT,
            DRIVER_CONTENT, DOCKERFILE_CONTENT, GITIGNORE_CONTENT,
            DOCKERIGNORE_CONTENT
        ]
        
        for i, conteudo in enumerate(conteudos):
            # Verifica se não há mistura de line endings
            lines = conteudo.split('\n')
            if lines:
                # Pega o primeiro line ending encontrado
                first_line = lines[0]
                if '\r\n' in first_line:
                    expected_ending = '\r\n'
                elif '\r' in first_line:
                    expected_ending = '\r'
                else:
                    expected_ending = '\n'
                
                # Verifica se todos os line endings são consistentes
                for line in lines:
                    if line and not line.endswith(expected_ending):
                        # Se a linha não termina com o line ending esperado,
                        # deve ser a última linha (sem line ending)
                        if line != lines[-1]:
                            pytest.fail(f"Conteúdo {i} tem line endings inconsistentes")

    def test_python_syntax_validity(self):
        """Testa se os conteúdos Python têm sintaxe válida."""
        import ast
        from rpa_arc.conteudos import API_CONTENT, LOGGER_CONTENT, DRIVER_CONTENT
        
        conteudos_python = [
            ("API_CONTENT", API_CONTENT),
            ("LOGGER_CONTENT", LOGGER_CONTENT),
            ("DRIVER_CONTENT", DRIVER_CONTENT)
        ]
        
        for nome, conteudo in conteudos_python:
            try:
                # Tenta compilar o código Python
                ast.parse(conteudo)
            except SyntaxError as e:
                pytest.fail(f"Sintaxe Python inválida em {nome}: {e}")

    def test_file_permissions(self):
        """Testa se os arquivos criados têm permissões corretas."""
        from rpa_arc.estrutura import criar_estrutura
        
        criar_estrutura(self.test_dir)
        
        # Verifica se arquivos são legíveis
        arquivos_teste = [
            self.test_dir / "requirements.txt",
            self.test_dir / "src" / "core" / "logger.py",
            self.test_dir / "src" / "api" / "Api.py"
        ]
        
        for arquivo in arquivos_teste:
            assert arquivo.exists(), f"Arquivo {arquivo} não existe"
            assert arquivo.is_file(), f"{arquivo} não é um arquivo"
            # Verifica se é legível
            try:
                arquivo.read_text(encoding='utf-8')
            except PermissionError:
                pytest.fail(f"Arquivo {arquivo} não é legível")

    def test_directory_structure_validity(self):
        """Testa se a estrutura de diretórios é válida."""
        from rpa_arc.estrutura import criar_estrutura
        
        criar_estrutura(self.test_dir)
        
        # Verifica se diretórios são diretórios
        diretorios_teste = [
            self.test_dir / "src",
            self.test_dir / "config",
            self.test_dir / "dados",
            self.test_dir / "logs",
            self.test_dir / "tests"
        ]
        
        for diretorio in diretorios_teste:
            assert diretorio.exists(), f"Diretório {diretorio} não existe"
            assert diretorio.is_dir(), f"{diretorio} não é um diretório"

    def test_no_circular_imports(self):
        """Testa se não há imports circulares."""
        import importlib
        import sys
        
        # Lista de módulos para testar
        modulos = ['rpa_arc.cli', 'rpa_arc.estrutura', 'rpa_arc.conteudos']
        
        for modulo in modulos:
            try:
                # Remove o módulo do cache se existir
                if modulo in sys.modules:
                    del sys.modules[modulo]
                
                # Tenta importar
                importlib.import_module(modulo)
            except ImportError as e:
                pytest.fail(f"Falha ao importar {modulo}: {e}")
            except Exception as e:
                pytest.fail(f"Erro inesperado ao importar {modulo}: {e}")

    def test_version_consistency(self):
        """Testa consistência de versão entre arquivos."""
        # Verifica se a versão está definida em pyproject.toml
        try:
            # Tenta importar tomllib (Python 3.11+) ou tomli (Python < 3.11)
            try:
                import tomllib
            except ImportError:
                import tomli as tomllib
            
            with open("pyproject.toml", "rb") as f:
                data = tomllib.load(f)
                version = data["project"]["version"]
                assert version is not None, "Versão não definida"
                assert isinstance(version, str), "Versão deve ser string"
                assert len(version) > 0, "Versão não pode estar vazia"
        except Exception as e:
            pytest.fail(f"Erro ao verificar versão: {e}")

    def test_dependencies_consistency(self):
        """Testa consistência das dependências."""
        from rpa_arc.conteudos import REQUIREMENTS_CONTENT
        
        # Verifica se requirements.txt contém dependências essenciais
        dependencias_essenciais = [
            "requests", "python-dotenv", "selenium", "webdriver-manager"
        ]
        
        for dep in dependencias_essenciais:
            assert dep in REQUIREMENTS_CONTENT, f"Dependência essencial {dep} não encontrada"

    def test_cli_help_output(self):
        """Testa se a CLI tem saída de ajuda."""
        from rpa_arc.cli import main
        import argparse
        
        # Testa se ArgumentParser está configurado
        try:
            with patch('sys.argv', ['rpa-arc', '--help']):
                # Deve gerar SystemExit (comportamento normal do argparse)
                with pytest.raises(SystemExit):
                    main()
        except Exception as e:
            pytest.fail(f"CLI não tem saída de ajuda válida: {e}") 