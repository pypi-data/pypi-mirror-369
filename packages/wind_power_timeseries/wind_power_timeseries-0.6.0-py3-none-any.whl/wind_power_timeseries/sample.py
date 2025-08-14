"""Module used for obtaining wind power timeseries for specified wind farm."""

import pathlib
from typing import Union

import pandas as pd

from . import compute, download


def wind_power(
    windfarm: dict,
    time_start: str,
    time_end: str,
    method: str = "Ninja",
    data_path: Union[str, pathlib.Path] = None,
) -> pd.DataFrame:
    """Get normalised wind power timeseries for specified wind farm location.

    Arguments:
        windfarm (dict): Table with latitude, longitude, turbine_height. Index = wind farm identifier
        time_start (str): start time, e.g. "2022-05-01"
        time_end (str): end time, e.g. "2022-05-05"
        method (str): method used for wind speed to power conversion.
            Availble: "Ninja", "Tradewind_offshore", "Tradewind_upland", "Tradewind_lowland"
        data_path (str or pathlib.Path): where downloaded wind speed data is kept
            If data has been downloaded before, it is read from local file.

    Returns:
        numpy.array - containing normalised wind power for wind farm location, index=time
    """

    df_windfarms = pd.DataFrame([windfarm]).set_index("id")
    if data_path is None:
        data_path = pathlib.Path("downloaded_nora3").mkdir(parents=True, exist_ok=True)
    else:
        data_path = pathlib.Path(data_path)

    wind_data = download.retrieve_nora3(df_windfarms, time_start, time_end, use_cache=True, data_path=data_path)

    if method == "Ninja":
        my_power_function = compute.func_ninja_compute_power
        my_args = {"turbine_power_curve": compute.get_power_curve(name="VestasV80")}
    elif method in ["Tradewind_offshore", "Tradewind_upland", "Tradewind_lowland"]:
        my_power_function = compute.func_power_curve(compute.get_power_curve(method))
        my_args = {}
    else:
        raise ValueError(f"Unknown power conversion method: {method}")

    # Compute power
    windpower = compute.compute_power(
        df_windfarms, wind_data, power_function=my_power_function, power_function_args=my_args
    )

    # Extract profile and convert to numpy array
    profile = windpower[windfarm["id"]].to_numpy()

    # Ensure that the normalized profile does not exceed 1 (this is done to take roundoff errors into account)
    profile[profile > 1] = 1

    return profile
