"""Відкриті тести задачі 1: Мережа з несправностями між двома сервісами.

Запуск: pytest tests/test_lab_01.py
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


T01 = [('S1',
  'link',
  [('seq', [('ok', 0.2)]), [None]],
  {'results': [('ok', 'відповідь на q0', 0.2)], 'processed': 1, 'seen': 1, 'log': [(0, 0.0, 'ok')]}),
 ('S1',
  'link',
  [('seq', [('ok', 0.2), ('error', 0.1), ('ok', 0.5)]), [None, None, None]],
  {'results': [('ok', 'відповідь на q0', 0.2), ('ServiceUnavailable', '503', 0.3), ('ok', 'відповідь на q2', 0.8)],
   'processed': 2,
   'seen': 2,
   'log': [(0, 0.0, 'ok'), (1, 0.2, 'error'), (2, 0.3, 'ok')]}),
 ('S1',
  'link',
  [('seq', [('error', 0.3), ('error', 0.3)]), [1.0, 1.0, 1.0]],
  {'results': [('ServiceUnavailable', '503', 0.3),
               ('ServiceUnavailable', '503', 0.6),
               ('ok', 'відповідь на q2', 0.61)],
   'processed': 1,
   'seen': 1,
   'log': [(0, 0.0, 'error'), (1, 0.3, 'error'), (2, 0.6, 'ok')]}),
 ('S2',
  'link',
  [('seq', [('ok', 3.0)]), [1.0]],
  {'results': [('CallTimeout', 'Тайм-аут 1.0 с', 1.0)], 'processed': 1, 'seen': 1, 'log': [(0, 0.0, 'timeout')]}),
 ('S2',
  'link',
  [('seq', [('drop', 0.0), ('ok', 0.2)]), [2.0, 2.0]],
  {'results': [('CallTimeout', 'Тайм-аут 2.0 с', 2.0), ('ok', 'відповідь на q1', 2.2)],
   'processed': 1,
   'seen': 1,
   'log': [(0, 0.0, 'timeout'), (1, 2.0, 'ok')]}),
 ('S2',
  'link',
  [('seq', [('error', 5.0)]), [1.5]],
  {'results': [('CallTimeout', 'Тайм-аут 1.5 с', 1.5)], 'processed': 0, 'seen': 0, 'log': [(0, 0.0, 'timeout')]}),
 ('S3',
  'link',
  [('windows', [(2.0, 5.0, 'error', 0.5)]), [None, None, None, None, None, None]],
  {'results': [('ok', 'відповідь на q0', 1.0),
               ('ok', 'відповідь на q1', 2.0),
               ('ServiceUnavailable', '503', 2.5),
               ('ServiceUnavailable', '503', 3.0),
               ('ServiceUnavailable', '503', 3.5),
               ('ServiceUnavailable', '503', 4.0)],
   'processed': 2,
   'seen': 2,
   'log': [(0, 0.0, 'ok'),
           (1, 1.0, 'ok'),
           (2, 2.0, 'error'),
           (3, 2.5, 'error'),
           (4, 3.0, 'error'),
           (5, 3.5, 'error')]}),
 ('S3',
  'link',
  [('windows', [(0.0, 4.0, 'ok', 1.0), (4.0, 8.0, 'drop', 0.0)]), [None, None, None, None, 0.5, 0.5, 0.5]],
  {'results': [('ok', 'відповідь на q0', 1.0),
               ('ok', 'відповідь на q1', 2.0),
               ('ok', 'відповідь на q2', 3.0),
               ('ok', 'відповідь на q3', 4.0),
               ('CallTimeout', 'Тайм-аут 0.5 с', 4.5),
               ('CallTimeout', 'Тайм-аут 0.5 с', 5.0),
               ('CallTimeout', 'Тайм-аут 0.5 с', 5.5)],
   'processed': 4,
   'seen': 4,
   'log': [(0, 0.0, 'ok'),
           (1, 1.0, 'ok'),
           (2, 2.0, 'ok'),
           (3, 3.0, 'ok'),
           (4, 4.0, 'timeout'),
           (5, 4.5, 'timeout'),
           (6, 5.0, 'timeout')]}),
 ('S3',
  'link',
  [('windows', [(0.0, 100.0, 'ok', 2.5)]), [2.0, 2.0, 3.0, 3.0]],
  {'results': [('CallTimeout', 'Тайм-аут 2.0 с', 2.0),
               ('CallTimeout', 'Тайм-аут 2.0 с', 4.0),
               ('ok', 'відповідь на q2', 6.5),
               ('ok', 'відповідь на q3', 9.0)],
   'processed': 4,
   'seen': 4,
   'log': [(0, 0.0, 'timeout'), (1, 2.0, 'timeout'), (2, 4.0, 'ok'), (3, 6.5, 'ok')]})]


@pytest.mark.parametrize("tag,drv,args,expected", T01, ids=_ids(T01, "T01"))
def test_task_01(tag, drv, args, expected):
    run(1, drv, args, expected)
