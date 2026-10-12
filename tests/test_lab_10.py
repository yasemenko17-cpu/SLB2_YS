"""Відкриті тести задачі 10: Аналіз експерименту і вибір параметрів.

Запуск: pytest tests/test_lab_10.py
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


T10 = [('S1',
  'summary',
  [[(0, 'ok'), (1, 'ok'), (2, 'error'), (3, 'timeout')]],
  {'total': 4, 'ok': 2, 'failed': 2, 'rejected': 0, 'reached_service': 4, 'success_rate': 0.5}),
 ('S1',
  'summary',
  [[(0, 'rejected'), (0, 'rejected'), (0, 'rejected'), (5, 'ok')]],
  {'total': 4, 'ok': 1, 'failed': 0, 'rejected': 3, 'reached_service': 1, 'success_rate': 0.25}),
 ('S1',
  'summary',
  [[(0, 'ok'), (0, 'ok'), (0, 'ok'), (0, 'ok'), (0, 'ok'), (0, 'ok'), (0, 'ok')]],
  {'total': 7, 'ok': 7, 'failed': 0, 'rejected': 0, 'reached_service': 7, 'success_rate': 1.0}),
 ('S2', 'amp', [[4, 4, 4]], 64),
 ('S2', 'amp', [[3]], 3),
 ('S2', 'amp', [[1, 1]], 1),
 ('S3', 'wcw', [1, 2.0, 0.1, 2.0, 1.0], 2.0),
 ('S3', 'wcw', [4, 2.0, 0.5, 2.0, 10.0], 11.5),
 ('S3', 'wcw', [5, 1.0, 1.0, 2.0, 3.0], 14.0)]


@pytest.mark.parametrize("tag,drv,args,expected", T10, ids=_ids(T10, "T10"))
def test_task_10(tag, drv, args, expected):
    run(10, drv, args, expected)
