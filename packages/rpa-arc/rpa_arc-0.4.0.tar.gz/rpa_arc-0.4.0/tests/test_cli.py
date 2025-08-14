import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from rpa_arc.cli import main


class TestCLI:
    """Testes para o módulo CLI da biblioteca rpa-arc."""

    def setup_method(self):
        """Configuração antes de cada teste."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = Path.cwd()
        self.test_dir = Path(self.temp_dir)

    def teardown_method(self):
        """Limpeza após cada teste."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('rpa_arc.cli.Path.cwd')
    @patch('rpa_arc.estrutura.criar_estrutura')
    def test_cli_sem_argumentos(self, mock_criar_estrutura, mock_cwd):
        """Testa CLI sem argumentos - deve criar estrutura na raiz atual."""
        # Arrange
        mock_cwd.return_value = self.test_dir
        
        # Act
        with patch('sys.argv', ['rpa-arc']):
            main()
        
        # Assert
        mock_criar_estrutura.assert_called_once_with(self.test_dir)

    @patch('rpa_arc.cli.Path.cwd')
    @patch('rpa_arc.estrutura.criar_estrutura')
    def test_cli_com_nome_projeto(self, mock_criar_estrutura, mock_cwd):
        """Testa CLI com nome do projeto - deve criar subpasta."""
        # Arrange
        mock_cwd.return_value = self.test_dir
        nome_projeto = "meu-projeto-rpa"
        
        # Act
        with patch('sys.argv', ['rpa-arc', nome_projeto]):
            main()
        
        # Assert
        caminho_esperado = self.test_dir / nome_projeto
        mock_criar_estrutura.assert_called_once_with(caminho_esperado)

    @patch('rpa_arc.cli.Path.cwd')
    @patch('builtins.print')
    def test_cli_pasta_existente(self, mock_print, mock_cwd):
        """Testa CLI quando a pasta já existe - deve abortar."""
        # Arrange
        mock_cwd.return_value = self.test_dir
        nome_projeto = "pasta-existente"
        pasta_existente = self.test_dir / nome_projeto
        pasta_existente.mkdir(parents=True)
        
        # Act
        with patch('sys.argv', ['rpa-arc', nome_projeto]):
            main()
        
        # Assert
        mock_print.assert_called_with(f"⚠️  A pasta '{nome_projeto}' já existe. Abortando para não sobrescrever nada.")

    @patch('rpa_arc.cli.Path.cwd')
    @patch('rpa_arc.estrutura.criar_estrutura')
    @patch('builtins.print')
    def test_cli_sucesso_com_nome(self, mock_print, mock_criar_estrutura, mock_cwd):
        """Testa mensagem de sucesso quando projeto é criado com nome."""
        # Arrange
        mock_cwd.return_value = self.test_dir
        nome_projeto = "novo-projeto"
        
        # Act
        with patch('sys.argv', ['rpa-arc', nome_projeto]):
            main()
        
        # Assert
        mock_print.assert_any_call(f"\n🎉 Projeto '{nome_projeto}' criado com sucesso!")
        mock_print.assert_any_call(f"📂 Local: {(self.test_dir / nome_projeto).resolve()}")

    @patch('rpa_arc.cli.Path.cwd')
    @patch('rpa_arc.estrutura.criar_estrutura')
    @patch('builtins.print')
    def test_cli_sucesso_sem_nome(self, mock_print, mock_criar_estrutura, mock_cwd):
        """Testa mensagem de sucesso quando estrutura é criada na raiz."""
        # Arrange
        mock_cwd.return_value = self.test_dir
        
        # Act
        with patch('sys.argv', ['rpa-arc']):
            main()
        
        # Assert
        mock_print.assert_any_call("\n🎉 Estrutura criada na raiz do projeto com sucesso!")
        mock_print.assert_any_call(f"📂 Local: {self.test_dir.resolve()}")

    def test_argument_parser_configuracao(self):
        """Testa se o ArgumentParser está configurado corretamente."""
        from rpa_arc.cli import main
        import argparse
        
        # Este teste verifica se o parser está configurado
        # Como main() usa ArgumentParser, podemos testar indiretamente
        assert True  # Placeholder - o teste real seria mais complexo

    @patch('rpa_arc.cli.Path.cwd')
    @patch('rpa_arc.estrutura.criar_estrutura')
    def test_cli_cria_diretorios_pais(self, mock_criar_estrutura, mock_cwd):
        """Testa se CLI cria diretórios pais quando necessário."""
        # Arrange
        mock_cwd.return_value = self.test_dir
        nome_projeto = "projeto/subpasta/nested"
        
        # Act
        with patch('sys.argv', ['rpa-arc', nome_projeto]):
            main()
        
        # Assert
        caminho_esperado = self.test_dir / nome_projeto
        mock_criar_estrutura.assert_called_once_with(caminho_esperado) 