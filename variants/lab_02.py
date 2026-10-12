"""Лабораторна SIS-LAB02. Задача 2: Тайм-аут і дедлайн.

Правила — у student.md (розділ 7, задача 2) та в картці вашого варіанта.
Відкриті тести: pytest tests/test_lab_02.py
"""


class DeadlineExceeded(Exception):
    """Дедлайн вичерпано."""


def effective_timeout(remaining: float, per_call: float, reserve: float = 0.0) -> float:
    """Тайм-аут одного виклику з урахуванням залишку часу й резерву."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


class Deadline:
    """Абсолютний момент, до якого відповідь ще корисна."""

    def __init__(self, clock, budget: float):
        raise NotImplementedError  # TODO: реалізуйте за описом задачі

    def remaining(self) -> float:
        raise NotImplementedError  # TODO

    def expired(self) -> bool:
        raise NotImplementedError  # TODO

    def check(self) -> None:
        raise NotImplementedError  # TODO

    def timeout_for(self, per_call: float) -> float:
        raise NotImplementedError  # TODO


def split_budget(total: float, weights: list[float], reserve: float = 0.0) -> list[float]:
    """Ділить час між кроками ланцюжка пропорційно вагам."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
