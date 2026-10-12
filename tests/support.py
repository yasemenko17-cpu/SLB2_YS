"""Допоміжний код тестів: керований годинник, «випадковість» із заданих чисел і драйвери задач.

Годинник рухається лише коли код викликає sleep, тому тести не чекають по-справжньому.
Генератор випадкових чисел замінено послідовністю заздалегідь заданих значень: так усі очікувані
значення можна перевірити вручну.
"""
from conftest import load


class Clock:
    """Керований годинник: now() і sleep(seconds)."""

    def __init__(self, start=0.0):
        self._now = float(start)

    def now(self):
        return self._now

    def sleep(self, seconds):
        if seconds < 0:
            raise ValueError("час не може йти назад")
        self._now += seconds


class FixedRng:
    """Замінює random.Random: random() повертає задані числа по колу, uniform(a, b) = a + (b - a) * random()."""

    def __init__(self, values):
        self.values = list(values) or [0.5]
        self.i = 0

    def random(self):
        value = self.values[self.i % len(self.values)]
        self.i += 1
        return value

    def uniform(self, a, b):
        return a + (b - a) * self.random()


def r(x):
    """Округлення для порівняння дробових чисел у виводі драйверів."""
    return round(x, 6) if isinstance(x, float) else x


def safe(fn, *args):
    """Виконує fn; виняток перетворюється на кортеж ("!Клас", "повідомлення")."""
    try:
        return fn(*args)
    except Exception as exc:  # noqa: BLE001
        return ("!" + type(exc).__name__, str(exc))


# ---- Задача 1


def d_link(mod, schedule, calls):
    clock = Clock()
    kind, spec = schedule[0], schedule[1]
    if kind == "seq":
        def sched(n, now):
            return tuple(spec[n]) if n < len(spec) else ("ok", 0.01)
    else:
        def sched(n, now):
            for t0, t1, k, lat in spec:
                if t0 <= now < t1:
                    return (k, lat)
            return ("ok", 1.0)
    seen = []

    def service(req):
        seen.append(req)
        return f"відповідь на {req}"
    link = mod.FaultyLink(clock, service, sched)
    results = []
    for i, timeout in enumerate(calls):
        try:
            results.append(("ok", link.call(f"q{i}", timeout), r(clock.now())))
        except Exception as exc:  # noqa: BLE001
            results.append((type(exc).__name__, str(exc), r(clock.now())))
    return {"results": results, "processed": link.processed, "seen": len(seen),
            "log": [(n, r(t), k) for n, t, k in link.log]}


# ---- Задача 2


def d_eff(mod, remaining, per_call, reserve=None):
    """reserve=None означає, що аргумент не передається (діє значення за замовчуванням)."""
    if reserve is None:
        return safe(mod.effective_timeout, remaining, per_call)
    return safe(mod.effective_timeout, remaining, per_call, reserve)


def d_deadline(mod, budget, steps):
    clock = Clock()
    dl = safe(mod.Deadline, clock, budget)
    if isinstance(dl, tuple):
        return dl
    out = []
    for step in steps:
        op = step[0]
        if op == "sleep":
            clock.sleep(step[1])
        elif op == "remaining":
            out.append(r(dl.remaining()))
        elif op == "expired":
            out.append(dl.expired())
        elif op == "check":
            out.append(safe(dl.check) or "ok")
        elif op == "timeout_for":
            v = safe(dl.timeout_for, step[1])
            out.append(r(v) if not isinstance(v, tuple) else v)
    return out


def d_split(mod, total, weights, reserve=None):
    if reserve is None:
        v = safe(mod.split_budget, total, weights)
    else:
        v = safe(mod.split_budget, total, weights, reserve)
    return [r(x) for x in v] if isinstance(v, list) else v


# ---- Задача 3


def d_status(mod, code):
    return safe(mod.classify_status, code)


def d_retryable(mod, method, outcome, key):
    return safe(mod.is_retryable, method, outcome, key)


def d_after(mod, value, default):
    return r(safe(mod.parse_retry_after, value, default))


# ---- Задача 4


def d_delays(mod, n, base, factor, cap):
    v = safe(mod.backoff_delays, n, base, factor, cap)
    return [r(x) for x in v] if isinstance(v, list) else v


def d_jitter(mod, attempt, base, factor, cap, mode, values):
    return r(safe(mod.jittered_delay, attempt, base, factor, cap, mode, FixedRng(values)))


def d_decor(mod, n, base, cap, values):
    v = safe(mod.decorrelated_delays, n, base, cap, FixedRng(values))
    return [r(x) for x in v] if isinstance(v, list) else v


# ---- Задача 5 і 8: скрипт відповідей сервісу


def make_op(mod, script):
    """script: елементи "ok:значення", "T", "T:пауза_сервера", "P" — по одному на кожен виклик."""
    state = {"calls": 0}

    def op():
        item = script[min(state["calls"], len(script) - 1)]
        state["calls"] += 1
        if item.startswith("ok"):
            return item.split(":", 1)[1] if ":" in item else "ok"
        if item.startswith("T"):
            if ":" in item:
                raise mod.TransientError("збій", retry_after=float(item.split(":")[1]))
            raise mod.TransientError("збій")
        raise mod.PermanentError("помилка")
    return op, state



def d_retry(mod, script, kwargs, values):
    kwargs = dict(kwargs)
    clock = Clock(kwargs.pop("start", 0.0))
    op, st = make_op(mod, script)
    got = safe(lambda: mod.retry_call(op, clock, FixedRng(values), **kwargs))
    if isinstance(got, tuple) and got and isinstance(got[0], str) and got[0].startswith("!"):
        outcome = list(got)
    else:
        outcome = ["ok", got[0], got[1]]
    return {"outcome": outcome, "calls": st["calls"], "now": r(clock.now())}


# ---- Задача 6 і 7


def d_breaker(mod, cls, params, steps):
    clock = Clock()
    cb = getattr(mod, cls)(clock, **params)
    trace = []
    calls = {"n": 0}

    def make(kind):
        def fn():
            calls["n"] += 1
            if kind.startswith("slow"):
                clock.sleep(float(kind.split(":")[1]))
                return "ok"
            if kind == "fail":
                raise ConnectionError("збій")
            return "ok"
        return fn
    for step in steps:
        if step[0] == "advance":
            clock.sleep(step[1])
        elif step[0] == "state":
            trace.append(cb.state)
        else:
            try:
                cb.call(make(step[1]))
                trace.append("ok")
            except mod.CircuitOpenError:
                trace.append("open")
            except ConnectionError:
                trace.append("fail")
    out = {"trace": trace, "state": cb.state, "service_calls": calls["n"]}
    if hasattr(cb, "log"):
        out["log"] = [(r(t), a, b) for t, a, b in cb.log]
    return out


# ---- Задача 8


class ScriptedBreaker:
    """Найпростіший вимикач для перевірки композиції: після open_after поспіль збоїв відхиляє все."""

    def __init__(self, mod, open_after):
        self.mod, self.open_after, self.failures, self.calls, self.rejected = mod, open_after, 0, 0, 0

    def call(self, fn):
        if self.failures >= self.open_after:
            self.rejected += 1
            raise self.mod.CircuitOpenError("розімкнено")
        self.calls += 1
        try:
            value = fn()
        except Exception:
            self.failures += 1
            raise
        self.failures = 0
        return value


def d_resilient(mod, open_after, script, kwargs, fallback):
    clock = Clock()
    op, st = make_op(mod, script)
    br = ScriptedBreaker(mod, open_after)
    fb = (lambda: fallback) if fallback is not None else None
    got = safe(lambda: mod.resilient_call(op, br, clock, fallback=fb, **kwargs))
    if isinstance(got, tuple) and got and isinstance(got[0], str) and got[0].startswith("!"):
        res = list(got)
    else:
        res = [got[0], got[1]]
    return {"result": res, "service_calls": st["calls"], "rejected": br.rejected, "now": r(clock.now())}


# ---- Задача 9


def d_cache(mod, ttl, stale_ttl, cache, steps):
    clock = Clock()
    cache = {k: tuple(v) for k, v in cache.items()}
    out = []
    for step in steps:
        if step[0] == "advance":
            clock.sleep(step[1])
            continue
        _, key, fetched = step

        def fetch():
            if fetched == "fail":
                raise ConnectionError("збій")
            return fetched
        got = safe(lambda: mod.get_with_fallback(key, fetch, cache, clock, ttl, stale_ttl))
        out.append(list(got))
    return {"results": out, "cache": {k: [v[0], r(v[1])] for k, v in sorted(cache.items())}}


def d_view(mod, order, catalogue, recs):
    def orders(oid):
        if order == "fail":
            raise ConnectionError("збій")
        return order

    def cat(sku):
        v = catalogue.get(sku, "fail")
        if v == "fail":
            raise ConnectionError("збій")
        return v

    def rec(oid):
        if recs == "fail":
            raise ConnectionError("збій")
        return recs
    got = safe(lambda: mod.build_order_view("o1", orders, cat, rec))
    if isinstance(got, dict):
        got = dict(got)
        got["total"] = r(got["total"])
    return got


def d_health(mod, results, critical):
    """results: служба -> (кількість успішних, кількість невдалих); перетворюється на список True/False."""
    expanded = {k: [True] * ok + [False] * bad for k, (ok, bad) in results.items()}
    return safe(mod.health_report, expanded, critical)


# ---- Задача 10


def d_summary(mod, events):
    return safe(mod.summarize_log, [tuple(e) for e in events])


def d_amp(mod, layers):
    return safe(mod.retry_amplification, layers)


def d_rps(mod, rps, layers):
    return r(safe(mod.amplified_rps, rps, layers))


def d_wcw(mod, attempts, timeout, base, factor, cap):
    return r(safe(mod.worst_case_wait, attempts, timeout, base, factor, cap))


def d_maxatt(mod, budget, timeout, base, factor, cap):
    return safe(mod.max_attempts_for_budget, budget, timeout, base, factor, cap)


DRIVERS = {k[2:]: v for k, v in dict(globals()).items() if k.startswith("d_")}
