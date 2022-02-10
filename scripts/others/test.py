from fameio.source.time import FameTime, Constants
import datetime as dt
import math


def roundup(x):
    return round(x / 1000.0) * 1000

def convert_fame_time_step_to_datetime(fame_time_steps: int) -> str:
    """Converts given `fame_time_steps` to corresponding real-world datetime string"""
    years_since_start_time = math.floor(fame_time_steps / Constants.STEPS_PER_YEAR)
    current_year = years_since_start_time + Constants.FIRST_YEAR
    beginning_of_year = dt.datetime(year=current_year, month=1, day=1, hour=0, minute=0, second=0)
    steps_in_current_year = (fame_time_steps - years_since_start_time * Constants.STEPS_PER_YEAR)
    seconds_in_current_year = steps_in_current_year / Constants.STEPS_PER_SECOND
    simulatedtime = beginning_of_year + dt.timedelta(seconds=seconds_in_current_year)
    tiemporounded = simulatedtime.replace(second=0, microsecond=0, minute=0, hour=simulatedtime.hour) + dt.timedelta(
        hours=simulatedtime.minute // 30)
    return tiemporounded.strftime('%Y-%m-%dT%H:%M:%S')

# agent id 53 last hour

test = 630718204
rounded = roundup(test)
result = convert_fame_time_step_to_datetime(rounded)
print(result)