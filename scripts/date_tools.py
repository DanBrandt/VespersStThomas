from datetime import date

def next_year_when_falls_on_weekday(month, day, weekday):
    today = date.today()
    start_year = today.year
    if date(start_year, month, day) <= today:
        start_year += 1
    for y in range(start_year, start_year + 100):
        if date(y, month, day).weekday = weekday:
            return y
    return 0
