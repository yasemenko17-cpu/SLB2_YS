"""Лабораторна SIS-LAB02. Задача 6: Автоматичний вимикач (Circuit Breaker).

Правила — у student.md (розділ 7, задача 6) та в картці вашого варіанта.
Відкриті тести: pytest tests/test_lab_06.py
"""


class CircuitOpenError(Exception):
    """Вимикач розімкнений: виклик не дійшов до сервісу."""


class CircuitBreaker:
    CLOSED, OPEN, HALF_OPEN = "Closed", "Open", "Half-Open"

    def __init__(self, clock, failure_threshold=3, open_timeout=10.0, success_threshold=2):
        raise NotImplementedError  # TODO: збережіть параметри; заведіть state, лічильники й журнал log

    def call(self, fn):
        """Виконує fn() під захистом вимикача."""
        raise NotImplementedError  # TODO: реалізуйте за описом задачі
