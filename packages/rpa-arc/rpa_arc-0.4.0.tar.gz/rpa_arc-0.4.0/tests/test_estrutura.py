import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.rpa_arc.estrutura import criar_estrutura, ESTRUTURA_PROJETO


class TestEstrutura:
    """Testes para o módulo estrutura da biblioteca rpa-arc."""

    def setup_method(self):
        """Configuração antes de cada teste."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)

    def teardown_method(self):
        """Limpeza após cada teste."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('builtins.print')
    def test_criar_estrutura_diretorios_principais(self, mock_print):
        """Testa se os diretórios principais são criados."""
        # Act
        criar_estrutura(self.test_dir)
        
        # Assert
        diretorios_esperados = ["config", "dados", "logs", "tests", "src"]
        for diretorio in diretorios_esperados:
            caminho = self.test_dir / diretorio
            assert caminho.exists(), f"Diretório {diretorio} não foi criado"
            assert caminho.is_dir(), f"{diretorio} não é um diretório"

    @patch('builtins.print')
    def test_criar_estrutura_subdiretorios_src(self, mock_print):
        """Testa se os subdiretórios dentro de src são criados."""
        # Act
        criar_estrutura(self.test_dir)
        
        # Assert
        src_path = self.test_dir / "src"
        subdiretorios_esperados = ["app", "core", "integracoes", "utils", "api"]
        for subdir in subdiretorios_esperados:
            caminho = src_path / subdir
            assert caminho.exists(), f"Subdiretorio {subdir} não foi criado"
            assert caminho.is_dir(), f"{subdir} não é um diretório"

    @patch('builtins.print')
    def test_criar_estrutura_arquivos_raiz(self, mock_print):
        """Testa se os arquivos na raiz são criados."""
        # Act
        criar_estrutura(self.test_dir)
        
        # Assert
        arquivos_esperados = [
            "requirements.txt", ".env", "Dockerfile", "README.md", 
            "main.py", ".gitignore", ".dockerignore"
        ]
        for arquivo in arquivos_esperados:
            caminho = self.test_dir / arquivo
            assert caminho.exists(), f"Arquivo {arquivo} não foi criado"
            assert caminho.is_file(), f"{arquivo} não é um arquivo"

    @patch('builtins.print')
    def test_criar_estrutura_arquivos_core(self, mock_print):
        """Testa se os arquivos do diretório core são criados."""
        # Act
        criar_estrutura(self.test_dir)
        
        # Assert
        core_path = self.test_dir / "src" / "core"
        arquivos_esperados = ["logger.py", "driver.py"]
        for arquivo in arquivos_esperados:
            caminho = core_path / arquivo
            assert caminho.exists(), f"Arquivo {arquivo} não foi criado em core"
            assert caminho.is_file(), f"{arquivo} não é um arquivo"

    @patch('builtins.print')
    def test_criar_estrutura_arquivos_api(self, mock_print):
        """Testa se os arquivos do diretório api são criados."""
        # Act
        criar_estrutura(self.test_dir)
        
        # Assert
        api_path = self.test_dir / "src" / "api"
        arquivos_esperados = ["Api.py"]
        for arquivo in arquivos_esperados:
            caminho = api_path / arquivo
            assert caminho.exists(), f"Arquivo {arquivo} não foi criado em api"
            assert caminho.is_file(), f"{arquivo} não é um arquivo"

    @patch('builtins.print')
    def test_criar_estrutura_conteudo_requirements(self, mock_print):
        """Testa se o arquivo requirements.txt tem o conteúdo correto."""
        # Act
        criar_estrutura(self.test_dir)
        
        # Assert
        requirements_path = self.test_dir / "requirements.txt"
        conteudo = requirements_path.read_text(encoding='utf-8')
        dependencias_esperadas = [
            "requests", "python-dotenv", "selenium", 
            "webdriver-manager", "fastapi", "uvicorn"
        ]
        for dependencia in dependencias_esperadas:
            assert dependencia in conteudo, f"Dependência {dependencia} não encontrada"

    @patch('builtins.print')
    def test_criar_estrutura_conteudo_dockerfile(self, mock_print):
        """Testa se o Dockerfile tem o conteúdo correto."""
        # Act
        criar_estrutura(self.test_dir)
        
        # Assert
        dockerfile_path = self.test_dir / "Dockerfile"
        conteudo = dockerfile_path.read_text(encoding='utf-8')
        assert "FROM python:3.12-slim" in conteudo
        assert "WORKDIR /app" in conteudo
        assert "CMD [" in conteudo

    @patch('builtins.print')
    def test_criar_estrutura_conteudo_gitignore(self, mock_print):
        """Testa se o .gitignore tem o conteúdo correto."""
        # Act
        criar_estrutura(self.test_dir)
        
        # Assert
        gitignore_path = self.test_dir / ".gitignore"
        conteudo = gitignore_path.read_text(encoding='utf-8')
        assert "__pycache__/" in conteudo
        assert "*.py[cod]" in conteudo
        assert ".env" in conteudo

    @patch('builtins.print')
    def test_criar_estrutura_conteudo_logger(self, mock_print):
        """Testa se o logger.py tem o conteúdo correto."""
        # Act
        criar_estrutura(self.test_dir)
        
        # Assert
        logger_path = self.test_dir / "src" / "core" / "logger.py"
        conteudo = logger_path.read_text(encoding='utf-8')
        assert "class Logger:" in conteudo
        assert "class DailyFileHandler" in conteudo
        assert "logging" in conteudo

    @patch('builtins.print')
    def test_criar_estrutura_conteudo_driver(self, mock_print):
        """Testa se o driver.py tem o conteúdo correto."""
        # Act
        criar_estrutura(self.test_dir)
        
        # Assert
        driver_path = self.test_dir / "src" / "core" / "driver.py"
        conteudo = driver_path.read_text(encoding='utf-8')
        assert "class GerenciadorNavegador:" in conteudo
        assert "selenium" in conteudo
        assert "webdriver" in conteudo

    @patch('builtins.print')
    def test_criar_estrutura_conteudo_api(self, mock_print):
        """Testa se o Api.py tem o conteúdo correto."""
        # Act
        criar_estrutura(self.test_dir)
        
        # Assert
        api_path = self.test_dir / "src" / "api" / "Api.py"
        conteudo = api_path.read_text(encoding='utf-8')
        assert "class Api:" in conteudo
        assert "requests" in conteudo
        assert "base64" in conteudo

    @patch('builtins.print')
    def test_criar_estrutura_mensagens_console(self, mock_print):
        """Testa se as mensagens de console são exibidas corretamente."""
        # Act
        criar_estrutura(self.test_dir)
        
        # Assert
        # Verifica se as mensagens principais foram chamadas
        calls = mock_print.call_args_list
        mensagens_esperadas = [
            "🛠️  Criando estrutura em:",
            "✅ Estrutura criada com sucesso!"
        ]
        
        for mensagem in mensagens_esperadas:
            assert any(mensagem in str(call) for call in calls), f"Mensagem '{mensagem}' não encontrada"

    def test_estrutura_projeto_constante(self):
        """Testa se a constante ESTRUTURA_PROJETO está definida corretamente."""
        # Assert
        assert "src" in ESTRUTURA_PROJETO
        assert "root_files" in ESTRUTURA_PROJETO
        assert isinstance(ESTRUTURA_PROJETO["src"], dict)
        assert isinstance(ESTRUTURA_PROJETO["root_files"], list)

    @patch('builtins.print')
    def test_criar_estrutura_diretorio_existente(self, mock_print):
        """Testa se a função funciona quando o diretório já existe."""
        # Arrange
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        # Act
        criar_estrutura(self.test_dir)
        
        # Assert - deve funcionar sem erro
        assert (self.test_dir / "src").exists()
        assert (self.test_dir / "config").exists()

    @patch('builtins.print')
    def test_criar_estrutura_permissoes(self, mock_print):
        """Testa se os arquivos criados têm permissões de leitura."""
        # Act
        criar_estrutura(self.test_dir)
        
        # Assert
        arquivos_teste = [
            self.test_dir / "requirements.txt",
            self.test_dir / "src" / "core" / "logger.py",
            self.test_dir / "src" / "api" / "Api.py"
        ]
        
        for arquivo in arquivos_teste:
            assert arquivo.exists()
            # Verifica se é possível ler o arquivo
            try:
                arquivo.read_text(encoding='utf-8')
            except PermissionError:
                pytest.fail(f"Não foi possível ler o arquivo {arquivo}") 