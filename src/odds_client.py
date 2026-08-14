from __future__ import annotations

import os
from dataclasses import dataclass

import requests

BASE_URL = "https://api.the-odds-api.com/v4"
LINHA_ALVO = 2.5


class OddsApiError(RuntimeError):
    pass


@dataclass
class Evento:
    id_partida: str
    time_casa: str
    time_fora: str
    commence_time_utc: str


@dataclass
class OddsOverUnder:
    odd_over: float
    odd_under: float


def _api_key() -> str:
    key = os.environ.get("ODDS_API_KEY")
    if not key:
        raise OddsApiError("ODDS_API_KEY não definida no ambiente")
    return key


def listar_eventos(sport_key: str) -> list[Evento]:
    """Lista os jogos futuros de uma liga. Não consome cota da API (endpoint free)."""
    resp = requests.get(
        f"{BASE_URL}/sports/{sport_key}/events",
        params={"apiKey": _api_key()},
        timeout=20,
    )
    resp.raise_for_status()
    return [
        Evento(
            id_partida=item["id"],
            time_casa=item["home_team"],
            time_fora=item["away_team"],
            commence_time_utc=item["commence_time"],
        )
        for item in resp.json()
    ]


def buscar_odds_pinnacle_2_5(sport_key: str, id_partida: str) -> OddsOverUnder | None:
    """Busca a odd Over/Under 2,5 da Pinnacle pro jogo, via mercado alternate_totals
    por evento — o mercado 'totals' da listagem geral não garante a linha 2,5
    (a Pinnacle varia a linha principal por jogo, confirmado na Fase 0). Cada
    chamada consome 1 requisição da cota da API.
    """
    resp = requests.get(
        f"{BASE_URL}/sports/{sport_key}/events/{id_partida}/odds",
        params={
            "apiKey": _api_key(),
            "regions": "eu",
            "markets": "alternate_totals",
            "bookmakers": "pinnacle",
        },
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()

    bookmakers = data.get("bookmakers", [])
    if not bookmakers:
        return None

    outcomes = bookmakers[0]["markets"][0]["outcomes"]
    odd_over = next(
        (o["price"] for o in outcomes if o["name"] == "Over" and o["point"] == LINHA_ALVO),
        None,
    )
    odd_under = next(
        (o["price"] for o in outcomes if o["name"] == "Under" and o["point"] == LINHA_ALVO),
        None,
    )
    if odd_over is None or odd_under is None:
        return None

    return OddsOverUnder(odd_over=odd_over, odd_under=odd_under)
