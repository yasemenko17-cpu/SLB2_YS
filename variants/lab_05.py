"""Лабораторна SIS-LAB02. Задача 5: Повторні спроби з обмеженнями.

Правила — у student.md (розділ 7, задача 5) та в картці вашого варіанта.
Відкриті тести: pytest tests/test_lab_05.py
"""


class TransientError(Exception):
    """Тимчасова помилка; необов'язковий атрибут retry_after (секунди)."""

    def __init__(self, message="", retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after


class PermanentError(Exception):
    """Постійна помилка: повтор безглуздий."""


class RetryGaveUp(Exception):
    """Повторні спроби припинено."""


def retry_call(op, clock, rng, max_attempts=3, base=0.1, factor=2.0, cap=2.0, jitter="none", budget=None):
    """Повертає (результат, кількість спроб)."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
