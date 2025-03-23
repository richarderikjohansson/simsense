import pandas as pd
import numpy as np
from simsense.chrono import generate_date_range, make_unix_time


class Dotted:
    """Turns keys of a dictionary into attributes"""

    def __init__(self, dictionary):
        # unravels nested dictionaries with recursion
        for key, value in dictionary.items():
            if isinstance(value, dict):
                value = Dotted(value)
            self.__dict__[key] = value

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def attr(self, key=None):
        """
        Return the attributes of the object back as keys. Useful if
        you have to represent the attributes as keys again in a loop
        for example

        Returns:
            (dict_keys): attributes as keys

        """
        return self.__dict__.keys()

    def to_dict(self):
        return self.__dict__


def group_vmr_by_date(list_of_retrievals):
    """Write doc string"""
    grouped = {}
    datetime_list = []

    for retrieval in list_of_retrievals:
        apriori = retrieval["vmr_field"][0, :, 0, 0]
        state = retrieval["x"][0:41]
        vmr = apriori * state
        date_key = retrieval["measurement_start"].date()

        if date_key not in grouped:
            grouped[date_key] = []
            datetime_list.append(date_key)

        grouped[date_key].append(vmr)
    return datetime_list, list(grouped.values())


def make_vmr_csv(retrievals, start_date, end_date, filename):
    """Write doc string"""

    daterange = generate_date_range(start_date=start_date, end_date=end_date)
    unix_time = make_unix_time(daterange=daterange)
    datetimes, vmr_grouped_by_date = group_vmr_by_date(retrievals)

    list_daily_mean_vmr = [np.mean(day, axis=0) for day in vmr_grouped_by_date]
    daily_vmr_dataframe = pd.DataFrame()

    for datetime, daily_mean_vmr in zip(datetimes, list_daily_mean_vmr):
        daily_vmr_dataframe[datetime] = daily_mean_vmr

    daily_vmr_dataframe = daily_vmr_dataframe.reindex(
        columns=daterange, fill_value=np.nan
    )
    daily_vmr_dataframe["altitude"] = make_mean_altitude(retrievals=retrievals)
    daily_vmr_dataframe.to_csv(f"{filename}.csv", index=False)

    daily_time_dataframe = pd.DataFrame({"datetime": daterange, "unix_time": unix_time})
    daily_time_dataframe.to_csv(f"{filename}_time.csv")


def make_mean_altitude(retrievals: list) -> list:
    altitude_array = np.array(
        [retrieval["z_field"][:, 0, 0] for retrieval in retrievals]
    )
    altitude_mean = altitude_array.mean(axis=0)
    return altitude_mean
