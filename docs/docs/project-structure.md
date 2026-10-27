# Estrutura do Projeto

```
F1/
├── pyproject.toml              # dependências, Ruff, pytest, tarefas (taskipy)
├── poetry.lock                 # lock gerado pelo Poetry (não editar)
├── .env.example                # variáveis de ambiente esperadas
├── .pre-commit-config.yaml     # ruff, ruff-format, detect-secrets, checks de arquivos
├── mkdocs.yml                  # configuração desta documentação
├── README.md                   # guia rápido (ASCII)
├── src/
│   └── f1/
│       ├── dashboard.py        # composition root Streamlit
│       ├── domain/
│       │   ├── models.py       # modelos Pydantic dos payloads OpenF1 e projeções
│       │   ├── repositories.py # contratos (ABCs) por endpoint
│       │   └── services.py     # F1DashboardService
│       ├── ingestion/
│       │   ├── http_client.py  # HttpClient: timeout, retry, filtros
│       │   └── openf1_client.py# repositórios concretos OpenF1
│       ├── processing/
│       │   └── lap_processor.py# filtros, ranking, médias, formatação de tempo
│       └── utils/
│           ├── config.py       # Settings carregadas do .env
│           └── logger.py       # get_logger
├── tests/
│   ├── conftest.py             # fixtures de payloads e entidades
│   ├── unit/                   # sem rede; httpx.MockTransport e MagicMock
│   └── integration/            # @pytest.mark.integration, API real
└── docs/
    └── docs/                   # páginas desta documentação
```

## Onde colocar código novo

| Preciso de... | Lugar |
|---|---|
| Um novo endpoint OpenF1 (ex.: `stints`) | modelo em `domain/models.py`, ABC em `domain/repositories.py`, implementação em `ingestion/openf1_client.py` |
| Uma transformação ou agregação | função pura em `processing/` |
| Um novo caso de uso do dashboard | método em `F1DashboardService` |
| Um novo componente visual | função `render_*` em `dashboard.py` |
