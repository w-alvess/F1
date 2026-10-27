# F1 Dashboard

Dashboard interativo para explorar dados históricos da Fórmula 1 (a partir de 2023)
consumindo a [OpenF1 API](https://openf1.org/docs), que é aberta e dispensa
autenticação para dados históricos.

## O que o dashboard mostra

- Seleção de **temporada → etapa → sessão**, ou atalho para a sessão mais recente (`latest`)
- Indicadores da sessão: pilotos, voltas registradas, voltas válidas e tempo médio
- **Top N voltas mais rápidas** (uma por piloto), com cartões do pódio, tabela com a
  cor da equipe, setores e speed trap
- Gráfico com o gap de cada piloto para a volta mais rápida

## Links rápidos

| Assunto | Página |
|---|---|
| Camadas e injeção de dependência | [Arquitetura](architecture.md) |
| Árvore de diretórios | [Estrutura do Projeto](project-structure.md) |
| Instalar e rodar | [Como Rodar Local](running-locally.md) |
| Testes e cobertura | [Como Rodar Testes](running-tests.md) |
| Fluxo de PR | [Como Contribuir](contributing.md) |

!!! note "Dados em tempo real"
    A OpenF1 exige assinatura para dados ao vivo. O projeto usa apenas o acesso
    histórico gratuito, mas a camada de ingestão está pronta para receber outra
    implementação dos repositórios.
