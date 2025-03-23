from datetime import datetime, timedelta


def make_datetime_objects(measurement: dict) -> dict:
    """Write doc string"""
    start_date = measurement["start_date"].decode("utf-8")
    start_time = measurement["start_time"].decode("utf-8")
    end_date = measurement["end_date"].decode("utf-8")
    end_time = measurement["end_time"].decode("utf-8")

    start_dt = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H-%M-%S")
    end_dt = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H-%M-%S")

    measurement["measurement_start"] = start_dt
    measurement["measurement_end"] = end_dt

    return measurement


def make_datetime_objects_from_path(paths: list) -> list:
    datetimes = []
    for path in paths:
        file = path.split("/")[-1]
        filename = file.split(".")[0]
        dt_len = 19
        date_string = filename[-dt_len:]
        dt = datetime.strptime(date_string, "%Y-%m-%d_%H-%M-%S")
        datetimes.append(dt)
    return datetimes


def generate_date_range(start_date: datetime, end_date: datetime) -> list:
    """
    Generate a list of datetime objects between start_date and end_date (inclusive).

    Parameters
    ----------
    start_date: The starting date.
    end_date: The ending date.

    Returns
    -------
    dates: A list of datetime objects between start_date and end_date.
    """
    dates = []
    current_date = start_date

    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)

    return dates


def make_unix_time(daterange: list) -> list:
    """Write doc string"""
    unix_time = [dt.timestamp() for dt in daterange]
    return unix_time
