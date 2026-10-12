"""Відкриті тести задачі 2: Тайм-аут і дедлайн.

Запуск: pytest tests/test_lab_02.py
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


T02 = [('S1', 'eff', [10.0, 3.0, 0.0], 3.0),
 ('S1', 'eff', [2.0, 3.0, 0.0], 2.0),
 ('S1', 'eff', [10.0, 3.0, 8.0], 2.0),
 ('S2',
  'deadline',
  [10.0,
   [('remaining',), ('sleep', 4.0), ('remaining',), ('expired',), ('sleep', 6.0), ('remaining',), ('expired',)]],
  [10.0, 6.0, False, 0.0, True]),
 ('S2', 'deadline', [5.0, [('timeout_for', 2.0), ('sleep', 4.0), ('timeout_for', 2.0)]], [2.0, 1.0]),
 ('S2',
  'deadline',
  [5.0, [('check',), ('sleep', 7.0), ('check',), ('timeout_for', 1.0)]],
  ['ok', ('!DeadlineExceeded', 'Дедлайн вичерпано'), ('!DeadlineExceeded', 'Дедлайн вичерпано')]),
 ('S3', 'split', [10.0, [1, 1], 0.0], [5.0, 5.0]),
 ('S3', 'split', [10.0, [1, 2, 2], 0.0], [2.0, 4.0, 4.0]),
 ('S3', 'split', [10.0, [3, 1], 2.0], [6.0, 2.0])]


@pytest.mark.parametrize("tag,drv,args,expected", T02, ids=_ids(T02, "T02"))
def test_task_02(tag, drv, args, expected):
    run(2, drv, args, expected)
