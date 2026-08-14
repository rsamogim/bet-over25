# Alertas EV+ Mais/Menos 2,5 Gols

Monitora jogos das grandes ligas europeias e sul-americanas, compara a probabilidade
justa do mercado Mais/Menos 2,5 gols (devig das odds da Pinnacle) contra a odd da
Betfair Exchange, e alerta no Telegram quando houver EV+. **Não aposta sozinho.**

## Status: Fase 0 (validação obrigatória) — ✅ CONCLUÍDA

Todos os 7 itens confirmados. Ver detalhes e achados completos em
[`docs/fase0.md`](docs/fase0.md). Pronto pra começar a Fase 1 (implementação de
`src/`).

| # | Item | Status |
|---|------|--------|
| 1 | Cobertura Pinnacle + O/U confirmada com chamada real | ✅ confirmado — The Odds API, chamada real em 2026-08-14 |
| 2 | Cobertura Pinnacle nas ligas sul-americanas | ✅ confirmado — `soccer_brazil_campeonato` tem Pinnacle + totals |
| 3 | Comissão atual da Betfair Exchange | ✅ informada pelo usuário: **6,5%** — constante `BETFAIR_COMMISSION` no `.env` |
| 4 | Autenticação da Betfair API-NG | ✅ **N/A por decisão do usuário** — Betfair descontinuou API-NG pra contas BR (jan/2025). Alerta não busca odd da Betfair automaticamente; usuário confere manualmente |
| 5 | Pacote `shin` validado | ✅ confirmado — bateu exatamente com os 2 exemplos do README oficial do pacote |
| 6 | Fuso horário da API | ✅ confirmado — UTC ISO 8601 com sufixo `Z` |
| 7 | Orçamento de requisições | ✅ calculado — descoberta é grátis, checagem custa 1 req/jogo, chave atual = 500 req/mês, uso estimado ~270–280/mês (margem apertada, ver docs/fase0.md) |

**Achado que muda o design**: o mercado `totals` do endpoint de lista da The Odds
API não garante a linha 2,5 (Pinnacle varia a linha principal por jogo). É
obrigatório usar o mercado `alternate_totals` via endpoint por evento e filtrar
`point == 2.5`. Detalhes em `docs/fase0.md`.

## Estrutura planejada

```
alertas-ev-over25/
├── .github/workflows/
│   ├── descoberta_diaria.yml
│   └── checagem_e_alerta.yml
├── src/
│   ├── descoberta_jogos.py
│   ├── odds_client.py
│   ├── devig.py
│   ├── ev_calculator.py
│   ├── database.py
│   ├── telegram_notifier.py
│   └── main.py
├── data/alertas.db
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```
