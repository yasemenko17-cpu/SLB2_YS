"""Лабораторна SIS-LAB02. Задача 4: Експоненційна затримка і джитер.

Правила — у student.md (розділ 7, задача 4) та в картці вашого варіанта.
Відкриті тести: pytest tests/test_lab_04.py
"""


def backoff_delays(n: int, base: float, factor: float, cap: float) -> list[float]:
    """Верхні межі пауз перед повторами 1..n."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def jittered_delay(attempt: int, base: float, factor: float, cap: float, mode: str, rng) -> float:
    """Пауза після невдалої спроби у режимі none, full або equal."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def decorrelated_delays(n: int, base: float, cap: float, rng) -> list[float]:
    """Декорельований джитер."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
