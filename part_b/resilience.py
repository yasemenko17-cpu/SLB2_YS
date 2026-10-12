"""Готові будівельні блоки для частини Б: керований годинник, сервіс-імітація, повтори та вимикач.

Цей файл змінювати не потрібно. Ви лише добираєте параметри в params.json (див. experiment.py).
"""
import random


class VirtualClock:
    """Час рухається лише коли код викликає sleep, тому експерименти миттєві й повторювані."""

    def __init__(self):
        self._now = 0.0

    def now(self):
        return self._now

    def sleep(self, seconds):
        self._now += seconds

    def advance_to(self, moment):
        self._now = max(self._now, moment)


class Catalogue:
    """Сервіс каталогу. У вікнах аварії відповідає помилкою ("fast") або зависає на 5 с ("hang")."""

    def __init__(self, clock, outages):
        self.clock = clock
        self.outages = outages          # список (початок, кінець, вид)
        self.calls = 0
        self.calls_in_outage = 0

    def _mode(self):
        now = self.clock.now()
        for start, end, kind in self.outages:
            if start <= now < end:
                return kind
        return None

    def get(self, timeout):
        self.calls += 1
        mode = self._mode()
        if mode is None:
            self.clock.sleep(0.05)
            return "картка товару"
        self.calls_in_outage += 1
        if mode == "fast":
            self.clock.sleep(0.05)
            raise ConnectionError("503")
        if 5.0 > timeout:
            self.clock.sleep(timeout)
            raise TimeoutError("тайм-аут")
        self.clock.sleep(5.0)
        raise ConnectionError("503")


class CircuitOpenError(Exception):
    pass


class Breaker:
    def __init__(self, clock, failure_threshold, open_timeout, success_threshold):
        self.clock, self.threshold, self.open_timeout, self.need = clock, failure_threshold, open_timeout, success_threshold
        self.state, self.failures, self.successes, self.opened_at, self.opens = "Closed", 0, 0, 0.0, 0

    def call(self, fn):
        if self.state == "Open":
            if self.clock.now() - self.opened_at < self.open_timeout:
                raise CircuitOpenError("розімкнено")
            self.state, self.successes = "Half-Open", 0
        try:
            value = fn()
        except Exception:
            if self.state == "Half-Open" or self.failures + 1 >= self.threshold:
                self.state, self.opened_at, self.failures = "Open", self.clock.now(), 0
                self.opens += 1
            else:
                self.failures += 1
            raise
        if self.state == "Half-Open":
            self.successes += 1
            if self.successes >= self.need:
                self.state, self.failures = "Closed", 0
        else:
            self.failures = 0
        return value


def fetch_with_protection(service, breaker, clock, rng, p):
    """Один запит користувача: повтори навколо вимикача, запасна відповідь у разі невдачі."""
    r = p["retry"]
    for attempt in range(1, r["max_attempts"] + 1):
        try:
            return breaker.call(lambda: service.get(p["timeout"])), "live"
        except CircuitOpenError:
            return "запасна відповідь", "fallback"
        except (ConnectionError, TimeoutError):
            if attempt == r["max_attempts"]:
                break
            top = min(r["cap"], r["base"] * r["factor"] ** (attempt - 1))
            clock.sleep(rng.random() * top if r["jitter"] == "full" else top)
    return "запасна відповідь", "fallback"


def run_scenario(scenario, p, seconds=120):
    """Користувачі надсилають по запиту щосекунди; повертає показники."""
    clock = VirtualClock()
    service = Catalogue(clock, scenario["outages"])
    b = p["breaker"]
    breaker = Breaker(clock, b["failure_threshold"], b["open_timeout"], b["success_threshold"])
    rng = random.Random(7)
    live = fallback = 0
    worst = 0.0
    last_end = max((e for _, e, _ in scenario["outages"]), default=0.0)
    recovered_at = None
    for second in range(seconds):
        clock.advance_to(float(second))
        started = clock.now()
        _, source = fetch_with_protection(service, breaker, clock, rng, p)
        worst = max(worst, clock.now() - started)
        if source == "live":
            live += 1
            if recovered_at is None and started >= last_end:
                recovered_at = started
        else:
            fallback += 1
    return {"requests": seconds, "live": live, "fallback": fallback, "service_calls": service.calls,
            "calls_in_outage": service.calls_in_outage, "worst_latency": round(worst, 3),
            "breaker_opens": breaker.opens,
            "recovery_after": None if recovered_at is None else round(recovered_at - last_end, 3)}
