'''
    Utility function to help in calculating next day of the week when we want our Change Request to be scheduled.
    Based on the input of the day # of the week, we will calculate distance till it and add it to current date.
    Time scheduled is in GMT (+5 EST) hence we will go next day.

    If SN server will work with local we will set:
    start_time = time(22, 00)
    end_time = time(23, 59)
    
    However same +5h, plus the day_of_the_week +1:
    start_time = time(3, 00)
    end_time = time(4, 59)
'''
from datetime import datetime, time
from dateutil.relativedelta import relativedelta

def dates_calculations(day_of_week:int):
    current = datetime.now()
    next_date = (current + relativedelta(hours=22, minutes=00, weekday=day_of_week+1)).date()
    co_start_date = (current + relativedelta(hours=22, minutes=00, weekday=day_of_week)).date()
    co_end_date = (current + relativedelta(hours=22, minutes=00, weekday=day_of_week+1)).date()
    start_time = time(21, 00)
    start_date = f'{datetime.combine(co_start_date, start_time):%d-%m-%Y %H:%M:%S}'
    end_time = time(5, 59)
    end_date = f'{datetime.combine(co_end_date, end_time):%d-%m-%Y %H:%M:%S}'
    week_year = next_date.strftime("%V")
    return start_date, end_date, week_year