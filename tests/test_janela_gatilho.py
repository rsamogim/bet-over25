from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import config
import main


def test_jogo_60_min_a_frente_esta_na_janela():
    agora = datetime(2026, 8, 15, 18, 0, 0, tzinfo=ZoneInfo(config.FUSO_BRASILIA))
    horario_jogo = (agora + timedelta(minutes=60)).isoformat()
    minutos = main._minutos_ate_inicio(horario_jogo, agora)
    assert config.JANELA_GATILHO_MINUTOS_MIN <= minutos <= config.JANELA_GATILHO_MINUTOS_MAX


def test_jogo_3_horas_a_frente_fica_fora_da_janela():
    agora = datetime(2026, 8, 15, 18, 0, 0, tzinfo=ZoneInfo(config.FUSO_BRASILIA))
    horario_jogo = (agora + timedelta(hours=3)).isoformat()
    minutos = main._minutos_ate_inicio(horario_jogo, agora)
    assert not (config.JANELA_GATILHO_MINUTOS_MIN <= minutos <= config.JANELA_GATILHO_MINUTOS_MAX)


def test_jogo_ja_comecado_fica_fora_da_janela():
    agora = datetime(2026, 8, 15, 18, 0, 0, tzinfo=ZoneInfo(config.FUSO_BRASILIA))
    horario_jogo = (agora - timedelta(minutes=10)).isoformat()
    minutos = main._minutos_ate_inicio(horario_jogo, agora)
    assert not (config.JANELA_GATILHO_MINUTOS_MIN <= minutos <= config.JANELA_GATILHO_MINUTOS_MAX)


def test_conversao_utc_para_brasilia():
    # 2026-08-15T19:30:00Z (UTC) deve virar 16:30 em horário de Brasília (UTC-3)
    horario_utc = datetime.fromisoformat("2026-08-15T19:30:00Z".replace("Z", "+00:00"))
    horario_brasilia = horario_utc.astimezone(ZoneInfo(config.FUSO_BRASILIA))
    assert horario_brasilia.hour == 16
    assert horario_brasilia.minute == 30
    assert horario_brasilia.utcoffset() == timedelta(hours=-3)
