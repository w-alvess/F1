# Como Rodar Testes

## Testes unitários

```bash
poetry run pytest tests/unit/
```

São isolados: o `HttpClient` usa `httpx.MockTransport`, os repositórios do serviço
são `MagicMock` e o backoff recebe uma função `sleep` falsa, então nenhum teste
espera nem acessa a rede.

| Arquivo | Cobre |
|---|---|
| `test_lap_processor.py` | funções puras de `processing/` |
| `test_models.py` | parsing dos payloads OpenF1 |
| `test_services.py` | `F1DashboardService` com repositórios mockados |
| `test_http_client.py` | retry, backoff, timeout, 404, 4xx, payloads inválidos |
| `test_openf1_client.py` | montagem das queries e descarte de itens inválidos |
| `test_config.py` | leitura e validação do `.env` |
| `test_dashboard.py` | conversão do ranking em tabela |

## Testes de integração

```bash
poetry run pytest tests/integration/ -m integration
```

Batem na OpenF1 real (`session_key=latest`, `meeting_key=latest`) e exigem internet.
Por padrão o `pyproject.toml` aplica `-m 'not integration'`, então `poetry run pytest`
sozinho **não** chama a API. Passar `-m integration` sobrescreve esse filtro.

!!! note "Cobertura ao rodar só a integração"
    O `--cov-fail-under=50` também vale para esta execução. Se ela falhar apenas por
    cobertura, acrescente `--no-cov`.

## Cobertura

O mínimo é **50%** (`--cov-fail-under=50`) e o relatório `term-missing` lista as
linhas não cobertas. Para um relatório HTML:

```bash
poetry run pytest tests/unit/ --cov-report=html   # abre htmlcov/index.html
```

O `dashboard.py` tem a menor cobertura porque as funções `render_*` dependem do
runtime do Streamlit. A lógica testável dele fica em funções puras, como
`top_laps_to_dataframe`.
