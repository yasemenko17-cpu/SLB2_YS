"""Відкриті тести задачі 4: Експоненційна затримка і джитер.

Запуск: pytest tests/test_lab_04.py
Тут лише приклади з карток варіантів; повний набір перевірок є у викладача.
"""
import signal

import pytest
from conftest import load
from support import DRIVERS


def _same(a, b):
    """Рівність із допуском для дробових чисел; список і кортеж вважаються однаковими послідовностями."""
    if isinstance(a, float) or isinstance(b, float):
        return isinstance(a, (int, float)) and isinstance(b, (int, float)) and abs(a - b) < 1e-9
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_same(a[k], b[k]) for k in a)
    return a == b


def run(task, drv, args, expected):
    """Запускає драйвер на вашому модулі. Помилки подано як ("!КласПомилки", "повідомлення")."""
    got = DRIVERS[drv](load(task), *args)
    assert _same(got, expected), f"отримано {got!r}, очікувалось {expected!r}"


def _ids(cases, prefix):
    return [f"{prefix}-{c[0]}-{i}" for i, c in enumerate(cases)]


@pytest.fixture(autouse=True)
def _watchdog():
    """Тест, що завис (нескінченний цикл), завершується за 10 с."""
    def boom(signum, frame):
        raise TimeoutError("тест завис довше 10 с: перевірте умови завершення циклів")
    old = signal.signal(signal.SIGALRM, boom)
    signal.alarm(10)
    yield
    signal.alarm(0)
    signal.signal(signal.SIGALRM, old)


T04 = [('S1', 'delays', [5, 0.1, 2.0, 10.0], [0.1, 0.2, 0.4, 0.8, 1.6]),
 ('S1', 'delays', [6, 0.5, 2.0, 4.0], [0.5, 1.0, 2.0, 4.0, 4.0, 4.0]),
 ('S1', 'delays', [3, 1.0, 1.0, 5.0], [1.0, 1.0, 1.0]),
 ('S2', 'jitter', [1, 1.0, 2.0, 30.0, 'none', [0.5]], 1.0),
 ('S2', 'jitter', [3, 1.0, 2.0, 30.0, 'none', [0.5]], 4.0),
 ('S2', 'jitter', [3, 1.0, 2.0, 30.0, 'full', [0.25]], 1.0),
 ('S3', 'decor', [3, 1.0, 100.0, [0.0, 0.0, 0.0]], [1.0, 1.0, 1.0]),
 ('S3', 'decor', [3, 1.0, 100.0, [1.0, 1.0, 1.0]], [3.0, 9.0, 27.0]),
 ('S3', 'decor', [4, 1.0, 10.0, [0.5]], [2.0, 3.5, 5.75, 9.125])]


@pytest.mark.parametrize("tag,drv,args,expected", T04, ids=_ids(T04, "T04"))
def test_task_04(tag, drv, args, expected):
    run(4, drv, args, expected)
