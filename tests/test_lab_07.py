"""Відкриті тести задачі 7: Вимикач за часткою збоїв у ковзному вікні.

Запуск: pytest tests/test_lab_07.py
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


T07 = [('S1',
  'breaker',
  ['WindowBreaker',
   {'window': 10, 'min_calls': 5, 'failure_rate': 0.5, 'open_timeout': 10.0, 'probe_calls': 2},
   [('call', 'ok'), ('call', 'ok'), ('call', 'ok'), ('call', 'fail'), ('call', 'fail'), ('state',)]],
  {'trace': ['ok', 'ok', 'ok', 'fail', 'fail', 'Closed'], 'state': 'Closed', 'service_calls': 5}),
 ('S1',
  'breaker',
  ['WindowBreaker',
   {'window': 10, 'min_calls': 5, 'failure_rate': 0.5, 'open_timeout': 10.0, 'probe_calls': 2},
   [('call', 'ok'), ('call', 'ok'), ('call', 'ok'), ('call', 'fail'), ('state',), ('call', 'ok'), ('state',)]],
  {'trace': ['ok', 'ok', 'ok', 'fail', 'Closed', 'ok', 'Closed'], 'state': 'Closed', 'service_calls': 5}),
 ('S1',
  'breaker',
  ['WindowBreaker',
   {'window': 10, 'min_calls': 5, 'failure_rate': 0.5, 'open_timeout': 10.0, 'probe_calls': 2},
   [('call', 'fail'),
    ('call', 'fail'),
    ('call', 'fail'),
    ('call', 'fail'),
    ('state',),
    ('call', 'fail'),
    ('state',),
    ('call', 'ok')]],
  {'trace': ['fail', 'fail', 'fail', 'fail', 'Closed', 'fail', 'Open', 'open'], 'state': 'Open', 'service_calls': 5}),
 ('S2',
  'breaker',
  ['WindowBreaker',
   {'window': 4, 'min_calls': 4, 'failure_rate': 0.5, 'open_timeout': 10.0, 'probe_calls': 2},
   [('call', 'fail'),
    ('call', 'fail'),
    ('call', 'ok'),
    ('call', 'ok'),
    ('state',),
    ('call', 'ok'),
    ('call', 'ok'),
    ('call', 'ok'),
    ('state',)]],
  {'trace': ['fail', 'fail', 'ok', 'ok', 'Open', 'open', 'open', 'open', 'Open'],
   'state': 'Open',
   'service_calls': 4}),
 ('S2',
  'breaker',
  ['WindowBreaker',
   {'window': 4, 'min_calls': 4, 'failure_rate': 0.75, 'open_timeout': 10.0, 'probe_calls': 2},
   [('call', 'fail'),
    ('call', 'fail'),
    ('call', 'fail'),
    ('call', 'ok'),
    ('state',),
    ('call', 'ok'),
    ('call', 'ok'),
    ('state',),
    ('call', 'fail'),
    ('call', 'fail'),
    ('state',)]],
  {'trace': ['fail', 'fail', 'fail', 'ok', 'Open', 'open', 'open', 'Open', 'open', 'open', 'Open'],
   'state': 'Open',
   'service_calls': 4}),
 ('S2',
  'breaker',
  ['WindowBreaker',
   {'window': 10, 'min_calls': 2, 'failure_rate': 0.5, 'open_timeout': 10.0, 'probe_calls': 2},
   [('call', 'fail'), ('state',), ('call', 'fail'), ('state',)]],
  {'trace': ['fail', 'Closed', 'fail', 'Open'], 'state': 'Open', 'service_calls': 2}),
 ('S3',
  'breaker',
  ['WindowBreaker',
   {'window': 10, 'min_calls': 5, 'failure_rate': 0.5, 'open_timeout': 10.0, 'probe_calls': 2},
   [('call', 'fail'),
    ('call', 'fail'),
    ('call', 'fail'),
    ('call', 'fail'),
    ('call', 'fail'),
    ('advance', 10.0),
    ('call', 'ok'),
    ('state',),
    ('call', 'ok'),
    ('state',)]],
  {'trace': ['fail', 'fail', 'fail', 'fail', 'fail', 'ok', 'Half-Open', 'ok', 'Closed'],
   'state': 'Closed',
   'service_calls': 7}),
 ('S3',
  'breaker',
  ['WindowBreaker',
   {'window': 10, 'min_calls': 5, 'failure_rate': 0.5, 'open_timeout': 10.0, 'probe_calls': 2},
   [('call', 'fail'),
    ('call', 'fail'),
    ('call', 'fail'),
    ('call', 'fail'),
    ('call', 'fail'),
    ('advance', 10.0),
    ('call', 'ok'),
    ('call', 'fail'),
    ('state',),
    ('call', 'ok')]],
  {'trace': ['fail', 'fail', 'fail', 'fail', 'fail', 'ok', 'fail', 'Open', 'open'],
   'state': 'Open',
   'service_calls': 7}),
 ('S3',
  'breaker',
  ['WindowBreaker',
   {'window': 10, 'min_calls': 5, 'failure_rate': 0.5, 'open_timeout': 10.0, 'probe_calls': 1},
   [('call', 'fail'),
    ('call', 'fail'),
    ('call', 'fail'),
    ('call', 'fail'),
    ('call', 'fail'),
    ('advance', 10.0),
    ('call', 'ok'),
    ('state',),
    ('call', 'fail'),
    ('state',)]],
  {'trace': ['fail', 'fail', 'fail', 'fail', 'fail', 'ok', 'Closed', 'fail', 'Closed'],
   'state': 'Closed',
   'service_calls': 7})]


@pytest.mark.parametrize("tag,drv,args,expected", T07, ids=_ids(T07, "T07"))
def test_task_07(tag, drv, args, expected):
    run(7, drv, args, expected)
