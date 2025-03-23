from datetime import datetime
import numpy as np

from simsense.data.tools import (
    find_hdf5_files,
    read_measurement_or_retrieval,
    read_simulation,
    set_config,
)
from simsense.data.transforms import Dotted
from simsense.chrono import make_datetime_objects_from_path
import matplotlib.pyplot as plt


class RealDataManager:
    """A class to set paths to hdf5 data

    Attributes
    ----------
    data_path: Absolute path to the top level directory where the data is stored
    data_source: Source of the dataset, can be retrieval, simulated of measurement data
    config: Name of the configuration if the data is retrieval data
    paths: Absolute paths to files
    convergence_flag: For retrieval data; check if sort_data method should check for convergence_flag

    Methods
    -------
    sort_data(): Checks if data have retrieval with config and can also check convergence
    read_data(): Reads the data and return a list of Dotted objects

    TODO
    ----
    1. Make sure that I can read all kinds of data, not only retrieval or measurement data.
    2. Add more methods for data transforms
    """

    def __init__(self, paths: list, name: str = None):
        self.paths = np.array(paths)
        if name.endswith(".json"):
            self.config = set_config(name)
            self.name = name.split(".")[0]
        else:
            self.name = name
        self.datetimes = np.array(make_datetime_objects_from_path(self.paths))

    def to_dict(self, dotted=False, filt=None) -> dict:
        self.dictionary = {}
        self.dotted = dotted
        if filt is not None:
            self.paths = self.paths[filt]
        match dotted:
            case True:
                for path in self.paths:
                    data = read_measurement_or_retrieval(
                        filename=path, dsource=self.name
                    )
                    self.dictionary[data["measurement_start"]] = Dotted(data)

            case False:
                for path in self.paths:
                    data = read_measurement_or_retrieval(
                        filename=path, dsource=self.name
                    )
                    self.dictionary[data["measurement_start"]] = data
        return self.dictionary

    def filter_date(self, start: datetime, stop: datetime):
        if start is stop:
            filt = (self.datetimes == start)
            self.paths = self.paths[filt]
        else:
            filt = (self.datetimes >= start) & (self.datetimes <= stop)
            self.paths = self.paths[filt]

    def get_dataset(self, dt, dotted):
        if dt in self.datetimes:
            self.filter_date(start=dt, stop=dt)
            return self.to_dict(dotted=True)
        else:
            print(f"{dt} not in path")

    def get_paths(self) -> list:
        """Method to return the paths as a list

        Returns
        -------
        paths: the paths to the files read

        """
        return self.paths


class SimulationManager:
    def __init__(self, data_path, names=None):
        self.data_path = data_path
        self.paths = find_hdf5_files(self.data_path)
        self.names = names

    def to_dict(self):
        self.dictionary = {}
        match self.names:
            case None:
                for path in self.paths:
                    name = self._get_name(path)
                    self.dictionary[name] = read_simulation(path)
                return self.dictionary
            case _:
                assert len(self.names) == len(self.paths), (
                    "Inconsistent size between 'names' and 'paths'"
                )
                for name, path in zip(self.names, self.paths):
                    self.dictionary[name] = read_simulation(path)
        return self.dictionary

    def to_dotted(self):
        self.dotted = Dotted({})
        match self.names:
            case None:
                for path in self.paths:
                    name = self._get_name(path)
                    self.dotted.__dict__[name] = Dotted(read_simulation(path))
                return self.dotted
            case _:
                assert len(self.names) == len(self.paths), (
                    "Inconsistent size between 'names' and 'paths'"
                )
                for name, path in zip(self.names, self.paths):
                    self.dotted.__dict__[name] = Dotted(read_simulation(path))

        return self.dotted

    def get_simulation(self, name):
        self.dictionary = self.to_dict()
        return self.dictionary[name]

    def get_names_from_filenames(self):
        self.names = []
        for path in self.paths:
            self.names.append(self._get_name(path))
        return self.names

    def set_names(self, names):
        self.names = []
        for name in names:
            self.names.append(name)

    def _get_name(self, path):
        filename = path.split("/")[-1]
        name = filename.split(".")[0]
        return name


class DataAnalyzer:
    def __init__(self, data):
        self.data = data

    def invert_yaxis(self):
        return plt.gca().invert_yaxis()

