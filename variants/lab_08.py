class CircuitOpenError(Exception):
    """Вимикач розімкнений."""
    pass

class TransientError(Exception):
    """Тимчасова помилка, яку можна повторити."""
    pass

class PermanentError(Exception):
    """Постійна помилка, повторювати яку немає сенсу."""
    pass

class RetryGaveUp(Exception):
    """Вичерпано всі спроби повтору."""
    pass


def resilient_call(op, breaker, clock, max_attempts=3, base=0.1, factor=2.0, cap=2.0, fallback=None):
    """
    Виконує виклик через вимикач (breaker) з підтримкою повторів (retry) та запасної відповіді (fallback).
    """
    for attempt in range(1, max_attempts + 1):
        try:
            res = breaker.call(op)
            return (res, {"attempts": attempt, "source": "service", "reason": None})
        except CircuitOpenError:
            # Вимикач розімкнений — не повторюємо, одразу використовуємо fallback або кидаємо виняток
            if fallback is not None:
                return (fallback(), {"attempts": attempt, "source": "fallback", "reason": "circuit_open"})
            raise
        except PermanentError:
            # Постійні помилки не повторюються і запасна відповідь не використовується
            raise
        except TransientError as err:
            if attempt < max_attempts:
                # Обчислюємо експоненційну паузу без джитеру за правилами задачі 8
                delay = min(cap, base * (factor ** (attempt - 1)))
                clock.sleep(delay)
            else:
                if fallback is not None:
                    return (fallback(), {"attempts": max_attempts, "source": "fallback", "reason": "exhausted"})
                raise RetryGaveUp(f"Вичерпано спроб: {max_attempts}") from err