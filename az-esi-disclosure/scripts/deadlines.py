#!/usr/bin/env python3
"""Arizona deadline math for this skill. Compute it; don't count by hand.

Usage:
  python3 deadlines.py period <YYYY-MM-DD trigger> <days> [label] [--holidays D,D,...]
      A period counted forward from an event (Rule 6(a)): excludes the trigger day
      (6(a)(1)); for periods under 11 days skips intermediate weekends and holidays
      (6(a)(2)); a last day on a weekend or holiday runs to the next day that is not one
      (6(a)(3)).
  python3 deadlines.py before <YYYY-MM-DD event> <days> [label] [--holidays D,D,...]
      A period measured before an event ("at least N days before"): the same rules,
      counting backward, so a weekend or holiday last day moves earlier (6(a)(4)).
  python3 deadlines.py date <YYYY-MM-DD> [label] [--holidays D,D,...]
      A calendar date set by stipulation or order. Not a counted period: if it falls on a
      weekend or holiday, the safe service day is the business day before.

--holidays takes the court's legal holidays as YYYY-MM-DD dates, comma-separated. This
script has no holiday calendar of its own: without --holidays it counts only weekends, and
every line it prints says whether holidays were applied.

Common periods: ESI production 40 days after the initial disclosure (26.1(c)(2)); response to
a request for production 30 days after service (34(b)(3)(A)); supplement 30 days after
discovery of the information (26.1(f)(2)). Extra days for the method of service are not
built in; rules.md does not bundle that rule.
"""
import datetime as dt, sys

WD = "Monday Tuesday Wednesday Thursday Friday Saturday Sunday".split()


def show(x):
    return f"{WD[x.weekday()]}, {x:%B} {x.day}, {x.year}"


def closed(x, holidays):
    return x.weekday() >= 5 or x in holidays


def why(x, holidays):
    return "a legal holiday you listed" if x in holidays else "a weekend day"


def count(trigger, days, step, holidays):
    """Rule 6(a)(1)-(4): step is +1 for after an event, -1 for before one."""
    x = trigger
    if days < 11:
        n = 0
        while n < days:
            x += dt.timedelta(step)
            if not closed(x, holidays):
                n += 1
        return x, ""
    x = trigger + dt.timedelta(step * days)
    if not closed(x, holidays):
        return x, ""
    first = x
    while closed(x, holidays):
        x += dt.timedelta(step)
    rule = "6(a)(3)" if step > 0 else "6(a)(3)-(4)"
    return x, f" ({show(first)} is {why(first, holidays)}; moves to {show(x)} under {rule})"


def tail(holidays):
    if holidays:
        return f"Holidays applied: {', '.join(f'{h:%Y-%m-%d}' for h in sorted(holidays))}. Confirm the list."
    return "No holidays applied: check for a legal holiday."


def main(argv):
    holidays = set()
    if "--holidays" in argv:
        i = argv.index("--holidays")
        if i + 1 >= len(argv):
            raise ValueError("--holidays needs a value")
        holidays = {dt.date.fromisoformat(h.strip()) for h in argv[i + 1].split(",") if h.strip()}
        argv = argv[:i] + argv[i + 2:]
    if len(argv) >= 3 and argv[0] in ("period", "before"):
        start, days = dt.date.fromisoformat(argv[1]), int(argv[2])
        if days < 1:
            raise ValueError("days must be 1 or more; use 'before' for a period before an event")
        label = argv[3] if len(argv) > 3 else "Deadline"
        step = 1 if argv[0] == "period" else -1
        x, note = count(start, days, step, holidays)
        sign = "+" if step > 0 else "-"
        return f"{label}: {show(start)} {sign} {days} days = {show(x)}{note}. {tail(holidays)}"
    if len(argv) >= 2 and argv[0] == "date":
        x = dt.date.fromisoformat(argv[1])
        label = argv[2] if len(argv) > 2 else "Deadline"
        if not closed(x, holidays):
            return f"{label}: {show(x)}. {tail(holidays)}"
        y = x
        while closed(y, holidays):
            y -= dt.timedelta(1)
        return (f"{label}: {show(x)} is {why(x, holidays)}. Rule 6(a) counts periods, not set "
                f"dates; serve by {show(y)} to be safe. {tail(holidays)}")
    raise ValueError("unrecognized command")


if __name__ == "__main__":
    try:
        print(main(sys.argv[1:]))
    except ValueError as e:
        sys.exit(f"Error: {e}\n\n{__doc__}")
