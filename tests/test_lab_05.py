"""Відкриті тести задачі 5: Повторні спроби з обмеженнями.

Запуск: pytest tests/test_lab_05.py
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


T05 = [('S1', 'retry', [['ok:A'], {}, [0.5]], {'outcome': ['ok', 'A', 1], 'calls': 1, 'now': 0.0}),
 ('S1', 'retry', [['T', 'T', 'ok:B'], {}, [0.5]], {'outcome': ['ok', 'B', 3], 'calls': 3, 'now': 0.3}),
 ('S1',
  'retry',
  [['T', 'T', 'ok:B'], {'max_attempts': 2}, [0.5]],
  {'outcome': ['!RetryGaveUp', 'Вичерпано спроб: 2'], 'calls': 2, 'now': 0.1}),
 ('S2', 'retry', [['P'], {}, [0.5]], {'outcome': ['!PermanentError', 'помилка'], 'calls': 1, 'now': 0.0}),
 ('S2',
  'retry',
  [['T', 'P', 'ok:X'], {}, [0.5]],
  {'outcome': ['!PermanentError', 'помилка'], 'calls': 2, 'now': 0.1}),
 ('S2',
  'retry',
  [['T', 'T', 'ok:F'], {'base': 1.0, 'factor': 2.0, 'cap': 10.0, 'jitter': 'full'}, [0.5, 0.25]],
  {'outcome': ['ok', 'F', 3], 'calls': 3, 'now': 1.0}),
 ('S3',
  'retry',
  [['T', 'T', 'ok:Z'], {'base': 1.0, 'budget': 3.0}, [0.5]],
  {'outcome': ['ok', 'Z', 3], 'calls': 3, 'now': 3.0}),
 ('S3',
  'retry',
  [['T', 'T', 'T', 'ok:Z'], {'max_attempts': 5, 'base': 1.0, 'budget': 2.5}, [0.5]],
  {'outcome': ['!RetryGaveUp', 'Бюджет 2.5 с вичерпано'], 'calls': 2, 'now': 1.0}),
 ('S3', 'retry', [['T:5', 'ok:R'], {'base': 1.0}, [0.5]], {'outcome': ['ok', 'R', 2], 'calls': 2, 'now': 5.0})]


@pytest.mark.parametrize("tag,drv,args,expected", T05, ids=_ids(T05, "T05"))
def test_task_05(tag, drv, args, expected):
    run(5, drv, args, expected)
