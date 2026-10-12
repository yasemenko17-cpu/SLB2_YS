"""Відкриті тести задачі 3: Тимчасові й постійні помилки, ідемпотентність.

Запуск: pytest tests/test_lab_03.py
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


T03 = [('S1', 'status', [200], 'ok'),
 ('S1', 'status', [204], 'ok'),
 ('S1', 'status', [301], 'ok'),
 ('S2', 'retryable', ['GET', 'transient', None], True),
 ('S2', 'retryable', ['get', 'timeout', None], True),
 ('S2', 'retryable', ['POST', 'timeout', None], False),
 ('S3', 'after', ['30', 1.0], 30.0),
 ('S3', 'after', [' 7 ', 1.0], 7.0),
 ('S3', 'after', [None, 2.5], 2.5)]


@pytest.mark.parametrize("tag,drv,args,expected", T03, ids=_ids(T03, "T03"))
def test_task_03(tag, drv, args, expected):
    run(3, drv, args, expected)
