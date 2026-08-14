import database


def _conn(tmp_path):
    return database.get_connection(tmp_path / "alertas_teste.db")


def test_upsert_e_leitura_jogos_do_dia(tmp_path):
    conn = _conn(tmp_path)
    database.upsert_jogo(
        conn,
        id_partida="evt1",
        liga_sport_key="soccer_brazil_campeonato",
        competicao="Brasileirão Série A",
        time_casa="Fluminense",
        time_fora="Palmeiras",
        horario_inicio_brasilia="2026-08-15T16:30:00-03:00",
        data_descoberta="2026-08-14",
    )
    jogos = database.get_jogos_do_dia(conn, "2026-08-14")
    assert len(jogos) == 1
    assert jogos[0]["time_casa"] == "Fluminense"


def test_deve_alertar_primeira_vez_e_true(tmp_path):
    conn = _conn(tmp_path)
    assert database.deve_alertar(conn, "evt1", "over_under_2_5", 2.10) is True


def test_dedup_nao_alerta_de_novo_sem_variacao_significativa(tmp_path):
    conn = _conn(tmp_path)
    database.registrar_alerta(conn, "evt1", "over_under_2_5", 2.10, 0.48, "2026-08-14T18:00:00-03:00")
    assert database.deve_alertar(conn, "evt1", "over_under_2_5", 2.11) is False


def test_realerta_quando_odd_minima_varia_significativamente(tmp_path):
    conn = _conn(tmp_path)
    database.registrar_alerta(conn, "evt1", "over_under_2_5", 2.10, 0.48, "2026-08-14T18:00:00-03:00")
    assert database.deve_alertar(conn, "evt1", "over_under_2_5", 2.30) is True
