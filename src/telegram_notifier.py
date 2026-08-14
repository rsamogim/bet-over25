from __future__ import annotations

import os

import requests

TELEGRAM_API_BASE = "https://api.telegram.org"

MENSAGEM_TEMPLATE = """\
⚽ <b>Jogo na janela de checagem</b>

🏆 {competicao} — {time_casa} x {time_fora}
🕐 {horario_brasilia}

📊 xG total esperado (via Pinnacle devigged): {xg_total:.2f}
📈 Probabilidade justa Over 2,5: {prob_over:.1%}
📉 Probabilidade justa Under 2,5: {prob_under:.1%}

💰 Odd mínima na Betfair pra Over 2,5 valer EV+: {odd_minima_over:.2f}
💰 Odd mínima na Betfair pra Under 2,5 valer EV+: {odd_minima_under:.2f}
(já líquidas da comissão de {comissao:.1%})

⚠️ Modelo baseado em devig da Pinnacle (método de Shin). Confira a odd atual na \
Betfair manualmente antes de decidir — este alerta não busca a odd da Betfair \
automaticamente. Não é garantia de resultado — variância de curto prazo é real \
mesmo com edge genuíno."""


class TelegramError(RuntimeError):
    pass


def _credenciais() -> tuple[str, str]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise TelegramError("TELEGRAM_BOT_TOKEN e/ou TELEGRAM_CHAT_ID não definidos no ambiente")
    return token, chat_id


def montar_mensagem(
    competicao: str,
    time_casa: str,
    time_fora: str,
    horario_brasilia: str,
    xg_total: float,
    prob_over: float,
    prob_under: float,
    odd_minima_over: float,
    odd_minima_under: float,
    comissao: float,
) -> str:
    return MENSAGEM_TEMPLATE.format(
        competicao=competicao,
        time_casa=time_casa,
        time_fora=time_fora,
        horario_brasilia=horario_brasilia,
        xg_total=xg_total,
        prob_over=prob_over,
        prob_under=prob_under,
        odd_minima_over=odd_minima_over,
        odd_minima_under=odd_minima_under,
        comissao=comissao,
    )


def enviar_alerta(mensagem: str) -> None:
    token, chat_id = _credenciais()
    resp = requests.post(
        f"{TELEGRAM_API_BASE}/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": mensagem, "parse_mode": "HTML"},
        timeout=20,
    )
    resp.raise_for_status()
