import pytest

import ev_calculator


def test_odd_minima_bate_com_conta_na_mao():
    # prob justa 50%, comissão 6,5% -> retorno líquido necessário = 2.0
    # lucro líquido necessário = 1.0 -> lucro bruto = 1.0 / 0.935 = 1.069518...
    # odd mínima = 1 + 1.069518... = 2.069518...
    odd_minima = ev_calculator.odd_minima_para_ev_positivo(0.5, 0.065)
    assert odd_minima == pytest.approx(2.0695187165775404, abs=1e-9)


def test_ev_na_odd_minima_e_zero():
    prob_justa = 0.5
    comissao = 0.065
    odd_minima = ev_calculator.odd_minima_para_ev_positivo(prob_justa, comissao)
    ev = ev_calculator.calcular_ev(prob_justa, odd_minima, comissao)
    assert ev == pytest.approx(0.0, abs=1e-9)


def test_ev_positivo_acima_da_odd_minima():
    ev = ev_calculator.calcular_ev(prob_justa=0.5, odd_betfair=2.20, comissao_betfair=0.065)
    assert ev == pytest.approx(0.061, abs=1e-3)
    assert ev > 0


def test_ev_negativo_abaixo_da_odd_minima():
    ev = ev_calculator.calcular_ev(prob_justa=0.5, odd_betfair=1.90, comissao_betfair=0.065)
    assert ev < 0


def test_piso_minimo_filtra_ev_baixo():
    assert not ev_calculator.passa_piso_minimo(0.01, piso=0.02)
    assert ev_calculator.passa_piso_minimo(0.05, piso=0.02)
