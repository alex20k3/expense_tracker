FAIRNESS_BY_INCOME = {
    "low": 0.7,     # мало зарабатывает → платит меньше
    "medium": 1.0,
    "high": 1.3     # много зарабатывает → платит больше
}

KARMA_FOR_PROMPT_SETTLE = 5
KARMA_FOR_CREATE_EXPENSE = 2


def income_to_coeff(income_category: str) -> float:
    return FAIRNESS_BY_INCOME.get(income_category, 1.0)
