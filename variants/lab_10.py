"""Лабораторна SIS-LAB02. Задача 10: Аналіз експерименту і вибір параметрів.

Правила — у student.md (розділ 7, задача 10) та в картці вашого варіанта.
Відкриті тести: pytest tests/test_lab_10.py
"""


def summarize_log(events):
    """Підсумок журналу подій (час, вид)."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def retry_amplification(layers):
    """Добуток кількостей спроб усіх шарів."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def amplified_rps(rps, layers):
    """Навантаження на нижній сервіс у найгіршому випадку."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def worst_case_wait(attempts, per_call_timeout, base, factor, cap):
    """Найдовше очікування відповіді."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def max_attempts_for_budget(budget, per_call_timeout, base, factor, cap):
    """Найбільша кількість спроб, що вкладається в бюджет."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
