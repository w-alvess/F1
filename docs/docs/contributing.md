# Como Contribuir

## Fluxo

1. Crie uma branch a partir da `main` (merge direto na `main` é proibido).
2. Instale os hooks uma vez: `poetry run pre-commit install`.
3. Faça a mudança seguindo as camadas descritas em [Arquitetura](architecture.md).
4. Rode lint e testes localmente.
5. Abra o Pull Request com a descrição no formato abaixo. Outra pessoa do time aprova.

## Padrões obrigatórios

- Type hints em todas as funções e métodos
- `get_logger(__name__)` em vez de `print`
- Imports absolutos (`from f1.domain.models import Lap`)
- `snake_case` para funções, variáveis e módulos; `PascalCase` para classes; `UPPER_CASE` para constantes
- Configuração via `.env`; nada sensível no código
- Não use `--no-verify` nem `pip install`

## Antes de abrir o PR

```bash
poetry run ruff check .
poetry run ruff format . --check
poetry run pytest tests/unit/
```

## Descrição do PR

```markdown
## O que foi feito
Descrição objetiva das mudanças realizadas.

## Por que foi feito
Contexto técnico ou de negócio que justifica a alteração.

## Como testar
Passo a passo para validar as mudanças localmente.

## Checklist
- [ ] Lint passou (`poetry run ruff check .`)
- [ ] Testes passaram (`poetry run pytest`)
- [ ] Cobertura >= 50%
- [ ] Documentação atualizada (se aplicável)
- [ ] Sem secrets no código
```
