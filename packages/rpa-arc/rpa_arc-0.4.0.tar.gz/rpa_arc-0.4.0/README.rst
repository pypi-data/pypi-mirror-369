rpa-arc
=======

🚀 **rpa-arc** cria a estrutura base de um projeto RPA em Python num piscar de olhos.

> Sem firula, na lata: um comando e pronto—you're ready to automate.

.. image:: https://img.shields.io/pypi/v/rpa-arc.svg
   :target: https://pypi.org/project/rpa-arc/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/rpa-arc.svg
   :target: https://pypi.org/project/rpa-arc/
   :alt: Python versions

.. image:: https://img.shields.io/pypi/l/rpa-arc.svg
   :target: https://pypi.org/project/rpa-arc/
   :alt: License

.. image:: https://img.shields.io/pypi/status/rpa-arc.svg
   :target: https://pypi.org/project/rpa-arc/
   :alt: Development Status

Por que usar rpa-arc?
---------------------

- **Simplicidade visionária:** seu projeto nasce 100% organizadinho
- **CLI intuitiva:** zig-zag, um ``rpa-arc nome-do-projeto`` e tudo se alinha
- **Flexível:** gera na raiz ou em subpasta, você escolhe
- **Estrutura completa:** inclui tudo que você precisa para um projeto RPA profissional

Requisitos
----------

- Python 3.7+
- requests
- python-dotenv
- selenium
- webdriver-manager

Instalação
----------

.. code-block:: bash

   pip install rpa-arc

Uso
---

.. code-block:: bash

   # Cria ./meu-projeto/
   rpa-arc meu-projeto

   # Gera estrutura na raiz atual (se não passar nome)
   rpa-arc

Estrutura Gerada
----------------

A biblioteca cria uma estrutura completa e organizada para projetos RPA:

.. code-block:: text

   meu-projeto/               # ou cwd/ se não passar nome
   ├── src/
   │   ├── app/
   │   │   └── app.py
   │   ├── core/
   │   │   ├── logger.py      # Sistema de logs com rotação diária
   │   │   └── driver.py      # Gerenciador de navegador Chrome
   │   ├── api/
   │   │   └── Api.py         # Cliente API com autenticação JWT
   │   ├── integracoes/       # Módulos de integração
   │   └── utils/             # Utilitários
   │       └── helpers/       # Helpers específicos
   ├── config/                # Arquivos de configuração
   ├── dados/                 # Dados e arquivos processados
   ├── logs/                  # Logs do sistema
   ├── tests/                 # Testes automatizados
   ├── .gitignore            # Configuração Git
   ├── .dockerignore         # Configuração Docker
   ├── Dockerfile            # Container Docker
   ├── requirements.txt       # Dependências Python
   ├── .env                  # Variáveis de ambiente
   ├── main.py               # Ponto de entrada
   └── README.md             # Documentação do projeto

Funcionalidades Principais
--------------------------

Sistema de Logs (logger.py)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Logs com rotação diária automática
- Saída para console e arquivo
- Formatação padronizada de timestamps
- Configuração flexível de níveis

.. code-block:: python

   from src.core.logger import Logger
   
   logger = Logger("meu_modulo").get_logger()
   logger.info("Iniciando processo RPA")
   logger.error("Erro encontrado")

Gerenciador de Navegador (driver.py)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Configuração automática do ChromeDriver
- Suporte a headless mode para Linux
- Download automático de arquivos
- Configurações otimizadas para RPA

.. code-block:: python

   from src.core.driver import GerenciadorNavegador
   
   navegador = GerenciadorNavegador()
   driver = navegador.obter_navegador()
   driver.get("https://exemplo.com")

Cliente API (Api.py)
~~~~~~~~~~~~~~~~~~~~

- Autenticação JWT automática
- Renovação automática de tokens
- Upload de arquivos para S3
- Sistema de logs integrado
- Tratamento de erros robusto

.. code-block:: python

   from src.api.Api import Api
   
   api = Api(hostname="api.exemplo.com")
   api.CheckToken()  # Valida/renova token automaticamente
   
   # Upload de arquivo para S3
   resultado = api.EnviarArquivoS3(
       "logs/2024-01-15.log",
       "rpa/relatorios/2024-01-15.log"
   )

Docker
------

O projeto inclui um Dockerfile otimizado com:

- Python 3.12-slim
- Dependências do sistema para Chrome
- Configuração de timezone (America/Sao_Paulo)
- Estrutura pronta para containerização

.. code-block:: bash

   docker build -t meu-projeto-rpa .
   docker run meu-projeto-rpa

Exemplo de Uso Completo
-----------------------

.. code-block:: python

   # main.py
   from src.core.logger import Logger
   from src.core.driver import GerenciadorNavegador
   from src.api.Api import Api
   
   def main():
       # Inicializar logger
       logger = Logger("rpa_processo").get_logger()
       logger.info("Iniciando automação RPA")
       
       try:
           # Configurar navegador
           navegador = GerenciadorNavegador()
           driver = navegador.obter_navegador()
           
           # Navegar para site
           driver.get("https://exemplo.com")
           logger.info("Site acessado com sucesso")
           
           # Processar dados...
           
           # Enviar logs para API
           api = Api()
           api.InserirLogApi(
               nivel_log="INFO",
               endpoint="/processo",
               dados_requisicao={"status": "sucesso"},
               mensagem="Processo concluído"
           )
           
       except Exception as e:
           logger.error(f"Erro no processo: {e}")
           
       finally:
           if driver:
               driver.quit()
   
   if __name__ == "__main__":
       main()

Configuração de Ambiente
------------------------

Crie um arquivo `.env` com suas configurações:

.. code-block:: text

   # API Configuration
   URL_API_RPA_V2=https://api.exemplo.com/v2
   USER_API_RPA=seu_usuario
   SENHA_API_RPA=sua_senha
   
   # Logs
   LOG_LEVEL=INFO
   
   # Downloads
   DOWNLOAD_DIR=dados/arquivos

Contribuição
------------

Sério, sua ajuda importa. Abra uma issue ou mande um PR—qualquer sugestão é bem-vinda.

Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (``git checkout -b feature/AmazingFeature``)
3. Commit suas mudanças (``git commit -m 'Add some AmazingFeature'``)
4. Push para a branch (``git push origin feature/AmazingFeature``)
5. Abra um Pull Request

Licença
-------

MIT License. Veja o `LICENSE <LICENSE>`_ para detalhes.

Changelog
---------

0.1.0
~~~~~

- Versão inicial
- CLI para geração de estrutura
- Sistema de logs com rotação diária
- Gerenciador de navegador Chrome
- Cliente API com autenticação JWT
- Suporte a Docker
- Estrutura completa de projeto RPA

Links
-----

- `PyPI <https://pypi.org/project/rpa-arc/>`_
- `GitHub <https://github.com/TeckSolucoes/RPA---LIB>`_
- `Documentação <https://rpa-arc.readthedocs.io/>`_ 