# backend/app/utils.py

# сколько кармы даём за действия
KARMA_FOR_CREATE_EXPENSE = 5
KARMA_FOR_PROMPT_SETTLE = 3

# коэффициенты справедливости по категории дохода
FAIRNESS_COEFFS = {
    "low": 0.7,     # низкий доход
    "medium": 1.0,   # средний доход
    "high": 1.5,    # высокий доход
}


def get_fairness_coeff_for_income(income_category: str) -> float:
    """
    Вернуть коэффициент справедливости по категории дохода.
    Если прилетело что-то неизвестное - считаем как средний доход (1.0).
    """
    return FAIRNESS_COEFFS.get(income_category, 1.0)


from datetime import datetime
from typing import Optional

def deadline_karma_delta(due_date: datetime, now: Optional[datetime] = None) -> int:
    now = now or datetime.utcnow()
    days_left = (due_date.date() - now.date()).days
    return days_left

def apply_negative_karma_penalty(user) -> None:
    """
    За каждые -10 кармы повышаем коэффициент на 0.1 и возвращаем карму на +10,
    чтобы штраф применялся дискретно, а не бесконечно.
    """
    while user.karma_points <= -10:
        user.fairness_coeff = (user.fairness_coeff or 1.0) + 0.1
        user.karma_points += 10
