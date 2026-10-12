"""Лабораторна SIS-LAB02. Задача 8: Повтори, вимикач і запасна відповідь разом.

Правила — у student.md (розділ 7, задача 8) та в картці вашого варіанта.
Відкриті тести: pytest tests/test_lab_08.py
"""


class CircuitOpenError(Exception):
    """Вимикач розімкнений."""


class TransientError(Exception):
    """Тимчасова помилка."""


class PermanentError(Exception):
    """Постійна помилка."""


class RetryGaveUp(Exception):
    """Спроби вичерпано."""


def resilient_call(op, breaker, clock, max_attempts=3, base=0.1, factor=2.0, cap=2.0, fallback=None):
    """Повертає (значення, {"attempts": ..., "source": ..., "reason": ...})."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
