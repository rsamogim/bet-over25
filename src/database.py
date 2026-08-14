from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "alertas.db"

VARIACAO_ODD_MINIMA_PARA_REALERTAR = 0.05

_SCHEMA = """
CREATE TABLE IF NOT EXISTS jogos_do_dia (
    id_partida TEXT PRIMARY KEY,
    liga_sport_key TEXT NOT NULL,
    competicao TEXT NOT NULL,
    time_casa TEXT NOT NULL,
    time_fora TEXT NOT NULL,
    horario_inicio_brasilia TEXT NOT NULL,
    data_descoberta TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS alertas_enviados (
    id_partida TEXT NOT NULL,
    mercado TEXT NOT NULL,
    odd_minima REAL NOT NULL,
    probabilidade_justa_over REAL NOT NULL,
    enviado_em TEXT NOT NULL,
    PRIMARY KEY (id_partida, mercado)
);
"""


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    return conn


def upsert_jogo(
    conn: sqlite3.Connection,
    id_partida: str,
    liga_sport_key: str,
    competicao: str,
    time_casa: str,
    time_fora: str,
    horario_inicio_brasilia: str,
    data_descoberta: str,
) -> None:
    conn.execute(
        """
        INSERT INTO jogos_do_dia
            (id_partida, liga_sport_key, competicao, time_casa, time_fora, horario_inicio_brasilia, data_descoberta)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id_partida) DO UPDATE SET
            liga_sport_key=excluded.liga_sport_key,
            competicao=excluded.competicao,
            time_casa=excluded.time_casa,
            time_fora=excluded.time_fora,
            horario_inicio_brasilia=excluded.horario_inicio_brasilia,
            data_descoberta=excluded.data_descoberta
        """,
        (id_partida, liga_sport_key, competicao, time_casa, time_fora, horario_inicio_brasilia, data_descoberta),
    )
    conn.commit()


def get_jogos_do_dia(conn: sqlite3.Connection, data_descoberta: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM jogos_do_dia WHERE data_descoberta = ?",
        (data_descoberta,),
    ).fetchall()


def deve_alertar(
    conn: sqlite3.Connection,
    id_partida: str,
    mercado: str,
    odd_minima: float,
    limiar_variacao: float = VARIACAO_ODD_MINIMA_PARA_REALERTAR,
) -> bool:
    row = conn.execute(
        "SELECT odd_minima FROM alertas_enviados WHERE id_partida = ? AND mercado = ?",
        (id_partida, mercado),
    ).fetchone()
    if row is None:
        return True
    return abs(odd_minima - row["odd_minima"]) > limiar_variacao


def registrar_alerta(
    conn: sqlite3.Connection,
    id_partida: str,
    mercado: str,
    odd_minima: float,
    probabilidade_justa_over: float,
    enviado_em: str,
) -> None:
    conn.execute(
        """
        INSERT INTO alertas_enviados
            (id_partida, mercado, odd_minima, probabilidade_justa_over, enviado_em)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id_partida, mercado) DO UPDATE SET
            odd_minima=excluded.odd_minima,
            probabilidade_justa_over=excluded.probabilidade_justa_over,
            enviado_em=excluded.enviado_em
        """,
        (id_partida, mercado, odd_minima, probabilidade_justa_over, enviado_em),
    )
    conn.commit()
