from __future__ import annotations

EV_MINIMO_ALERTA = 0.02


def odd_minima_para_ev_positivo(prob_justa: float, comissao_betfair: float) -> float:
    """Odd de equilíbrio na Betfair, líquida de comissão, para EV = 0.

    A comissão da Betfair incide sobre o lucro líquido (odd - 1), não sobre a odd
    bruta, então o retorno líquido de uma aposta vencedora é
    1 + (odd - 1) * (1 - comissao). Isolando a odd bruta que deixa o EV em zero:
    """
    retorno_liquido_necessario = 1 / prob_justa
    lucro_liquido_necessario = retorno_liquido_necessario - 1
    lucro_bruto_necessario = lucro_liquido_necessario / (1 - comissao_betfair)
    return 1 + lucro_bruto_necessario


def calcular_ev(prob_justa: float, odd_betfair: float, comissao_betfair: float) -> float:
    lucro_bruto = odd_betfair - 1
    lucro_liquido = lucro_bruto * (1 - comissao_betfair)
    retorno_liquido = 1 + lucro_liquido
    return prob_justa * retorno_liquido - 1


def passa_piso_minimo(ev: float, piso: float = EV_MINIMO_ALERTA) -> bool:
    return ev > piso
