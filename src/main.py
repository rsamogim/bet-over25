from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv

import config
import database
import devig
import ev_calculator
import odds_client
import telegram_notifier


def _minutos_ate_inicio(horario_inicio_brasilia: str, agora: datetime) -> float:
    horario = datetime.fromisoformat(horario_inicio_brasilia)
    return (horario - agora).total_seconds() / 60


def checar_e_alertar() -> int:
    load_dotenv()
    conn = database.get_connection()
    agora = datetime.now(ZoneInfo(config.FUSO_BRASILIA))
    hoje = agora.date().isoformat()
    comissao = float(os.environ.get("BETFAIR_COMMISSION", "0"))

    jogos = database.get_jogos_do_dia(conn, hoje)
    jogos_na_janela = [
        jogo
        for jogo in jogos
        if config.JANELA_GATILHO_MINUTOS_MIN
        <= _minutos_ate_inicio(jogo["horario_inicio_brasilia"], agora)
        <= config.JANELA_GATILHO_MINUTOS_MAX
    ]

    print(f"{len(jogos)} jogo(s) em jogos_do_dia, {len(jogos_na_janela)} na janela de gatilho")

    alertas_enviados = 0
    for jogo in jogos_na_janela:
        odds = odds_client.buscar_odds_pinnacle_2_5(jogo["liga_sport_key"], jogo["id_partida"])
        if odds is None:
            print(f"sem odds Pinnacle na linha 2,5 pra {jogo['time_casa']} x {jogo['time_fora']}")
            continue

        try:
            resultado = devig.devig_over_under_2_5(odds.odd_over, odds.odd_under)
        except ValueError as erro:
            print(f"devig falhou pra {jogo['time_casa']} x {jogo['time_fora']}: {erro}")
            continue

        odd_minima_over = ev_calculator.odd_minima_para_ev_positivo(resultado.prob_over_2_5, comissao)
        odd_minima_under = ev_calculator.odd_minima_para_ev_positivo(resultado.prob_under_2_5, comissao)

        if not database.deve_alertar(conn, jogo["id_partida"], config.MERCADO_OVER_UNDER_2_5, odd_minima_over):
            print(f"jogo {jogo['time_casa']} x {jogo['time_fora']} já alertado, pulando (dedup)")
            continue

        mensagem = telegram_notifier.montar_mensagem(
            competicao=jogo["competicao"],
            time_casa=jogo["time_casa"],
            time_fora=jogo["time_fora"],
            horario_brasilia=jogo["horario_inicio_brasilia"],
            xg_total=resultado.expected_goals,
            prob_over=resultado.prob_over_2_5,
            prob_under=resultado.prob_under_2_5,
            odd_minima_over=odd_minima_over,
            odd_minima_under=odd_minima_under,
            comissao=comissao,
        )
        telegram_notifier.enviar_alerta(mensagem)

        database.registrar_alerta(
            conn,
            id_partida=jogo["id_partida"],
            mercado=config.MERCADO_OVER_UNDER_2_5,
            odd_minima=odd_minima_over,
            probabilidade_justa_over=resultado.prob_over_2_5,
            enviado_em=agora.isoformat(),
        )
        alertas_enviados += 1
        print(f"alerta enviado: {jogo['time_casa']} x {jogo['time_fora']}")

    print(f"{alertas_enviados} alerta(s) enviado(s)")
    return alertas_enviados


if __name__ == "__main__":
    checar_e_alertar()
