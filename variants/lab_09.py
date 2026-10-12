"""Лабораторна SIS-LAB02. Задача 9: Часткові відмови і деградація.

Правила — у student.md (розділ 7, задача 9) та в картці вашого варіанта.
Відкриті тести: pytest tests/test_lab_09.py
"""


def get_with_fallback(key, fetch, cache, clock, ttl, stale_ttl):
    """Кеш зі «застарілою» відповіддю на випадок збою. Повертає (значення, джерело)."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def build_order_view(order_id, orders, catalogue, recommendations):
    """Подання замовлення з необов'язковими частинами."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def health_report(results, critical):
    """Стан сервісів за часткою успішних викликів."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
