"""Лабораторна SIS-LAB02. Задача 7: Вимикач за часткою збоїв у ковзному вікні.

Правила — у student.md (розділ 7, задача 7) та в картці вашого варіанта.
Відкриті тести: pytest tests/test_lab_07.py
"""


class CircuitOpenError(Exception):
    """Вимикач розімкнений: виклик не дійшов до сервісу."""


class WindowBreaker:
    CLOSED, OPEN, HALF_OPEN = "Closed", "Open", "Half-Open"

    def __init__(self, clock, window=10, min_calls=5, failure_rate=0.5, open_timeout=10.0,
                 probe_calls=2, slow_threshold=None):
        raise NotImplementedError  # TODO: збережіть параметри; заведіть state і вікно результатів

    def call(self, fn):
        """Виконує fn() під захистом вимикача."""
        raise NotImplementedError  # TODO: реалізуйте за описом задачі
