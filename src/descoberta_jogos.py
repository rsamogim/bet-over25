from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv

import config
import database
import odds_client


def descobrir_jogos_do_dia() -> int:
    load_dotenv()
    conn = database.get_connection()
    hoje = datetime.now(ZoneInfo(config.FUSO_BRASILIA)).date().isoformat()

    total = 0
    for sport_key, nome_liga in config.LIGAS_COBERTAS.items():
        eventos = odds_client.listar_eventos(sport_key)
        for evento in eventos:
            horario_utc = datetime.fromisoformat(evento.commence_time_utc.replace("Z", "+00:00"))
            horario_brasilia = horario_utc.astimezone(ZoneInfo(config.FUSO_BRASILIA))
            database.upsert_jogo(
                conn,
                id_partida=evento.id_partida,
                liga_sport_key=sport_key,
                competicao=nome_liga,
                time_casa=evento.time_casa,
                time_fora=evento.time_fora,
                horario_inicio_brasilia=horario_brasilia.isoformat(),
                data_descoberta=hoje,
            )
            total += 1
        print(f"{nome_liga}: {len(eventos)} jogo(s) encontrado(s)")

    print(f"Total: {total} jogo(s) salvos em jogos_do_dia (data_descoberta={hoje})")
    return total


if __name__ == "__main__":
    descobrir_jogos_do_dia()
