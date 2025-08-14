REQUIREMENTS_CONTENT = """
requests
python-dotenv
selenium
webdriver-manager
fastapi
uvicorn
"""

ENV_CONTENT = """
####################API-RPA CREDENCIAIS#######################
LOGIN_API = seu_user_api
PASSWORD_API = sua_senha_api
"""

API_CONTENT = '''
import base64
import os
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()


class Api:
    """Camada fininha sobre *requests* com autenticação JWT, registro de logs e upload para S3.

    Agora tudo vive aqui; não existe mais helper externo ou `RestBuilder`. Mudou o host? É só
    passar nos parâmetros do construtor.
    """

    def __init__(
        self,
        hostname: str = "api-rpa.tecksolucoes.com.br",
        port: Optional[int] = None,
        protocol: str = "https",
    ) -> None:
        base = f"{protocol}://{hostname}{f':{port}' if port else ''}"
        # Evita // no final/intermediário; garante que *não* termina com barra
        self._base_url = base.rstrip("/")

        # Cache do token
        self.token: Optional[str] = None

        # Credenciais (já vêm em base64 no .env)
        self._username = base64.b64decode(os.getenv("LOGIN_API", "").encode()).decode()
        self._password = base64.b64decode(os.getenv("PASSWORD_API", "").encode()).decode()

    # -------------------------------------------------------------------------
    # Helpers low‑level
    # -------------------------------------------------------------------------

    def _url(self, *segments: str) -> str:
        """Concatena `self._base_url` com os *segments* removendo barras duplicadas."""
        clean = [s.strip("/") for s in segments if s]
        return "/".join([self._base_url, *clean])

    def _post(self, url: str, *, token: str | None = None, **kwargs):
        headers = kwargs.pop("headers", {})
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return requests.post(url, headers=headers, timeout=30, **kwargs)

    def _get(self, url: str, *, token: str | None = None, **kwargs):
        headers = kwargs.pop("headers", {})
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return requests.get(url, headers=headers, timeout=30, **kwargs)

    # -------------------------------------------------------------------------
    # Autenticação e validação do token
    # -------------------------------------------------------------------------

    def GetToken(self) -> str | bool:
        url = self._url("api", "token")
        payload = {"username": self._username, "password": self._password}
        try:
            resp = self._post(url, json=payload)
            if resp.status_code == 200:
                self.token = resp.json().get("access")
                return self.token  # type: ignore[return-value]
            print(f"Erro: {resp.status_code} - {resp.text}")
            return False
        except Exception as exc:
            print(f"POST Error - {exc}")
            return False

    def CheckToken(self) -> None:
        """Garante que `self.token` existe e é válido; renova se necessário."""
        if not self.token:
            self.token = self.GetToken()
            return

        url = self._url("api", "validateToken")
        try:
            resp = self._get(url, token=self.token)
            if resp.status_code != 200:
                print(f"Token inválido ({resp.status_code}). Gerando novo token…")
                self.token = self.GetToken()
        except Exception as exc:
            print(f"Erro ao verificar token: {exc}. Tentando novo token.")
            self.token = self.GetToken()

    def ValidateUser(self, username: str, password: str) -> Optional[dict]:
        url = self._url("api", "token")
        payload = {"username": username, "password": password}
        try:
            resp = self._post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return {"user_id": data.get("user_id"), "token": data.get("access")}
            print(f"Erro ao validar usuário ({resp.status_code}). Detalhes: {resp.text}")
            return None
        except Exception as exc:
            print(f"Erro ao validar usuário: {exc}")
            return None

    # -------------------------------------------------------------------------
    # Logs
    # -------------------------------------------------------------------------

    def InserirLogApi(
        self,
        nivel_log: str,
        endpoint: str,
        dados_requisicao,
        dados_resposta=None,
        detalhes_erro: str = "",
        duracao_ms: int = 0,
        mensagem: str = "",
        token: str | None = None,
    ):
        if not token:
            self.CheckToken()
            token = self.token
        url = self._url("api", "insert_logs_api")
        payload = {
            "nivel_log": nivel_log,
            "endpoint": endpoint,
            "dados_requisicao": dados_requisicao,
            "dados_resposta": dados_resposta,
            "detalhes_erro": detalhes_erro,
            "duracao_ms": duracao_ms,
            "mensagem": mensagem,
        }
        try:
            resp = self._post(url, json=payload, token=token)
            if resp.status_code == 200:
                print("Log inserido com sucesso.")
                return resp.json()
            print(f"Erro ao inserir log na API ({resp.status_code}). Detalhes: {resp.text}")
            return None
        except Exception as exc:
            print(f"Erro ao inserir log na API: {exc}")
            return None

    # -------------------------------------------------------------------------
    # Upload S3
    # -------------------------------------------------------------------------

    def EnviarArquivoS3(self, caminho_arquivo: str, caminho_destino: str):
        """Envia um arquivo para `/api/enviar_s3/` via *multipart/form-data*."""
        self.CheckToken()
        url = self._url("api", "enviar_s3")
        try:
            with open(caminho_arquivo, "rb") as f:
                files = {"arquivo": (os.path.basename(caminho_arquivo), f)}
                data = {"caminho": caminho_destino}
                resp = self._post(url, data=data, files=files, token=self.token)
            if resp.status_code == 200:
                resultado = resp.json()
                print(f"✅ Arquivo enviado: {resultado.get('message')}")
                print(f"🔗 URL temporária: {resultado.get('url_temporaria')}")
                return resultado
            print(f"❌ Falha ao enviar ({resp.status_code}): {resp.text}")
            return None
        except Exception as exc:
            print(f"🚨 Erro geral no EnviarArquivoS3: {exc}")
            return None

'''

LOGGER_CONTENT = """
import logging
import os
from datetime import datetime
import time
from logging.handlers import TimedRotatingFileHandler


class DailyFileHandler(TimedRotatingFileHandler):
    def __init__(self, log_dir: str, log_level=logging.INFO):
        os.makedirs(log_dir, exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d.log")
        filename = os.path.join(log_dir, today)
        super().__init__(filename, when='midnight', interval=1, backupCount=0, encoding='utf-8')
        self.setLevel(log_level)
        fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.setFormatter(fmt)
        self.suffix = ""
        self.extMatch = None

    def doRollover(self):
        if self.stream:
            self.stream.close()
        new_name = datetime.now().strftime("%Y-%m-%d.log")
        self.baseFilename = os.path.join(self.baseFilename.rsplit(os.sep, 1)[0], new_name)
        self.stream = open(self.baseFilename, 'a', encoding=self.encoding)

class Logger:
    def __init__(self, name=__name__, log_dir='logs', log_level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        # evita handlers duplicados
        if not self.logger.handlers:
            # handler diário
            daily_handler = DailyFileHandler(log_dir, log_level)
            # handler de console
            console = logging.StreamHandler()
            console.setLevel(log_level)
            console.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

            self.logger.addHandler(daily_handler)
            self.logger.addHandler(console)

    def get_logger(self):
        return self.logger
"""




ENVIAR_S3_CONTENT = '''
import requests
from dotenv import load_dotenv
import os
from src.core.logger import Logger
from src.utils.helpers._get_token import GetToken


class EnviarS3:
    """
    Classe para enviar arquivos para o endpoint /api/enviar_s3/ usando multipart/form-data.
    Inclui o token JWT no header de Authorization.
    """

    def __init__(self, logger: Logger = None):
        load_dotenv()
        self.base_url = os.getenv("URL_API_RPA_V2") or os.getenv("URL_API")  # fallback
        self.token = GetToken().token
        self.logger = logger or Logger().get_logger()

    def EnviarArquivoS3(self, caminho_arquivo, caminho_destino):
        """
        Envia um arquivo (por exemplo .log) para o endpoint /api/enviar_s3/ usando multipart/form-data.
        Retorna o JSON com 'message' e 'url_temporaria' caso de sucesso, ou None em caso de falha.
        """
        max_tentativas = 2  # uma com o token atual, outra após renovar

        for tentativa in range(1, max_tentativas + 1):
            try:
                url = f"{self.base_url}/api/enviar_s3/"
                with open(caminho_arquivo, "rb") as f:
                    files = {
                        "arquivo": (os.path.basename(caminho_arquivo), f)
                    }
                    data = {
                        "caminho": caminho_destino
                    }
                    headers = {
                        "Authorization": f"Bearer {self.token}"
                    }

                    response = requests.post(url, files=files, data=data, headers=headers)

                if response.status_code == 200:
                    resultado = response.json()
                    self.logger.info(f"✅ Arquivo enviado: {resultado.get('message')}")
                    self.logger.info(f"🔗 URL temporária: {resultado.get('url_temporaria')}")
                    os.remove(caminho_arquivo)
                    self.logger.info(f"🗑️ Arquivo removido localmente: {caminho_arquivo}")
                    return resultado

                elif response.status_code in (401, 403):
                    self.logger.warning(f"🔒 Token inválido ou expirado. Tentativa {tentativa} de {max_tentativas}")
                    if tentativa < max_tentativas:
                        self.token = GetToken().token  # atualiza token
                        continue

                self.logger.error(f"❌ Falha ao enviar ({response.status_code}): {response.text}")
                return None

            except Exception as e:
                self.logger.error(f"💥 Erro geral no EnviarArquivoS3 (tentativa {tentativa}): {e}")
                return None


if __name__ == "__main__":
    s3_uploader = EnviarS3(logger=Logger().get_logger())

    # Exemplo de uso
    caminho_arquivo = "logs/2025-06-20.log"
    caminho_destino = "rpa/contratos_cancelados/2025-06-20.log"

    resultado = s3_uploader.EnviarArquivoS3(caminho_arquivo, caminho_destino)

    if resultado:
        print("Upload bem-sucedido!")
    else:
        print("Falha no upload.")
'''




GET_TOKEN_CONTENT = """
import os
import requests
from dotenv import load_dotenv
from src.core.logger import Logger

load_dotenv()
URL_API_RPA_V2 = os.getenv("URL_API_RPA_V2", "http://localhost:3000/v2")


class GetToken:
    def __init__(self):
        self.logger = Logger().get_logger()
        self.token = None
        self.check_token()

    def get_token(self):
        url = f"{URL_API_RPA_V2}/auth/token"
        credentials = {
            "username": os.getenv("USER_API_RPA"),
            "password": os.getenv("SENHA_API_RPA")
        }
        print(f"Obtendo token para {credentials['username']}...com senha {credentials['password']}")

        try:
            response = requests.post(url, json=credentials)
            if response.status_code == 200:
                return response.json().get("access_token")
            else:
                self._log_error(f"❌ Erro ao obter token ({response.status_code}): {response.text}")
        except Exception as e:
            self._log_error(f"💥 Erro na requisição de token: {e}")
        return None

    def check_token(self):
        if not self.token:
            self.token = self.get_token()
            return

        url = f"{URL_API_RPA_V2}/auth/refresh"
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                self._log_error(f"🔄 Token inválido, tentando obter novo.")
                self.token = self.get_token()
        except Exception as e:
            self._log_error(f"💥 Erro ao validar token: {e}")
            self.token = self.get_token()

    def _log_error(self, msg):
        self.logger.error(msg)


if __name__ == "__main__":
    token_manager = GetToken()
    token = token_manager.token
    print(f"Token obtido: {token}")

"""


DRIVER_CONTENT = '''
import os
import platform
import re
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class GerenciadorNavegador:
    def __init__(self, diretorio_arquivo=None) -> None:
        if diretorio_arquivo is None:
            diretorio_arquivo = os.path.abspath("dados/arquivos")

        os.makedirs(diretorio_arquivo, exist_ok=True)

        self.driver = None
        self._DIRETORIO_ARQUIVO = diretorio_arquivo

    @staticmethod
    def obter_versao_chrome():
        """
        Tenta obter a versão do Chrome instalada.
        Retorna uma string, ou 'Nao foi possivel obter a versao do Chrome.' se falhar.
        """
        comandos = {
            "Windows": "reg query HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon /v version",
            "Linux": [
                "google-chrome --version",
                "google-chrome-stable --version",
                "chromium --version",
            ],
        }

        sistema = platform.system()
        if sistema == "Windows":
            try:
                resultado = subprocess.check_output(
                    comandos["Windows"], shell=True, text=True
                )
                versao = re.search(r"\d+\.\d+\.\d+\.\d+", resultado).group()
                return versao
            except:
                pass
        elif sistema == "Linux":
            for comando in comandos["Linux"]:
                try:
                    resultado = subprocess.check_output(
                        comando, shell=True, text=True
                    )
                    versao = re.search(r"\d+\.\d+\.\d+\.\d+", resultado).group()
                    return versao
                except:
                    continue

        return "Nao foi possivel obter a versao do Chrome."

    def Open(self) -> webdriver.Chrome:
        """
        Inicializa o driver do Chrome com opções específicas.
        Adiciona prints para depuração de versões e caminhos.
        """
        if self.driver is None:
            options = Options()

            sistema = platform.system()

            # Configurações para desativar a caixa de diálogo de download
            prefs = {
                "profile.default_content_settings.popups": 0,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "download.default_directory": self._DIRETORIO_ARQUIVO,
                # adicione estas duas linhas:
                "safebrowsing.enabled": False,
                "safebrowsing.disable_download_protection": True,
            }
            options.add_experimental_option("prefs", prefs)

            # Configurações específicas para Linux
            if sistema == "Linux":
                options.binary_location = "/usr/bin/google-chrome"
                options.add_argument('--headless=new')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--start-maximized')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_argument('--ignore-certificate-errors')
                options.add_argument('--allow-insecure-localhost')
                options.add_argument('--disable-extensions')
                options.page_load_strategy = 'eager'

            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            #options.add_argument('--incognito')

            # Define um User-Agent específico
            options.add_argument(
                "user-agent=Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/89.0.4389.90 Safari/537.36"
            )

            # Se precisar fixar a versão do ChromeDriver, troque .install() por:
            # ChromeDriverManager(driver_version="131.0.6778.264").install()
            driver_path = ChromeDriverManager().install()
            service = Service(driver_path)

            # Prints de debug
            print("-------------------------------------------")
            print(f"[DEBUG] Versao do Chrome: {self.obter_versao_chrome()}")
            print(f"[DEBUG] Versao do selenium (webdriver): {webdriver.__version__}")
            print(f"[DEBUG] ChromeDriver salvo em: {driver_path}")
            print(f"[DEBUG] Arquivos baixados serão salvos em: {self._DIRETORIO_ARQUIVO}")
            print("-------------------------------------------")

            try:
                self.driver = webdriver.Chrome(service=service, options=options)

                # Permite downloads automáticos
                self.driver.execute_cdp_cmd(
                    "Page.setDownloadBehavior",
                    {
                        "behavior": "allow",
                        "downloadPath": str(self._DIRETORIO_ARQUIVO)
                    }
                )

                self.driver.delete_all_cookies()
                self.driver.implicitly_wait(10)
                self.driver.set_page_load_timeout(60)
                return self.driver
            except Exception as e:
                print(f"Erro ao configurar o navegador: {e}")
                return None

        return self.driver

    def obter_navegador(self):
        """
        Retorna a instância do driver, se existir.
        Se não existir, cria chamando self.Open().
        """
        if not self.driver:
            self.driver = self.Open()
        return self.driver
'''



DOCKERFILE_CONTENT = """
FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Sao_Paulo

# Dependências do sistema + libs do Chrome
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    unzip \
    curl \
    gnupg \
    ca-certificates \
    fonts-liberation \
    xdg-utils \
    tzdata \
    # libs gráficas/áudio usadas pelo Chrome
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxss1 \
    libgbm1 \
    libxshmfence1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxtst6 \
    libgtk-3-0 \
    libdrm2 \
    libxcb-dri3-0 \
    libgdk-pixbuf-2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Repositório oficial do Google Chrome (com keyring moderno) --DESCOMENTE CASO SEU PROJETO USE AUTOMAÇÃO DE NAVEGADOR
# RUN mkdir -p /etc/apt/keyrings && \
#     curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-linux.gpg && \
#     echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-linux.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
#       > /etc/apt/sources.list.d/google-chrome.list && \
#     apt-get update && apt-get install -y --no-install-recommends \
#       google-chrome-stable \
#       && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar e instalar requirements primeiro pra cachear melhor
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do projeto
COPY . .

CMD ["python3", "main.py"]


# docker build --no-cache -t nome_da_imagem .
# docker run -d -p 3000:3000 --name meu_container nome_da_imagem

"""

GITIGNORE_CONTENT = """
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
#   For a library or package, you might want to ignore these files since the code is
#   intended to run in multiple environments; otherwise, check them in:
# .python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# UV
#   Similar to Pipfile.lock, it is generally recommended to include uv.lock in version control.
#   This is especially recommended for binary packages to ensure reproducibility, and is more
#   commonly ignored for libraries.
#uv.lock

# poetry
#   Similar to Pipfile.lock, it is generally recommended to include poetry.lock in version control.
#   This is especially recommended for binary packages to ensure reproducibility, and is more
#   commonly ignored for libraries.
#   https://python-poetry.org/docs/basic-usage/#commit-your-poetrylock-file-to-version-control
#poetry.lock

# pdm
#   Similar to Pipfile.lock, it is generally recommended to include pdm.lock in version control.
#pdm.lock
#   pdm stores project-wide configurations in .pdm.toml, but it is recommended to not include it
#   in version control.
#   https://pdm.fming.dev/latest/usage/project/#working-with-version-control
.pdm.toml
.pdm-python
.pdm-build/

# PEP 582; used by e.g. github.com/David-OConnor/pyflow and github.com/pdm-project/pdm
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# PyCharm
#  JetBrains specific template is maintained in a separate JetBrains.gitignore that can
#  be found at https://github.com/github/gitignore/blob/main/Global/JetBrains.gitignore
#  and can be added to the global gitignore or merged into this file.  For a more nuclear
#  option (not recommended) you can uncomment the following to ignore the entire idea folder.
#.idea/

# Ruff stuff:
.ruff_cache/

# PyPI configuration file
.pypirc

"""

DOCKERIGNORE_CONTENT = """
# Ignore o ambiente virtual
venv/
.venv/
ENV/
env/
env.bak/
venv.bak/

# Ignore arquivos Python compilados
__pycache__/
*.py[cod]
*$py.class

# Ignore arquivos de log
*.log
logs/

# Ignore arquivos e diretórios de testes
tests/
.pytest_cache/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/

                
# Ignore dependências temporárias
*.egg-info/
.eggs/
dist/
build/
*.egg
pip-log.txt
pip-delete-this-directory.txt

# Ignore cache e lixo
*.DS_Store
*.swp
*.bak
*.tmp

# Ignore documentação gerada
docs/_build/

# Ignore arquivos de IDEs
.idea/
.vscode/
*.code-workspace

# Jupyter Notebooks
.ipynb_checkpoints/

# Arquivos de controle de versionamento que não devem ir pro container
.git/
.gitignore
.dockerignore
"""