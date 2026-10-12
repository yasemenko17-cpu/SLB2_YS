"""Відкриті тести задачі 6: Автоматичний вимикач (Circuit Breaker).

Запуск: pytest tests/test_lab_06.py
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


T06 = [('S1',
  'breaker',
  ['CircuitBreaker',
   {'failure_threshold': 3, 'open_timeout': 10.0, 'success_threshold': 2},
   [('call', 'ok'),
    ('call', 'fail'),
    ('call', 'fail'),
    ('call', 'ok'),
    ('call', 'fail'),
    ('call', 'fail'),
    ('state',)]],
  {'trace': ['ok', 'fail', 'fail', 'ok', 'fail', 'fail', 'Closed'],
   'state': 'Closed',
   'service_calls': 6,
   'log': []}),
 ('S1',
  'breaker',
  ['CircuitBreaker',
   {'failure_threshold': 3, 'open_timeout': 10.0, 'success_threshold': 2},
   [('call', 'fail'), ('call', 'fail'), ('call', 'fail'), ('state',), ('call', 'ok'), ('call', 'ok')]],
  {'trace': ['fail', 'fail', 'fail', 'Open', 'open', 'open'],
   'state': 'Open',
   'service_calls': 3,
   'log': [(0.0, 'Closed', 'Open')]}),
 ('S1',
  'breaker',
  ['CircuitBreaker',
   {'failure_threshold': 1, 'open_timeout': 5.0, 'success_threshold': 1},
   [('call', 'fail'), ('call', 'ok'), ('call', 'ok')]],
  {'trace': ['fail', 'open', 'open'], 'state': 'Open', 'service_calls': 1, 'log': [(0.0, 'Closed', 'Open')]}),
 ('S2',
  'breaker',
  ['CircuitBreaker',
   {'failure_threshold': 3, 'open_timeout': 10.0, 'success_threshold': 2},
   [('call', 'fail'),
    ('call', 'fail'),
    ('call', 'fail'),
    ('advance', 9.9),
    ('call', 'ok'),
    ('advance', 0.1),
    ('call', 'ok'),
    ('state',),
    ('call', 'ok'),
    ('state',)]],
  {'trace': ['fail', 'fail', 'fail', 'open', 'ok', 'Half-Open', 'ok', 'Closed'],
   'state': 'Closed',
   'service_calls': 5,
   'log': [(0.0, 'Closed', 'Open'), (10.0, 'Open', 'Half-Open'), (10.0, 'Half-Open', 'Closed')]}),
 ('S2',
  'breaker',
  ['CircuitBreaker',
   {'failure_threshold': 3, 'open_timeout': 10.0, 'success_threshold': 2},
   [('call', 'fail'),
    ('call', 'fail'),
    ('call', 'fail'),
    ('advance', 10.0),
    ('call', 'ok'),
    ('call', 'ok'),
    ('call', 'fail'),
    ('state',)]],
  {'trace': ['fail', 'fail', 'fail', 'ok', 'ok', 'fail', 'Closed'],
   'state': 'Closed',
   'service_calls': 6,
   'log': [(0.0, 'Closed', 'Open'), (10.0, 'Open', 'Half-Open'), (10.0, 'Half-Open', 'Closed')]}),
 ('S2',
  'breaker',
  ['CircuitBreaker',
   {'failure_threshold': 2, 'open_timeout': 3.0, 'success_threshold': 1},
   [('call', 'fail'), ('call', 'fail'), ('advance', 3.0), ('call', 'ok'), ('state',)]],
  {'trace': ['fail', 'fail', 'ok', 'Closed'],
   'state': 'Closed',
   'service_calls': 3,
   'log': [(0.0, 'Closed', 'Open'), (3.0, 'Open', 'Half-Open'), (3.0, 'Half-Open', 'Closed')]}),
 ('S3',
  'breaker',
  ['CircuitBreaker',
   {'failure_threshold': 3, 'open_timeout': 10.0, 'success_threshold': 2},
   [('call', 'fail'),
    ('call', 'fail'),
    ('call', 'fail'),
    ('advance', 10.0),
    ('call', 'fail'),
    ('call', 'ok'),
    ('advance', 10.0),
    ('call', 'ok'),
    ('call', 'ok'),
    ('state',)]],
  {'trace': ['fail', 'fail', 'fail', 'fail', 'open', 'ok', 'ok', 'Closed'],
   'state': 'Closed',
   'service_calls': 6,
   'log': [(0.0, 'Closed', 'Open'),
           (10.0, 'Open', 'Half-Open'),
           (10.0, 'Half-Open', 'Open'),
           (20.0, 'Open', 'Half-Open'),
           (20.0, 'Half-Open', 'Closed')]}),
 ('S3',
  'breaker',
  ['CircuitBreaker',
   {'failure_threshold': 3, 'open_timeout': 10.0, 'success_threshold': 2},
   [('call', 'fail'),
    ('call', 'fail'),
    ('call', 'fail'),
    ('advance', 12.0),
    ('call', 'ok'),
    ('call', 'fail'),
    ('advance', 5.0),
    ('call', 'ok'),
    ('advance', 5.0),
    ('call', 'ok'),
    ('call', 'ok'),
    ('call', 'ok')]],
  {'trace': ['fail', 'fail', 'fail', 'ok', 'fail', 'open', 'ok', 'ok', 'ok'],
   'state': 'Closed',
   'service_calls': 8,
   'log': [(0.0, 'Closed', 'Open'),
           (12.0, 'Open', 'Half-Open'),
           (12.0, 'Half-Open', 'Open'),
           (22.0, 'Open', 'Half-Open'),
           (22.0, 'Half-Open', 'Closed')]}),
 ('S3',
  'breaker',
  ['CircuitBreaker',
   {'failure_threshold': 2, 'open_timeout': 1.0, 'success_threshold': 3},
   [('call', 'fail'),
    ('call', 'fail'),
    ('advance', 1.0),
    ('call', 'ok'),
    ('call', 'ok'),
    ('call', 'ok'),
    ('call', 'fail'),
    ('call', 'fail'),
    ('state',)]],
  {'trace': ['fail', 'fail', 'ok', 'ok', 'ok', 'fail', 'fail', 'Open'],
   'state': 'Open',
   'service_calls': 7,
   'log': [(0.0, 'Closed', 'Open'),
           (1.0, 'Open', 'Half-Open'),
           (1.0, 'Half-Open', 'Closed'),
           (1.0, 'Closed', 'Open')]})]


@pytest.mark.parametrize("tag,drv,args,expected", T06, ids=_ids(T06, "T06"))
def test_task_06(tag, drv, args, expected):
    run(6, drv, args, expected)
