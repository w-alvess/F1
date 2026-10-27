# Como Rodar Local

## Pré-requisitos

- Python 3.12 (o arquivo `.python-version` fixa a 3.12.10 para o pyenv)
- [Poetry](https://python-poetry.org/) 2.x
- Acesso à internet (a OpenF1 é consultada em tempo de execução)

!!! warning "Não use `pip install`"
    Todas as dependências são gerenciadas pelo Poetry.

## Instalação

```bash
poetry install --with dev,docs
cp .env.example .env
```

!!! tip "Variável `VIRTUAL_ENV` herdada"
    Se `VIRTUAL_ENV` estiver definida no seu shell, o Poetry passa a usar aquele
    interpretador em vez do `.venv` do projeto. Remova a variável antes de rodar
    `poetry install` (PowerShell: `Remove-Item Env:VIRTUAL_ENV`).

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `OPENF1_BASE_URL` | `https://api.openf1.org/v1` | URL base da API |
| `OPENF1_TIMEOUT` | `10` | Timeout por requisição, em segundos |
| `ENVIRONMENT` | `development` | `development`, `staging` ou `production` |
| `LOG_LEVEL` | `INFO` | Nível de log (`DEBUG` mostra cada payload inválido) |

## Executar o dashboard

```bash
poetry run streamlit run src/f1/dashboard.py
```

Abra <http://localhost:8501>. Na barra lateral, escolha temporada, etapa e sessão, ou
ative **Sessão mais recente (latest)**.

## Executar a documentação

```bash
poetry run mkdocs serve   # http://127.0.0.1:8000
poetry run mkdocs build   # gera o site estático em site/
```

## Atalhos (taskipy)

```bash
poetry run task test      # testes unitários com cobertura
poetry run task lint      # ruff check .
poetry run task format    # ruff format .
poetry run task docs      # mkdocs serve
```
