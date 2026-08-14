# Fase 0 — Validação obrigatória

Registro do que foi confirmado, como, e o que ainda depende de acesso do usuário
(contas/chaves de API que o Claude Code não pode criar sozinho).

## Item 5 — Pacote `shin` ✅ CONFIRMADO

- `pip install shin` **falha ao compilar** em Python 3.14 (não há wheel pré-compilada
  pra `cp314` no Windows na versão 0.2.2 — só até `cp313`). Builda via Rust/maturin e
  precisa de `cargo`/`rustc`, que não estavam instalados. **Decisão: fixar o projeto em
  Python 3.12** (já era o que o workflow do GitHub Actions especificava) — wheel
  pré-compilada existe pra essa versão, sem precisar de toolchain Rust.
- Instalado `shin` numa venv Python 3.12 local e testado contra os dois exemplos
  numéricos documentados no README do pacote (github.com/mberk/shin):
  - 3 vias, odds `[2.6, 2.4, 4.3]` → probabilidades `[0.37299406033208965, 0.4047794109200184, 0.2222265287474275]`, z=0.01694251276407055, 426 iterações (caso iterativo)
  - binário, odds `[1.5, 2.74]` → probabilidades `[0.6508515815085157, 0.3491484184914841]`, z=0.03172728540646625, 0 iterações (caso analítico fechado)
- Resultado local bateu **exatamente** (todos os dígitos) com os dois casos. `shin`
  validado para uso em produção.
- API real do pacote: `shin.calculate_implied_probabilities(odds, full_output=True)` —
  não é `shin.calculate(...)` como o prompt original supôs; ajustar em `devig.py`.

## Item 3 e 4 — BLOQUEIO ESTRUTURAL: API direta da Betfair não está disponível para contas do Brasil

**Achado crítico, confirmado via suporte oficial do Betfair Developer Program**
(support.developer.betfair.com/hc/en-us/articles/17814508363804):

- Desde **1º de janeiro de 2025**, a Betfair **descontinuou o acesso direto à API-NG
  (Personal Direct API) para clientes cadastrados como Brasil** — o motivo declarado
  oficialmente é "the Geo IP & authentication requirements for Brazil that heavily
  restrict the use of automated bots". App keys antigas de contas BR foram
  desativadas; `developer.betfair.com` não fica mais acessível a essas contas.
- Isso **não é** um bloqueio ao uso manual da Betfair Exchange — a Exchange é
  licenciada e opera normalmente no Brasil sob a SPA/MF (Portaria nº 248/2025), e o
  usuário continua conseguindo ver odds e apostar manualmente pelo site/app. O que
  não existe mais é a via programática oficial (API-NG) pra automação a partir de
  uma conta brasileira.
- A própria Betfair recomenda, como alternativa oficial pra automação/trading a
  partir do Brasil, ferramentas de terceiros (Geeks Toy, LayBack Trader, LayBack
  Bot, Traderline, BfBotManager, Wagertool, SokkerPro, Sharktool, MyBetSpace) — são
  softwares desktop, não uma API REST chamável de um workflow do GitHub Actions na
  nuvem.
- **Isso invalida a premissa arquitetural original** (estágio 2 do workflow
  `checagem_e_alerta.yml` chamando `BETFAIR_APP_KEY`/`BETFAIR_SESSION_TOKEN` direto
  da nuvem pra buscar a odd da Exchange).

### Nota — via alternativa encontrada, mas não adotada

Depois dessa decisão, encontrei que a **The Odds API também expõe a Betfair
Exchange como um bookmaker próprio** (`betfair_ex_uk`), agregando preços reais de
Over/Under 2,5 sem passar pela API restrita da própria Betfair (é a The Odds API
que coleta o preço publicamente, não uma chamada autenticada na conta do usuário).
Testado e confirmado (evento Fluminense x Palmeiras, 2026-08-14): `betfair_ex_uk`
retornou Over 2.5 @ 2.30 / Under 2.5 @ 1.68 via `alternate_totals`. Isso reabriria a
porta pra EV% automático de verdade. **Ressalva não resolvida**: não dá pra
confirmar se esse pool de liquidez UK/internacional é o mesmo que o usuário vê no
app da Betfair Brasil (mercados regulados às vezes têm liquidez segregada por
jurisdição, como Itália/Espanha). Apresentado ao usuário, que preferiu manter a
decisão original (sem odd ao vivo, comparação 100% manual) por segurança/
simplicidade. Fica registrado aqui caso queira reconsiderar no futuro.

### Decisão tomada com o usuário

O usuário optou por **remover a busca automática da odd da Betfair** do pipeline.
O alerta passa a trazer a probabilidade justa (via devig da Pinnacle) e a **odd
mínima necessária pra EV+** (já líquida da comissão configurada), e o usuário
confere manualmente a odd atual na Betfair antes de decidir apostar. Isso:

- Elimina a dependência de `BETFAIR_APP_KEY`/`BETFAIR_SESSION_TOKEN` e de qualquer
  chamada à API da Betfair — todo o pipeline continua 100% na nuvem via GitHub
  Actions, sem nada rodando localmente na máquina do usuário.
- Reduz o item 4 (autenticação Betfair API-NG) a **não aplicável** — não será
  implementado.
- Reduz o item 3 (comissão da Betfair) a uma **constante configurável** que o
  usuário informa (olhando a própria conta), não precisa mais de chamada
  autenticada à API pra confirmar.
- Muda o texto do alerta: em vez de "EV estimado: X%" (que dependia da odd real da
  Betfair), o alerta mostra a odd mínima de equilíbrio e pede pro usuário comparar
  manualmente com a odd exibida na Betfair no momento.

### Processo de autenticação Betfair API-NG (documentado, mas não aplicável a conta BR)

Confirmado via documentação oficial (support.developer.betfair.com):

- Cada conta recebe automaticamente uma **Delayed App Key** (dados atrasados,
  aprovação em minutos, boa pra dev/teste) e pode solicitar uma **Live App Key**
  (dados em tempo real, aprovação por e-mail em 1–3 dias úteis).
- Duas formas de login:
  - **Interativo**: usuário/senha (+2FA se ativo) a cada sessão — simples, mas não
    serve pra automação desatendida (GitHub Actions).
  - **Não-interativo (bot/cert)**: autenticação via certificado SSL cliente
    (`client-2048.crt` gerado localmente, upload em Conta → Configurações →
    Segurança → "Certificate Authentication"). É o método recomendado pra bots e o
    que este projeto deve usar, já que roda sem intervenção humana no GitHub Actions.
- **Pendente**: gerar de fato a App Key e o certificado na conta do usuário, e rodar
  uma chamada de login real pra confirmar que o fluxo funciona — isso requer acesso
  à conta Betfair do usuário (login, e-mail de aprovação da Live Key). Não posso
  criar contas nem fazer login em nome do usuário.

## Item 1 e 2 — Cobertura Pinnacle + O/U + ligas sul-americanas ✅ CONFIRMADO (chamada real)

Provedor escolhido pelo usuário: **The Odds API** (chave já ativa, ver `.env`).
Testado com chamadas reais em 2026-08-14:

- `GET /v4/sports/` lista `soccer_brazil_campeonato` ("Brazil Série A") — a
  preocupação levantada pela pesquisa documental (item abaixo) **não se confirmou**:
  o Brasileirão está coberto. `soccer_conmebol_copa_libertadores` e
  `soccer_conmebol_copa_sudamericana` também existem, mas não serão usados — o
  usuário decidiu cobrir **só ligas nacionais** (ver lista final abaixo).
- `GET /v4/sports/soccer_brazil_campeonato/odds/?regions=eu&markets=totals&bookmakers=pinnacle`
  retornou jogos reais com Pinnacle presente e mercado `totals` populado — cobertura
  confirmada.
- **Achado importante que muda o design do `odds_client.py`**: o mercado `totals`
  "featured" (endpoint de lista) traz só **uma linha por jogo**, e essa linha **nem
  sempre é 2,5** — a Pinnacle ajusta a linha principal conforme o total esperado
  (ex: um jogo veio com linha 2,25, não 2,5). Pra garantir a linha exata de 2,5 em
  todo jogo, é preciso o mercado `alternate_totals`, que só existe no endpoint por
  evento (`/v4/sports/{sport}/events/{eventId}/odds?markets=alternate_totals`), não
  no endpoint de lista. Testado e confirmado: o mesmo jogo que só tinha linha 2,25
  no featured market tinha a linha 2,5 completa (Over 2.28 / Under 1.66) no
  `alternate_totals` por evento. **`odds_client.py` deve sempre buscar via endpoint
  por evento com `markets=alternate_totals` e filtrar `point == 2.5`, nunca confiar
  no featured market.** Isso também encaixa perfeitamente na arquitetura de dois
  estágios já desenhada (estágio 2 já busca por jogo individual).

## Pesquisa documental prévia (mantida por histórico — a chamada real acima é que vale)

Pesquisa de documentação (não substitui a chamada real exigida pelo prompt original):

- **The Odds API**, FAQ oficial (theoddsapi.com/faq): plano Business (US$99/mês,
  200.000 requisições) inclui Pinnacle e Betfair Exchange como bookmakers, e mercados
  de totals (O/U) pra futebol.
- **Porém**: a mesma FAQ, ao listar as ligas de futebol cobertas, cita apenas Premier
  League, Champions League, Europa League, La Liga, Bundesliga, Serie A, Ligue 1,
  Eredivisie, EFL Championship, Liga MX e MLS — **não menciona Brasileirão, Libertadores
  ou Sul-Americana**. Isso não prova ausência (pode ser lista não-exaustiva do FAQ),
  mas é um sinal de alerta real contra a premissa do projeto. Não deu pra confirmar via
  o endpoint público `/sports` porque ele exige chave de API.
- **OddsPapi**: material de marketing do próprio site (blog) alega cobertura de 350+
  bookmakers incluindo Pinnacle e Betfair, mas não confirma explicitamente as ligas
  sul-americanas nem detalha profundidade de liquidez. Fonte é auto-promocional,
  peso baixo.
- **Conclusão**: item 1 e 2 **não podem ser considerados confirmados** só com pesquisa
  documental — exatamente como o prompt original exigia. É necessário:
  1. Uma chave de teste/trial de cada provedor candidato.
  2. Uma chamada real ao endpoint de sports/leagues pra ver se `soccer_brazil_campeonato`
     (ou equivalente) existe.
  3. Uma chamada real ao endpoint de odds desse sport_key filtrando por Pinnacle,
     checando se o mercado totals aparece e se há profundidade/liquidez razoável.

## Item 6 — Fuso horário ✅ CONFIRMADO (chamada real)

`commence_time` retornado pela The Odds API é UTC, ISO 8601 com sufixo `Z` (ex:
`"2026-08-15T19:30:00Z"`) — confirmado nas respostas reais acima, bate com a FAQ.
Conversão em `descoberta_jogos.py` deve ser `datetime.fromisoformat(...).astimezone(zoneinfo.ZoneInfo("America/Sao_Paulo"))`.

## Item 3 — Comissão Betfair Exchange — PENDENTE, precisa da conta do usuário

Varia por mercado, região e nível de fidelidade (Betfair Rewards/Reduzida). Só é
visível logado na conta real do usuário (Configurações → Minha Conta → Comissão) ou
via chamada autenticada à API (`getAccountFunds`/`getAccountDetails`). Não há como
confirmar sem acesso à conta.

## Item 7 — Orçamento de requisições ✅ CALCULADO (com números reais)

Confirmado nas chamadas reais acima:
- `GET /v4/sports/{sport}/events` (descoberta, sem odds) — **custo zero de quota**
  (`x-requests-used` não mudou depois dessa chamada). Isso valida a arquitetura de
  dois estágios do usuário: a descoberta diária pode rodar sem se preocupar com
  orçamento nenhum.
- `GET /v4/sports/{sport}/events/{id}/odds?markets=alternate_totals&bookmakers=pinnacle`
  (checagem por jogo) — **custa 1 requisição por chamada**, independente do número
  de linhas retornadas.
- A chave atual do usuário está num plano de **500 requisições/mês**
  (`x-requests-remaining` + `x-requests-used` = 500 exato). Isso é o plano free, não
  o Business de US$99/mês descrito no prompt original — **o usuário deve confirmar
  no próprio dashboard da The Odds API se esse é o plano pretendido** antes de ir
  pra produção. Os testes desta validação já consumiram ~5 requisições dessa cota
  (500 → ~495 restantes).

Fórmula: `total_mensal = Σ(jogos por liga por mês)` (descoberta é grátis, só a
checagem por jogo/janela de gatilho conta, e cada jogo é checado uma única vez por
causa do dedup).

Ligas decididas com o usuário — **apenas ligas nacionais**, sem copas continentais:
Premier League, La Liga, Bundesliga, Serie A (Itália), Ligue 1, Brasileirão Série A.

| Liga | Jogos/mês (estimativa, temporada cheia) |
|---|---|
| Premier League | ~40 |
| La Liga | ~40 |
| Bundesliga | ~34 |
| Serie A (Itália) | ~40 |
| Ligue 1 | ~34 |
| Brasileirão Série A | ~80–90 (quase todo dia, poucas pausas) |
| **Total estimado** | **~270–280/mês** |

Cabe dentro do limite de 500/mês, mas com margem apertada — não sobra muito espaço
pra retries, testes manuais (`workflow_dispatch`) ou meses com calendário mais
carregado (rodadas duplas por conta de Copa do Brasil/copas nacionais empurrando
jogos pro meio de semana). **Recomendação**: monitorar o header
`x-requests-remaining` nos primeiros alertas reais e, se ficar apertado, considerar
upgrade de plano ou reduzir a lista de ligas.
