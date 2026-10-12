"""Лабораторна SIS-LAB02. Задача 3: Тимчасові й постійні помилки, ідемпотентність.

Правила — у student.md (розділ 7, задача 3) та в картці вашого варіанта.
Відкриті тести: pytest tests/test_lab_03.py
"""


def classify_status(code: int) -> str:
    """"ok", "transient" або "permanent" за кодом відповіді HTTP."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def is_retryable(method: str, outcome: str, idempotency_key: str | None = None) -> bool:
    """Чи можна безпечно повторити запит."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def parse_retry_after(value: str | None, default: float) -> float:
    """Секунди очікування із заголовка Retry-After."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
