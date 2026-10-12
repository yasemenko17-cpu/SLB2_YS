"""Частина Б. Запускає два сценарії з вашими параметрами з params.json і друкує показники.

Запуск:  python experiment.py            (читає params.json у цій теці)
         python experiment.py іншийфайл.json
"""
import json
import sys
from pathlib import Path

from resilience import run_scenario

SCENARIOS = {
    "A": {"title": "Короткий збій: 503 з 30-ї по 32-гу секунду", "outages": [(30.0, 32.0, "fast")]},
    "B": {"title": "Тривала аварія: сервіс зависає з 30-ї по 90-ту секунду", "outages": [(30.0, 90.0, "hang")]},
}


def load_params(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else Path(__file__).with_name("params.json")
    params = load_params(path)
    for key, sc in SCENARIOS.items():
        m = run_scenario(sc, params)
        print(f"Сценарій {key}. {sc['title']}")
        for name, value in m.items():
            print(f"  {name:<16} {value}")
        print()


if __name__ == "__main__":
    main()
