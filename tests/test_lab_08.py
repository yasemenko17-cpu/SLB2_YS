"""Відкриті тести задачі 8: Повтори, вимикач і запасна відповідь разом.

Запуск: pytest tests/test_lab_08.py
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


T08 = [('S1',
  'resilient',
  [99, ['ok:V'], {}, None],
  {'result': ['V', {'attempts': 1, 'source': 'service', 'reason': None}],
   'service_calls': 1,
   'rejected': 0,
   'now': 0.0}),
 ('S1',
  'resilient',
  [99, ['T', 'T', 'ok:V'], {}, None],
  {'result': ['V', {'attempts': 3, 'source': 'service', 'reason': None}],
   'service_calls': 3,
   'rejected': 0,
   'now': 0.3}),
 ('S1',
  'resilient',
  [99, ['T', 'T', 'T', 'ok:V'], {}, None],
  {'result': ['!RetryGaveUp', 'Вичерпано спроб: 3'], 'service_calls': 3, 'rejected': 0, 'now': 0.3}),
 ('S2',
  'resilient',
  [99, ['T', 'T', 'T'], {}, 'кеш'],
  {'result': ['кеш', {'attempts': 3, 'source': 'fallback', 'reason': 'exhausted'}],
   'service_calls': 3,
   'rejected': 0,
   'now': 0.3}),
 ('S2',
  'resilient',
  [2, ['T', 'T', 'T'], {'max_attempts': 5}, 'кеш'],
  {'result': ['кеш', {'attempts': 3, 'source': 'fallback', 'reason': 'circuit_open'}],
   'service_calls': 2,
   'rejected': 1,
   'now': 0.3}),
 ('S2',
  'resilient',
  [99, ['T', 'ok:V'], {}, 'кеш'],
  {'result': ['V', {'attempts': 2, 'source': 'service', 'reason': None}],
   'service_calls': 2,
   'rejected': 0,
   'now': 0.1}),
 ('S3',
  'resilient',
  [99, ['P'], {}, 'кеш'],
  {'result': ['!PermanentError', 'помилка'], 'service_calls': 1, 'rejected': 0, 'now': 0.0}),
 ('S3',
  'resilient',
  [99, ['T', 'P'], {}, None],
  {'result': ['!PermanentError', 'помилка'], 'service_calls': 2, 'rejected': 0, 'now': 0.1}),
 ('S3',
  'resilient',
  [99, ['T', 'T', 'ok:V'], {'max_attempts': 1}, None],
  {'result': ['!RetryGaveUp', 'Вичерпано спроб: 1'], 'service_calls': 1, 'rejected': 0, 'now': 0.0})]


@pytest.mark.parametrize("tag,drv,args,expected", T08, ids=_ids(T08, "T08"))
def test_task_08(tag, drv, args, expected):
    run(8, drv, args, expected)
