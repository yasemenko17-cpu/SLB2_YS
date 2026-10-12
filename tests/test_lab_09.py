"""Відкриті тести задачі 9: Часткові відмови і деградація.

Запуск: pytest tests/test_lab_09.py
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


T09 = [('S1',
  'cache',
  [10.0, 60.0, {}, [('get', 'a', 'v1'), ('advance', 5.0), ('get', 'a', 'v2'), ('advance', 5.0), ('get', 'a', 'v3')]],
  {'results': [['v1', 'live'], ['v1', 'fresh'], ['v3', 'live']], 'cache': {'a': ['v3', 10.0]}}),
 ('S1',
  'cache',
  [10.0,
   60.0,
   {'a': ('старе', 0.0)},
   [('advance', 30.0), ('get', 'a', 'fail'), ('advance', 40.0), ('get', 'a', 'fail')]],
  {'results': [['старе', 'stale'], ['!ConnectionError', 'збій']], 'cache': {'a': ['старе', 0.0]}}),
 ('S1', 'cache', [10.0, 60.0, {}, [('get', 'a', 'fail')]], {'results': [['!ConnectionError', 'збій']], 'cache': {}}),
 ('S2',
  'view',
  [{'id': 'o1', 'lines': [{'sku': 's1', 'qty': 2}, {'sku': 's2', 'qty': 4}]},
   {'s1': {'title': 'Книга', 'price': 100.0}, 's2': {'title': 'Ручка', 'price': 12.5}},
   ['s9']],
  {'order_id': 'o1',
   'lines': [{'sku': 's1', 'qty': 2, 'title': 'Книга', 'price': 100.0},
             {'sku': 's2', 'qty': 4, 'title': 'Ручка', 'price': 12.5}],
   'total': 250.0,
   'recommendations': ['s9'],
   'degraded': []}),
 ('S2',
  'view',
  [{'id': 'o1', 'lines': [{'sku': 's1', 'qty': 2}, {'sku': 's2', 'qty': 4}]},
   {'s1': {'title': 'Книга', 'price': 100.0}},
   ['s9']],
  {'order_id': 'o1',
   'lines': [{'sku': 's1', 'qty': 2, 'title': 'Книга', 'price': 100.0},
             {'sku': 's2', 'qty': 4, 'title': None, 'price': None}],
   'total': 200.0,
   'recommendations': ['s9'],
   'degraded': ['catalogue']}),
 ('S2',
  'view',
  [{'id': 'o1', 'lines': [{'sku': 's1', 'qty': 2}, {'sku': 's2', 'qty': 4}]}, {}, 'fail'],
  {'order_id': 'o1',
   'lines': [{'sku': 's1', 'qty': 2, 'title': None, 'price': None},
             {'sku': 's2', 'qty': 4, 'title': None, 'price': None}],
   'total': 0.0,
   'recommendations': [],
   'degraded': ['catalogue', 'recommendations']}),
 ('S3',
  'health',
  [{'orders': (100, 0), 'catalogue': (99, 1)}, ['orders']],
  {'services': {'catalogue': {'rate': 0.99, 'status': 'ok'}, 'orders': {'rate': 1.0, 'status': 'ok'}},
   'overall': 'ok'}),
 ('S3',
  'health',
  [{'orders': (1, 1), 'catalogue': (10, 0)}, ['orders']],
  {'services': {'catalogue': {'rate': 1.0, 'status': 'ok'}, 'orders': {'rate': 0.5, 'status': 'degraded'}},
   'overall': 'degraded'}),
 ('S3',
  'health',
  [{'orders': (10, 0), 'catalogue': (1, 2)}, ['orders']],
  {'services': {'catalogue': {'rate': 0.3333, 'status': 'down'}, 'orders': {'rate': 1.0, 'status': 'ok'}},
   'overall': 'degraded'})]


@pytest.mark.parametrize("tag,drv,args,expected", T09, ids=_ids(T09, "T09"))
def test_task_09(tag, drv, args, expected):
    run(9, drv, args, expected)
