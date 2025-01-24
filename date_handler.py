from datetime import datetime
from datetime import date
from pandas_market_calendars import get_calendar
import pytz
from datetime import datetime
import pandas as pd


today = date.today()

today_year_to_day = today
today_standard = today.strftime("%m-%d-%Y")
today_crunched = today.strftime("%m%d%Y")


def get_prev_bus_day():
    # Get the NYSE calendar
    nyse = get_calendar('NYSE')

    # Get the New York time zone
    timezone_str = nyse.tz.zone
    timezone = pytz.timezone(timezone_str)


    # Specify the start date and time zone
    start_date = datetime(2024, 1, 1, tzinfo=timezone)
    end_date = datetime.now(tz=timezone)


    # Define a date range excluding weekends and stock market holidays
    holidays = nyse.holidays().holidays
    weekmask = 'Mon Tue Wed Thu Fri'
    business_days = pd.bdate_range(start=start_date, end=end_date, freq='C', holidays=holidays, weekmask=weekmask)

    # Get the previous business day
    previous_business_day = business_days[-2]
    return previous_business_day, business_days