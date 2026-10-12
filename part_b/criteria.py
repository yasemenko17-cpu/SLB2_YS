"""Вимоги частини Б до параметрів. Повертає список невиконаних вимог (порожній список означає успіх)."""
from experiment import SCENARIOS
from resilience import run_scenario


def check(params):
    problems = []
    a = run_scenario(SCENARIOS["A"], params)
    b = run_scenario(SCENARIOS["B"], params)
    if a["live"] < 119:
        problems.append(f"сценарій A: живих відповідей {a['live']} із 120 (потрібно не менше 119)")
    if a["breaker_opens"] != 0:
        problems.append(f"сценарій A: вимикач розімкнувся {a['breaker_opens']} раз(и), а короткий збій має пережити лише Retry")
    if b["breaker_opens"] < 1:
        problems.append("сценарій B: вимикач жодного разу не розімкнувся")
    if b["calls_in_outage"] > 25:
        problems.append(f"сценарій B: до завислого сервісу дійшло {b['calls_in_outage']} викликів (потрібно не більше 25)")
    if b["worst_latency"] > 4.0:
        problems.append(f"сценарій B: найдовше очікування користувача {b['worst_latency']} с (потрібно не більше 4,0 с)")
    if b["recovery_after"] is None or b["recovery_after"] > 15:
        problems.append(f"сценарій B: сервіс відновився, а живі відповіді повернулись через {b['recovery_after']} с (потрібно не більше 15 с)")
    return problems
