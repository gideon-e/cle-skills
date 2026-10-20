#!/usr/bin/env python3
"""Arizona deadline math for this skill. Compute it; don't count by hand.

Usage:
  python3 deadlines.py period <YYYY-MM-DD trigger> <days> [label]
      A period counted in days (Rule 6(a)): excludes the trigger day (6(a)(1)); for periods
      under 11 days skips intermediate weekends (6(a)(2)); rolls a weekend last day forward
      (6(a)(3)).
  python3 deadlines.py date <YYYY-MM-DD> [label]
      A calendar date set by stipulation or order. Not a counted period: if it falls on a
      weekend, the safe service day is the business day before.

Common periods: ESI production 40 days after the initial disclosure (26.1(c)(2)); response to
a request for production 30 days after service (34(b)(3)(A)); supplement 30 days after
discovery of the information (26.1(f)(2)).

Holidays are not built in: the output always reminds the user to check them.
"""
import datetime as dt, sys

WD = "Monday Tuesday Wednesday Thursday Friday Saturday Sunday".split()


def d(s):
    return dt.date.fromisoformat(s)


def show(x):
    return f"{WD[x.weekday()]}, {x:%B} {x.day}, {x.year}"


def period(trigger, days, label):
    t = d(trigger)
    if days < 11:
        x, n = t, 0
        while n < days:
            x += dt.timedelta(1)
            if x.weekday() < 5:
                n += 1
    else:
        x = t + dt.timedelta(days)
    note = ""
    if x.weekday() >= 5:
        y = x
        while y.weekday() >= 5:
            y += dt.timedelta(1)
        note = f" (falls on {WD[x.weekday()]}; rolls to {show(y)} under 6(a)(3))"
        x = y
    print(f"{label}: {show(t)} + {days} days = {show(x)}{note}. Check for a legal holiday.")


def date(s, label):
    x = d(s)
    if x.weekday() >= 5:
        y = x
        while y.weekday() >= 5:
            y -= dt.timedelta(1)
        print(f"{label}: {show(x)} is a weekend. Rule 6(a) counts periods, not set dates; "
              f"serve by {show(y)} to be safe. Check for a legal holiday.")
    else:
        print(f"{label}: {show(x)}. Check for a legal holiday.")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "period" and len(a) >= 3:
        period(a[1], int(a[2]), a[3] if len(a) > 3 else "Deadline")
    elif a and a[0] == "date" and len(a) >= 2:
        date(a[1], a[2] if len(a) > 2 else "Deadline")
    else:
        sys.exit(__doc__)
