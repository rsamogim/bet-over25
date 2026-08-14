import pytest
import shin
from scipy.stats import poisson

import devig


def test_shin_bate_com_exemplo_documentado_binario():
    probs = shin.calculate_implied_probabilities([1.5, 2.74])
    assert probs[0] == pytest.approx(0.6508515815085157, abs=1e-9)
    assert probs[1] == pytest.approx(0.3491484184914841, abs=1e-9)


def test_shin_bate_com_exemplo_documentado_tres_vias():
    probs = shin.calculate_implied_probabilities([2.6, 2.4, 4.3])
    assert probs[0] == pytest.approx(0.37299406033208965, abs=1e-9)
    assert probs[1] == pytest.approx(0.4047794109200184, abs=1e-9)
    assert probs[2] == pytest.approx(0.2222265287474275, abs=1e-9)


def test_devig_over_under_2_5_retorna_resultado_consistente():
    resultado = devig.devig_over_under_2_5(1.99, 1.86)

    assert 0 < resultado.prob_over_2_5 < 1
    assert 0 < resultado.prob_under_2_5 < 1
    assert resultado.prob_over_2_5 + resultado.prob_under_2_5 == pytest.approx(1.0, abs=1e-9)
    assert resultado.expected_goals > 0


def test_lambda_encontrado_bate_com_poisson_cdf():
    resultado = devig.devig_over_under_2_5(1.99, 1.86)
    prob_under_recalculada = poisson.cdf(2, resultado.expected_goals)
    assert prob_under_recalculada == pytest.approx(resultado.prob_under_2_5, abs=1e-6)


def test_monte_carlo_bate_com_analitico():
    resultado = devig.devig_over_under_2_5(1.99, 1.86)
    assert abs(resultado.monte_carlo_prob_under_2_5 - resultado.prob_under_2_5) < devig.MONTE_CARLO_TOLERANCE
