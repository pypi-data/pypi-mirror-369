from datetime import datetime
from math import floor
from time import time, localtime


# Accepted time/date formats (all functions rely on this list)
TIME_FORMATS = [
    "%H:%M",
    "%H:%M:%S",
    "%H:%M:%S:%f",
    "%H:%M, %d.%m.",
    "%H:%M, %d.%m.%y",
    "%H:%M, %d.%m.%Y",
    "%H:%M:%S, %d.%m.",
    "%H:%M:%S, %d.%m.%y",
    "%H:%M:%S, %d.%m.%Y",
    "%H:%M:%S:%f, %d.%m.",
    "%H:%M:%S:%f, %d.%m.%y",
    "%H:%M:%S:%f, %d.%m.%Y"
]


def get_time_from_string(t_str):
    """
    Parse a flexible time/date string into a datetime object.

    Missing date values default to today's date.
    Missing year values default to the current year.
    See TIME_FORMATS for supported formats.

    Parameters
    ----------
    t_str : str
        The time/date string to parse.

    Returns
    -------
    datetime
        The parsed datetime object.

    Raises
    ------
    ValueError
        If the input string doesn't match any supported format.
    """
    t_str = t_str.strip()
    for fmt in TIME_FORMATS:
        try:
            dt = datetime.strptime(t_str, fmt)
            if "%Y" not in fmt and "%y" not in fmt:
                dt = dt.replace(year=datetime.now().year)
            if "%d" not in fmt:
                now = datetime.now()
                dt = dt.replace(year=now.year, month=now.month, day=now.day)
            return dt
        except ValueError:
            continue
    raise ValueError(f"Time format not recognized: {t_str}")


def get_string_from_time(dt, include_ms=False, include_date=True):
    """
    Format a datetime object into a string.

    Parameters
    ----------
    dt : datetime
        The datetime object to format.
    include_ms : bool, optional
        Whether to include milliseconds (default: False).
    include_date : bool, optional
        Whether to include the date in 'DD.MM.YYYY' format (default: True).

    Returns
    -------
    str
        The formatted time/date string.
    """
    if include_date:
        return dt.strftime("%H:%M:%S:%f, %d.%m.%Y" if include_ms else "%H:%M:%S, %d.%m.%Y")
    else:
        return dt.strftime("%H:%M:%S:%f" if include_ms else "%H:%M:%S")


def time_diff_seconds(time1_str, time2_str=None):
    """
    Calculate the difference in seconds between two time points.

    Parameters
    ----------
    time1_str : str
        The first time/date string (see TIME_FORMATS for supported formats).
    time2_str : str, optional
        The second time/date string. If omitted, the current time is used.

    Returns
    -------
    float
        The time difference in seconds. Positive if time2 is after time1,
        negative if time2 is before time1.

    Raises
    ------
    ValueError
        If either input string doesn't match any supported format.
    """
    dt1 = get_time_from_string(time1_str)
    dt2 = get_time_from_string(time2_str) if time2_str else datetime.now()
    return (dt2 - dt1).total_seconds()


def get_time_delta_prettystring(
    start: float,
    end: float = None,
    start_is_delta: bool = False,
    include_milliseconds: bool = False,
    add_days_to_hours: bool = False,
    include_days: bool = True,
):
    """Get the time difference in the form of hours:minutes:seconds{:milliseconds}

    Args:
        start (float): first point in time
        end (float, optional): second point in time. Defaults to None meaning now if not start_is_delta.
        start_is_delta (bool, optional): set True if you input the difference. Defaults to False.
        include_milliseconds (bool, optional): adds ":milliseconds". Defaults to False.
        include_days (bool, optional): adds days. Defaults to True.
        add_days_to_hours (bool, optional): enlarges hours to inlude the days. Defaults to False.

    Returns:
        str: time difference in the form of hours:minutes:seconds{:milliseconds}
    """
    d, h, m, s, ms = 60 * 60 * 24, 60 * 60, 60, 1, 0.001
    if end == None:
        current = time()
    else:
        current = end
    dr, hr, mr, sr, msr = 365, 24, 60, 60, 1000
    if start_is_delta:
        delta = start
    else:
        delta = current - start
    milliseconds = floor(delta // ms % msr)
    seconds = floor(delta // s % sr)
    minutes = floor(delta // m % mr)
    hours = floor(delta // h % hr)
    days = floor(delta // d)
    if add_days_to_hours:
        hours += 24 * days

    milliseconds = str(milliseconds)
    while len(milliseconds) < 3:
        milliseconds = "0" + milliseconds
    seconds = str(seconds)
    if len(seconds) < 2:
        seconds = "0" + seconds
    minutes = str(minutes)
    if len(minutes) < 2:
        minutes = "0" + minutes
    hours = str(hours)
    if len(hours) < 2:
        hours = "0" + hours
    days = str(days) + ":"
    if days == "0:" or not include_days:
        days = ""

    if not include_milliseconds:
        return f"{days}{hours}:{minutes}:{seconds}"
    else:
        return f"{days}{hours}:{minutes}:{seconds}:{milliseconds}"


def get_time_delta_prettystring2(
    start: float,
    end: float = None,
    start_is_delta: bool = False,
    include_milliseconds: bool = False,
    zeros: bool = True,
    long_units: bool = False,
    add_days_to_hours: bool = False,
    include_days: bool = True,
):
    """Get the time difference in the form of [hours] h [minutes] min [seconds] s {[milliseconds] ms}

    Args:
        start (float): first point in time
        end (float, optional): second point in time. Defaults to None meaning now if not start_is_delta.
        start_is_delta (bool, optional): set True if you input the difference. Defaults to False.
        include_milliseconds (bool, optional): adds ":milliseconds". Defaults to False.
        zeros (bool, optional): adds 0 to keep a standard length. Defaults to True.
        long_units (bool, optional): use hours, minutes, seconds, milliseconds instead of h, min, s, ms. Defaults to True.
        include_days (bool, optional): adds days. Defaults to True.
        add_days_to_hours (bool, optional): enlarges hours to inlude the days. Defaults to False.

    Returns:
        str: time difference in the form of [hours] h [minutes] min [seconds] s {[milliseconds] ms}
    """
    d, h, m, s, ms = 60 * 60 * 24, 60 * 60, 60, 1, 0.001
    if end == None:
        current = time()
    else:
        current = end
    dr, hr, mr, sr, msr = 365, 24, 60, 60, 1000
    if start_is_delta:
        delta = start
    else:
        delta = current - start
    milliseconds = floor(delta // ms % msr)
    seconds = floor(delta // s % sr)
    minutes = floor(delta // m % mr)
    hours = floor(delta // h % hr)
    days = floor(delta // d)
    if add_days_to_hours:
        hours += 24 * days

    if zeros:
        milliseconds = str(milliseconds)
        while len(milliseconds) < 3:
            milliseconds = "0" + milliseconds
        seconds = str(seconds)
        if len(seconds) < 2:
            seconds = "0" + seconds
        minutes = str(minutes)
        if len(minutes) < 2:
            minutes = "0" + minutes
        hours = str(hours)
        if len(hours) < 2:
            hours = "0" + hours
        days = str(days)
        if days == "0":
            days = ""

    if long_units:
        d, h, min, s, ms = "days", "hours", "minutes", "seconds", "milliseconds"
    else:
        d, h, min, s, ms = "d", "h", "min", "s", "ms"

    if not include_days or days == "":
        days = ""
    else:
        days = days + " " + d + " "

    if not include_milliseconds:
        return f"{days}{hours} {h} {minutes} {min} {seconds} {s}"
    else:
        return f"{days}{hours} {h} {minutes} {min} {seconds} {s} {milliseconds} {ms}"


def get_year(point_of_time: float) -> int:
    local = localtime(point_of_time)
    return local.tm_year


def get_month(point_of_time: float) -> int:
    local = localtime(point_of_time)
    return local.tm_mon


def get_month_3_characters_eng(point_of_time: float) -> str:
    local = localtime(point_of_time)
    months_3c_eng = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    return months_3c_eng[local.tm_mon - 1]


def get_month_name_eng(point_of_time: float) -> str:
    local = localtime(point_of_time)
    months_eng = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    return months_eng[local.tm_mon - 1]


def get_years_day(point_of_time: float) -> int:
    local = localtime(point_of_time)
    return local.tm_yday


def get_months_day(point_of_time: float) -> int:
    local = localtime(point_of_time)
    return local.tm_mday


def get_weaks_day(point_of_time: float) -> int:
    local = localtime(point_of_time)
    return local.tm_wday


def get_weeks_day_3_characters_eng(point_of_time: float) -> str:
    local = localtime(point_of_time)
    week_3c_eng = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    return week_3c_eng[local.tm_wday - 1]


def get_weeks_day_name_eng(point_of_time: float) -> str:
    local = localtime(point_of_time)
    week_eng = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    return week_eng[local.tm_wday - 1]


def get_hour(point_of_time: float) -> int:
    local = localtime(point_of_time)
    return local.tm_hour


def get_minute(point_of_time: float) -> int:
    local = localtime(point_of_time)
    return local.tm_min


def get_second(point_of_time: float) -> int:
    local = localtime(point_of_time)
    return local.tm_sec


def get_millisecond_not_rounded(point_of_time: float) -> float:
    return point_of_time % 1 * 1000


def get_millisecond(point_of_time: float) -> int:
    return round(point_of_time % 1 * 1000)


def get_european_date_without_0s(point_of_time: float) -> str:
    return f"{get_months_day(point_of_time)}.{get_month(point_of_time)}.{get_year(point_of_time)}"


def get_european_date_with_0s(point_of_time: float) -> str:
    str_months_day, str_month = str(get_months_day(point_of_time)), str(
        get_month(point_of_time)
    )
    while len(str_months_day) < 2:
        str_months_day = "0" + str_months_day
    while len(str_month) < 2:
        str_month = "0" + str_month
    return f"{str_months_day}.{str_month}.{get_year(point_of_time)}"


def get_american_date_without_0s(point_of_time: float) -> str:
    return f"{get_month(point_of_time)}/{get_months_day(point_of_time)}/{get_year(point_of_time)}"


def get_american_date_with_0s(point_of_time: float) -> str:
    str_months_day, str_month = str(get_months_day(point_of_time)), str(
        get_month(point_of_time)
    )
    while len(str_months_day) < 2:
        str_months_day = "0" + str_months_day
    while len(str_month) < 2:
        str_month = "0" + str_month
    return f"{str_month}/{str_months_day}/{get_year(point_of_time)}"


def get_time_string_24h_without_0s(point_of_time: float) -> str:
    return f"{get_hour(point_of_time)}:{get_minute(point_of_time)}:{get_second(point_of_time)}"


def get_time_string_24h_with_0s(point_of_time: float) -> str:
    str_hour, str_minute, str_second = (
        str(get_hour(point_of_time)),
        str(get_minute(point_of_time)),
        str(get_second(point_of_time)),
    )
    while len(str_hour) < 2:
        str_hour = "0" + str_hour
    while len(str_minute) < 2:
        str_minute = "0" + str_minute
    while len(str_second) < 2:
        str_second = "0" + str_second
    return f"{str_hour}:{str_minute}:{str_second}"


def get_time_stamp(
    point_of_time: float = None,
    zeros: bool = True,
    time_seperator: str = "-",
    date_seperator: str = "-",
    date_time_seperator: str = " - ",
    milliseconds: bool = True,
) -> str:
    """
    Get a time stamp formated like: 'year-month-day - hour-minute-second-millisecond' for example '2023-06-18 - 17-52-42-446'

    0 before the number (e.g. june -> 06) can be trashed by setting zeros to `False`
    """
    if point_of_time == None:
        point_of_time = time()
    str_months_day, str_month = str(get_months_day(point_of_time)), str(
        get_month(point_of_time)
    )
    if zeros:
        while len(str_months_day) < 2:
            str_months_day = "0" + str_months_day
        while len(str_month) < 2:
            str_month = "0" + str_month
    str_hour, str_minute, str_second, str_millisecond = (
        str(get_hour(point_of_time)),
        str(get_minute(point_of_time)),
        str(get_second(point_of_time)),
        str(get_millisecond(point_of_time)),
    )
    if zeros:
        while len(str_hour) < 2:
            str_hour = "0" + str_hour
        while len(str_minute) < 2:
            str_minute = "0" + str_minute
        while len(str_second) < 2:
            str_second = "0" + str_second
        while len(str_millisecond) < 3:
            str_millisecond = "0" + str_millisecond
    if milliseconds:
        return (
            str(get_year(point_of_time))
            + date_seperator
            + str_month
            + date_seperator
            + str_months_day
            + date_time_seperator
            + str_hour
            + time_seperator
            + str_minute
            + time_seperator
            + str_second
            + time_seperator
            + str_millisecond
        )
    else:
        return (
            str(get_year(point_of_time))
            + date_seperator
            + str_month
            + date_seperator
            + str_months_day
            + date_time_seperator
            + str_hour
            + time_seperator
            + str_minute
            + time_seperator
            + str_second
        )


def get_time_stamp2(
    point_of_time: float = None,
    zeros: bool = True,
    time_seperator: str = "-",
    date_seperator: str = "-",
    date_time_seperator: str = " - ",
) -> str:
    """
    Get a time stamp formated like: 'hour-minute-second-millisecond - year-month-day' for example '17-52-42-446 - 18-06-2023'

    0 before the number (e.g. june -> 06) can be trashed by setting zeros to `False`
    """
    if point_of_time == None:
        point_of_time = time()
    str_months_day, str_month = str(get_months_day(point_of_time)), str(
        get_month(point_of_time)
    )
    if zeros:
        while len(str_months_day) < 2:
            str_months_day = "0" + str_months_day
        while len(str_month) < 2:
            str_month = "0" + str_month
    str_hour, str_minute, str_second, str_millisecond = (
        str(get_hour(point_of_time)),
        str(get_minute(point_of_time)),
        str(get_second(point_of_time)),
        str(get_millisecond(point_of_time)),
    )
    if zeros:
        while len(str_hour) < 2:
            str_hour = "0" + str_hour
        while len(str_minute) < 2:
            str_minute = "0" + str_minute
        while len(str_second) < 2:
            str_second = "0" + str_second
        while len(str_millisecond) < 3:
            str_millisecond = "0" + str_millisecond
    return (
        str_hour
        + time_seperator
        + str_minute
        + time_seperator
        + str_second
        + time_seperator
        + str_millisecond
        + date_time_seperator
        + str_months_day
        + date_seperator
        + str_month
        + date_seperator
        + str(get_year(point_of_time))
    )



def get_time_stamp_s(
    point_of_time: float = None,
    zeros: bool = True,
    time_seperator: str = "-",
    date_seperator: str = "-",
    date_time_seperator: str = " - ",
) -> str:
    """
    Get a time stamp formated like: 'year-month-day - hour-minute-second' for example '2023-06-18 - 17-52-42'

    0 before the number (e.g. june -> 06) can be trashed by setting zeros to `False`
    """
    if point_of_time == None:
        point_of_time = time()
    str_months_day, str_month = str(get_months_day(point_of_time)), str(
        get_month(point_of_time)
    )
    if zeros:
        while len(str_months_day) < 2:
            str_months_day = "0" + str_months_day
        while len(str_month) < 2:
            str_month = "0" + str_month
    str_hour, str_minute, str_second = (
        str(get_hour(point_of_time)),
        str(get_minute(point_of_time)),
        str(get_second(point_of_time)),
    )
    if zeros:
        while len(str_hour) < 2:
            str_hour = "0" + str_hour
        while len(str_minute) < 2:
            str_minute = "0" + str_minute
        while len(str_second) < 2:
            str_second = "0" + str_second
    return (
        str(get_year(point_of_time))
        + date_seperator
        + str_month
        + date_seperator
        + str_months_day
        + date_time_seperator
        + str_hour
        + time_seperator
        + str_minute
        + time_seperator
        + str_second
    )


def get_time_stamp_s2(
    point_of_time: float = None,
    zeros: bool = True,
    time_seperator: str = "-",
    date_seperator: str = "-",
    date_time_seperator: str = " - ",
) -> str:
    """
    Get a time stamp formated like: 'hour-minute-second - year-month-day' for example '17-52-42 - 18-06-2023'

    0 before the number (e.g. june -> 06) can be trashed by setting zeros to `False`
    """
    if point_of_time == None:
        point_of_time = time()
    str_months_day, str_month = str(get_months_day(point_of_time)), str(
        get_month(point_of_time)
    )
    if zeros:
        while len(str_months_day) < 2:
            str_months_day = "0" + str_months_day
        while len(str_month) < 2:
            str_month = "0" + str_month
    str_hour, str_minute, str_second = (
        str(get_hour(point_of_time)),
        str(get_minute(point_of_time)),
        str(get_second(point_of_time)),
    )
    if zeros:
        while len(str_hour) < 2:
            str_hour = "0" + str_hour
        while len(str_minute) < 2:
            str_minute = "0" + str_minute
        while len(str_second) < 2:
            str_second = "0" + str_second
    return (
        str_hour
        + time_seperator
        + str_minute
        + time_seperator
        + str_second
        + date_time_seperator
        + str_months_day
        + date_seperator
        + str_month
        + date_seperator
        + str(get_year(point_of_time))
    )


def get_time_stamp_date(
    point_of_time: float = None,
    zeros: bool = True,
    seperator: str = "-",
) -> str:
    """
    Get a time stamp formated like: 'year-month-day' for example '2023-06-18'

    0 before the number (e.g. june -> 06) can be trashed by setting zeros to `False`
    """
    if point_of_time == None:
        point_of_time = time()
    str_months_day, str_month = str(get_months_day(point_of_time)), str(
        get_month(point_of_time)
    )
    if zeros:
        while len(str_months_day) < 2:
            str_months_day = "0" + str_months_day
        while len(str_month) < 2:
            str_month = "0" + str_month
    str_hour, str_minute, str_second = (
        str(get_hour(point_of_time)),
        str(get_minute(point_of_time)),
        str(get_second(point_of_time)),
    )
    if zeros:
        while len(str_hour) < 2:
            str_hour = "0" + str_hour
        while len(str_minute) < 2:
            str_minute = "0" + str_minute
        while len(str_second) < 2:
            str_second = "0" + str_second
    return (
        str(get_year(point_of_time))
        + seperator
        + str_month
        + seperator
        + str_months_day
    )


def date_to_total_seconds(day, month, year, hour, minute, second):
    dt = datetime(year, month, day, hour, minute, second)
    return dt.timestamp()


def total_seconds_to_date(s, microseconds=False):
    if not microseconds:
        return str(datetime.fromtimestamp(round(s)))
    else:
        return str(datetime.fromtimestamp(s))


if __name__ == "__main__":
    pass
