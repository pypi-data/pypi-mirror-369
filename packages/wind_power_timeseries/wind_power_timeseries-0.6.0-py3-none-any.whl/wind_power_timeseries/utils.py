"""Helper functionality."""

import pandas as pd
from metocean_api import ts


class Timeseries_products:
    ERA5 = "ERA5"
    NORA3 = "NORA3_wind_sub"


def validate_windfarm_data(wind_farms):
    """Check that given wind farm data is OK

    Arguments:
        wind_farms (pandas.DataFrame): Properties of each wind farm.
            The dataframe contains at least the following columns:

               * `lat`, `lon`: latitude and longitude in degrees
               *  `turbine_height`: turbine hub height in metres

    Raises:
        TypeError: If input is of wrong type
        ValueError: If input contains invalid values

    """

    if not isinstance(wind_farms, pd.DataFrame):
        raise TypeError("wind_farms must be a pandas DataFrame.")

    if not all(c in wind_farms.columns for c in ["lat", "lon", "turbine_height"]):
        raise ValueError("wind_farms must have columns lat,lon,turbine_height")

    if (wind_farms["lat"] > 90).any() or (wind_farms["lat"] < -90).any():
        raise ValueError("Latitude must be in range [-90,90]")

    if (wind_farms["lon"] > 180).any() or (wind_farms["lon"] < -180).any():
        raise ValueError("Longitude must be in range [-180,180]")

    if (wind_farms["turbine_height"] < 10).any() or (wind_farms["turbine_height"] > 300).any():
        raise ValueError("turbine_height must be in range [10,300]")


def validate_timeseries_data(ts_data_dict, dict_keys=None):
    """Check that given time series data is as expected

    Arguments:
        ts_data_dict (dict): Dict of timeseries data.

    Raises:
        TypeError: If input is of wrong type
        ValueError: If input contains invalid values
    """

    if not isinstance(ts_data_dict, dict):
        raise TypeError("time series data must be dictionary of metocean_api.ts.TimeSeries objects")

    if dict_keys:
        if not all(k in ts_data_dict for k in dict_keys):
            raise ValueError("not all keys are present in time series data")

    for key, ts_data in ts_data_dict.items():
        if not isinstance(ts_data, ts.TimeSeries):
            raise TypeError("time series object must be of type metocean_api.ts.TimeSeries")

        if not hasattr(ts_data, "data"):
            raise AttributeError("invalid time series object.")

        if ts_data.data is None:
            raise ValueError("time series object is empty.")
