import json
import os
import subprocess

import h5py

from simsense.chrono import make_datetime_objects


def find_hdf5_files(
    data_path: str,
    convergence: bool = False,
    sort: bool = False,
    config: str = None,
    name: str = None,
) -> list:
    """Function to find all paths from an top level directory

    Parameters
    ----------
    data_path: path to the top level directory

    Returns
    -------
    paths: list of all paths to .hdf5 files

    """
    if config.endswith(".json"):
        config = set_config(config)
    paths = []
    for dirpath, _, filenames in os.walk(data_path):
        for file in filenames:
            if file.endswith(".hdf5"):
                path = os.path.abspath(os.path.join(dirpath, file))
                if convergence and sort:
                    if check_convergence(path, config) and check_retrieval_status(path, config):
                        paths.append(path)
                if sort and not convergence:
                    if check_retrieval_status(path, config):
                        paths.append(path)
                    else:
                        paths.append(path)
    return sorted(paths)


def get_git_root() -> str:
    """Function to find path to top level directory of git repository

    Returns
    -------
    git_root: path to top level in git repository

    """
    git_root = (
        subprocess.Popen(
            ["git", "rev-parse", "--show-toplevel"], stdout=subprocess.PIPE
        )
        .communicate()[0]
        .rstrip()
        .decode("utf-8")
    )
    return git_root


def read_measurement_or_retrieval(filename: str, dsource: str) -> dict:
    """Function to read data from .hdf5 file

    The function can handle measurement and data from pyarts

    Parameters
    ----------
    filename: absolute path to the file to read.
    dsource: data source, like "kimra_data", "mira_data" etc.

    """

    # shit implementing!
    with h5py.File(filename, "r") as file:
        data = {}
        names = file.keys()
        if "kimra_data" in names and dsource != "kimra_data":
            measurement = {
                "start_date": file["kimra_data"]["start_date"][()],
                "start_time": file["kimra_data"]["start_time"][()],
                "end_date": file["kimra_data"]["end_date"][()],
                "end_time": file["kimra_data"]["end_time"][()],
            }

        if "mira2_data" in names and dsource != "mira2_data":
            measurement = {
                "start_date": file["mira2_data"]["start_date"][()],
                "start_time": file["mira2_data"]["start_time"][()],
                "end_date": file["mira2_data"]["end_date"][()],
                "end_time": file["mira2_data"]["end_time"][()],
            }

        for key in file[dsource].keys():
            if key != "config":
                data[key] = file[dsource][key][()]
        if dsource == "mira2_data" or dsource == "kimra_data":
            data = make_datetime_objects(measurement=data)
        else:
            measurement = make_datetime_objects(measurement)
            data["measurement_start"] = measurement["measurement_start"]
            data["measurement_end"] = measurement["measurement_end"]
        return data


def read_simulation(filename: str) -> dict:
    with h5py.File(filename, "r") as file:
        data = {}
        for key in file.keys():
            data[key] = file[key][()]
        return data


def check_convergence(filename: str, config: dict) -> bool:
    """Function to check that a pyarts retrieval have converged

    Parameters
    ----------
    filename: path to the .hdf5 file that should be checked
    config: configuration used for the retrieval

    Returns
    -------
    : bool if the retrieval converged or not

    """
    with h5py.File(filename, "r") as dataset:
        keys = dataset.keys()
        if config["fieldname"] in keys:
            if "convergence" in dataset[config["fieldname"]].attrs.keys():
                if dataset[config["fieldname"]].attrs["convergence"] == 0.0:
                    return True
        return False


def check_retrieval_status(filename: str, config: dict) -> bool:
    """Function to check if a retrieval have been done

    Parameters
    ----------
    filename: path to the .hdf5 file that should be checked
    config: configuration used for the retrieval

    Returns
    : bool if the file contain a retrieval with the configuration
    """
    with h5py.File(filename, "r") as dataset:
        keys = dataset.keys()
        if config["fieldname"] in keys:
            return True
        return False


def set_config(config: str) -> dict:
    """Function to set a configuration

    Parameters
    ----------
    config: path to the .json configuration to be set

    Returns
    -------
    dct: configuration read from the .json configuration
    """

    # get path to the root of git repo
    git_root = get_git_root()
    config_path = find_config_file(config_name=config)
    if config_path is None:
        return None

    # open json file and returns dictionary
    with open(config_path) as json_file:
        dct = json.load(json_file)

    # check 'abs_lookup' in configuration file and set correct path
    for key in dct.keys():
        match key:
            case "abs_lookup":
                file = dct[key]
                dct[key] = f"{git_root}/assets/LUT/{file}"
            case "atm_profile":
                profile = dct[key]
                dct[key] = f"{git_root}/assets/profiles/{profile}/{profile}"
            case "p_grid":
                file = dct[key]
                dct[key] = f"{git_root}/assets/general/{file}"
            case "f_grid":
                file = dct[key]
                dct[key] = f"{git_root}/general/{file}"
            case "lines":
                lines = dct[key]
                dct[key] = f"{git_root}/assets/{lines}/"

    return dct


def find_config_file(config_name: str) -> str:
    """Function to find configuration

    Parameters
    ----------
    config_name: full name of the configuration

    Returns
    -------
    : absolute path to the configuration file

    """
    config_path = f"{get_git_root()}/assets/configs"
    for dirpath, _, filenames in os.walk(config_path):
        for file in filenames:
            if file == config_name:
                return os.path.abspath(os.path.join(dirpath, file))
