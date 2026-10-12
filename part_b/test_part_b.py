"""Перевірка частини Б: pytest part_b  (або PARAMS=шлях/до/params.json pytest part_b)."""
import json
import os
from pathlib import Path

import pytest

from criteria import check

PARAMS = Path(os.environ.get("PARAMS", Path(__file__).with_name("params.json")))


def test_params_have_all_fields():
    p = json.loads(PARAMS.read_text(encoding="utf-8"))
    assert set(p) == {"timeout", "retry", "breaker"}
    assert set(p["retry"]) == {"max_attempts", "base", "factor", "cap", "jitter"}
    assert set(p["breaker"]) == {"failure_threshold", "open_timeout", "success_threshold"}
    assert p["retry"]["jitter"] in ("none", "full")


def test_params_meet_requirements():
    problems = check(json.loads(PARAMS.read_text(encoding="utf-8")))
    assert not problems, "\n" + "\n".join(problems)
