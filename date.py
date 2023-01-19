from datetime import datetime
from calendar import monthrange


def weekday(date):
    formatted_date = datetime(day=int(date[0:2]), month=int(date[3:5]), year=int(date[6:10]))
    formatted_date.isoweekday()


def max_date(timedelta):
    year = datetime.now().year
    month = datetime.now().month

    month = month + int(timedelta)
    if month == 13:
        month = 1
        year += 1
    day = monthrange(year, month)[1]

    return day, month, year
