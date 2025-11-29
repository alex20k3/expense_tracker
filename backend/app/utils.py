# backend/app/utils.py

# сколько кармы даём за действия
KARMA_FOR_CREATE_EXPENSE = 5
KARMA_FOR_PROMPT_SETTLE = 3

# коэффициенты справедливости по категории дохода
FAIRNESS_COEFFS = {
    "low": 0.75,     # низкий доход
    "medium": 1.0,   # средний доход
    "high": 1.25,    # высокий доход
}


def get_fairness_coeff_for_income(income_category: str) -> float:
    """
    Вернуть коэффициент справедливости по категории дохода.
    Если прилетело что-то неизвестное - считаем как средний доход (1.0).
    """
    return FAIRNESS_COEFFS.get(income_category, 1.0)
