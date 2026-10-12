"""Лабораторна SIS-LAB02. Задача 1: Мережа з несправностями між двома сервісами.

Правила — у student.md (розділ 7, задача 1) та в картці вашого варіанта.
Відкриті тести: pytest tests/test_lab_01.py
"""


class ServiceUnavailable(Exception):
    """Сервіс відповів помилкою 503."""


class CallTimeout(Exception):
    """Відповідь не прийшла за відведений час."""


class FaultyLink:
    """Канал між клієнтом і сервісом, що псує виклики за розкладом schedule(index, now) -> (kind, latency)."""

    def __init__(self, clock, service, schedule):
        raise NotImplementedError  # TODO: збережіть параметри, заведіть лічильники index, processed і журнал log

    def call(self, request, timeout=None):
        """Виконує один виклик за правилами задачі 1."""
        raise NotImplementedError  # TODO: реалізуйте за описом задачі
