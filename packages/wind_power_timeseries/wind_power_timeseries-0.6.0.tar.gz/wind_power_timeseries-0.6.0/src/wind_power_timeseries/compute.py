"""Methods for computing wind power from wind speed data."""

import pathlib

import numpy as np
import pandas as pd
import scipy

import wind_power_timeseries.utils as utils


def compute_power(wind_farms, windspeed_data, power_function, power_function_args=None):
    """Compute electric power from wind speed data

    Arguments:
        wind_farms (pandas.DataFrame): Wind frams and their properties.
            The dataframe contains the following columns:

                * lat, lon: latitude and longitude in degrees
                * orientation: degrees from north, typically aligned with dominant wind direction
                * shape: aspect ratio, number of columns (i.e. number of turbines in a row) divided by number of rows of turbines
                * turbine_height: turbine hub height in metres
        windspeed_data (dict): metocean_api.ts.TimeSeries objects; dictionary keys are wind_farm id's
        power_function (function) : function that can compute power from wind speed and other possibly other input parameters
        power_function_args (dict) : additional parameters to power_curve method

    Returns:
        dict of pandas.DataFrame objects with wind power time-series for each wind farm

        Wind power is normalised with values in the range [0,1]
    """

    # Check input data and raise exception if invalid
    utils.validate_windfarm_data(wind_farms)
    utils.validate_timeseries_data(windspeed_data)

    # if (windspeed_data is None) and (path_windspeed_data is None):
    #    raise ValueError("You must specify windspeed_data or path_windspeed_data")
    # elif (windspeed_data is not None) and (path_windspeed_data is not None):
    #    raise ValueError("You cannot specify both windspeed_data and path_windspeed_data. Only one of them")
    if power_function_args is None:
        power_function_args = dict()

    time_index = windspeed_data[list(windspeed_data.keys())[0]].data.index
    wind_powers = pd.DataFrame(index=time_index)
    for id, wind_farm in wind_farms.iterrows():
        ts_windspeed = windspeed_data[id]
        turbine_height = wind_farm["turbine_height"]
        ts_at_hub = _get_at_hub(ts_windspeed, turbine_height)
        # arguments for power fuction:
        power_function_args["windspeed_at_hub"] = ts_at_hub["windspeed_at_hub"]
        power_function_args["winddirection_at_hub"] = ts_at_hub["winddirection_at_hub"]
        if ("shape" in wind_farm) and ("orientation" in wind_farm):
            power_function_args["windfarm_shape"] = wind_farm["shape"]
            power_function_args["windfarm_orientation"] = wind_farm["orientation"]

        # Use supplied power curve function to compute power from wind speed and other parameters
        power = power_function(**power_function_args)
        # power = power_from_windspeed(power_curve, windspeed_at_hub, winddirection_at_hub, windfarm_orientation,windfarm_shape)
        wind_powers[id] = power
    return wind_powers


def _get_at_hub(ts_wind, turbine_height):
    product = ts_wind.product
    if product == utils.Timeseries_products.NORA3:
        alpha, z1, u1 = _power_law_exponent_nora3(ts_wind, turbine_height)
        windspeed_at_hub = _power_law(z=turbine_height, u_0=u1, z_0=z1, alpha=alpha)
        winddirection_at_hub = _wind_direction_interpolation_nora3(ts_wind, turbine_height)
    elif product == utils.Timeseries_products.ERA5:
        alpha, z1, u1 = _power_law_exponent_era5(ts_wind, turbine_height)
        windspeed_at_hub = _power_law(z=turbine_height, u_0=u1, z_0=z1, alpha=alpha)
        winddirection_at_hub = _wind_direction_interpolation_era5(ts_wind, turbine_height)
    else:
        raise ValueError(f"Unknown timeseries product type: {product}")
    # additional arguments:
    df_hub = pd.DataFrame()
    df_hub["windspeed_at_hub"] = windspeed_at_hub
    df_hub["winddirection_at_hub"] = winddirection_at_hub
    return df_hub


def get_power_curve(name):
    """Get pre-defined power curves

    Arguments:
        name (str): name of power curve. Available values are:
            'VestasV80',
            'Tradewind_lowland', 'Tradewind_upland', 'Tradewind_offshore', 'Tradewind_offshore_2030'
            'IEA_15MW_240_RWT', 'IEA_10MW_198_RWT', 'NREL_5MW_126_RWT', 'DTU_10MW_178_RWT'

    Returns:
        pandas.Series - Lookup table with wind speeds as index and normalised power output as values.
    """
    if name == "VestasV80":
        # from here http://windatlas.xyz/turbine/?name=Vestas%20V80-2000 (page source file)
        # fmt: off
        powercurve = pd.Series(
                index= [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5, 15.0, 15.5, 16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 19.5, 20.0, 20.5, 21.0, 21.5, 22.0, 22.5, 23.0, 23.5, 24.0, 24.5, 25.0, 25.5, 26.0, 26.5, 27.0, 27.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 31.0, 31.5, 32.0, 32.5, 33.0, 33.5, 34.0, 34.5, 35.0],
                data = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 35.0, 70.0, 117.0, 165.0, 225.0, 285.0, 372.0, 459.0, 580.0, 701.0, 832.0, 964.0, 1127.0, 1289.0, 1428.0, 1567.0, 1678.0, 1788.0, 1865.0, 1941.0, 1966.0, 1990.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            )/2000
        # fmt: on
    elif name[:9] == "Tradewind":
        powercurve_table_tradwind = pd.read_csv(
            pathlib.Path(__file__).parent / "powercurves" / "wind_powercurves_tradewind.csv", index_col=0
        )
        subname = name[10:]
        powercurve = powercurve_table_tradwind[subname]
    elif name == "IEA_15MW_240_RWT":
        # https://github.com/NREL/turbine-models/blob/master/turbine_models/data/Offshore/IEA_15MW_240_RWT.csv
        data = pd.read_csv(pathlib.Path(__file__).parent / "powercurves" / f"{name}.csv", index_col=0)
        powercurve = data["Power [kW]"] / 15000
    elif name == "IEA_10MW_198_RWT":
        data = pd.read_csv(pathlib.Path(__file__).parent / "powercurves" / f"{name}.csv", index_col=0)
        powercurve = data["Power [kW]"] / 10638  # max output
    elif name == "NREL_5MW_126_RWT":
        data = pd.read_csv(pathlib.Path(__file__).parent / "powercurves" / f"{name}_corrected.csv", index_col=0)
        powercurve = data["Power [kW]"] / 5000
    elif name == "DTU_10MW_178_RWT":
        data = pd.read_csv(pathlib.Path(__file__).parent / "powercurves" / f"{name}_v1.csv", index_col=0)
        powercurve = data["Power [kW]"] / 10638
    else:
        raise ValueError(f"Unknown power curve: {name}")
    return powercurve


def func_power_curve(turbine_power_curve, sigma=0):
    """Get power curve as function from lookup table, using Gauss-filtering if sigma>0

    Arguments:
        turbine_power_curve (pandas.Series): Lookup table with wind speeds as index
            and normalised power output as values.
        sigma (float): Standard deviation for filter.

    Returns:
        function to compute power from wind speed.

    """
    if sigma > 0:
        power_curve = scipy.ndimage.gaussian_filter1d(turbine_power_curve, sigma=sigma)  # 2*sigma!
    else:
        power_curve = turbine_power_curve

    func = scipy.interpolate.interp1d(turbine_power_curve.index, power_curve, fill_value=0, bounds_error=False)

    # the powercurve function needs to accept additional parameters, allthough not used
    def func_x(windspeed_at_hub, **kwargs):
        return func(windspeed_at_hub)

    return func_x


def func_ninja_compute_power(**kwargs):
    """Compute wind power as done by Renewables.ninja

    Arguments:
        windspeed_at_hub (pandas.Series): Windspeeds in m/s, index is datetime values.
        turbine_power_curve (pandas.Series): Single turbine power curve. Index is wind
            speed (m/s) and value is power output in the range [0,1].
        sigma (float): Standard deviation used for Gauss filter (m/s). Default = 2*1.17.
        wakeloss (float): Effective wind speed reduction due to wakes (m/s). Default = 0.71.

    Returns:
        pandas.sereis of wind power, with same index as windspeed.
    """
    windspeed = kwargs["windspeed_at_hub"]
    turbine_curve = kwargs["turbine_power_curve"]
    if "sigma" in kwargs:
        sigma = kwargs["sigma"]
    else:
        sigma = 2 * 1.17
    if "wakeloss" in kwargs:
        wakeloss = kwargs["wakeloss"]
    else:
        wakeloss = 0.71

    f = func_power_curve(turbine_curve, sigma)
    wind_speed_with_loss = (windspeed - wakeloss).clip(lower=0)
    wind_power = f(wind_speed_with_loss)
    df_windpower = pd.Series(index=windspeed.index, data=wind_power)
    return df_windpower


def get_3PLE(powercurve, windspeed=None):
    """Compute 3PLE powercurve from turbine power curve.

    Arguments:
        powercurve (pandas.Series): Power curve with wind speeds as index
        windspeed (list): wind speeds to use. If None, use index of powercurve

    Returns:
        pandas.Series - power curve of 3LPE model

    """
    # 3PLE
    # https://www.researchgate.net/publication/342285999_A_Review_on_Wind_Turbine_Deterministic_Power_Curve_Models
    print("WARNING - This does not work as intended. Output not to be trusted.")

    v_ip, p_ip, s_ip = _find_inflection_point(powercurve)
    p_r = 1  # rated power
    b2 = p_r
    b1 = 2 * s_ip / (p_r - p_ip)
    b0 = v_ip
    if windspeed is None:
        windspeed = powercurve.index
    power_out = b2 / (1 + np.exp(-b1 * (windspeed - b0)))
    powercurve_3PLE = pd.Series(index=windspeed, data=power_out)
    return powercurve_3PLE


def _find_inflection_point(powercurve, wspeed_min=5, wspeed_max=20):
    """Find inflection point of power curve, for use with 3PLE model

    Arguments:
        powercurve (pandas.Series): powercurve to consider
        wspeed_min, wspeed_max (float): wind speed range to consider

    Returns
        tuple (v_ip,p_ip,s) with wind speed, power and slope at inflection pint
    """
    step_ws = 0.1
    windspeed_range = np.arange(start=wspeed_min, stop=wspeed_max, step=step_ws)
    func_powercurve = func_power_curve(powercurve, sigma=0)
    raw = func_powercurve(windspeed_range)

    # smooth
    smooth = scipy.ndimage.gaussian_filter1d(raw, 2)
    # compute derivative
    smooth_d1 = np.gradient(smooth)
    # compute second derivative
    smooth_d2 = np.gradient(smooth_d1)
    # find switching points
    infls = np.where(np.diff(np.sign(smooth_d2)))[0]

    windspeed_inflection = windspeed_range[infls[0]]
    windpower_inflection = func_powercurve(windspeed_inflection)
    windpower_slope = smooth_d1[infls[0]] / step_ws
    return windspeed_inflection, windpower_inflection, windpower_slope


def _heights_below_above_nora3(height):
    """Find heights of nearest data point below and above given hub height"""
    nora3_heights_available = [10, 20, 50, 100, 250, 500, 750]
    if height <= 10:
        z1, z2 = 10, 20
    elif height > 750:
        z1, z2 = 500, 750
    else:
        z1 = 0
        for z2 in nora3_heights_available:
            if z2 >= height:
                break
            else:
                z1 = z2
    return z1, z2


def _power_law_exponent_nora3(ts, height):
    """Compute power law exponent from timeseries data"""
    # REF: https://wes.copernicus.org/articles/6/1501/2021/ (section 2.3)
    z1, z2 = _heights_below_above_nora3(height)
    # print("found height: ", height,z1,z2)
    u1 = ts.data[f"wind_speed_{z1}m"]
    u2 = ts.data[f"wind_speed_{z2}m"]
    alpha = np.log(u2 / u1) / np.log(z2 / z1)
    return alpha, z1, u1


def _power_law_exponent_era5(ts, height):
    """Compute power law exponent from timeseries data"""
    # REF: https://wes.copernicus.org/articles/6/1501/2021/ (section 2.3)
    z1 = 10
    z2 = 100
    u1 = np.sqrt(ts.data["u10"] ** 2 + ts.data["v10"] ** 2)
    u2 = np.sqrt(ts.data["u100"] ** 2 + ts.data["v100"] ** 2)
    alpha = np.log(u2 / u1) / np.log(z2 / z1)
    return alpha, z1, u1


def _power_law(z, z_0, u_0, alpha):
    """Compute wind speed at height z using power law for wind shear"""
    u = u_0 * (z / z_0) ** alpha
    return u


def _wind_direction_interpolation_nora3(ts, height):
    z1, z2 = _heights_below_above_nora3(height)
    df = pd.DataFrame()
    df["wdir1"] = ts.data[f"wind_direction_{z1}m"]
    df["wdir2"] = ts.data[f"wind_direction_{z2}m"]
    wdir = df.apply(lambda row: np.interp(x=height, xp=[z1, z2], fp=[row["wdir1"], row["wdir2"]]), axis=1)
    return wdir


def _direction_from_uv(u, v):
    """Compute direction in degrees from north from u,v components.

    wind from north = 0, wind from east = 90 deg
    u = direction towards east (x-axis), v = direction towards north (y-axis)
    """
    wind_dir_degrees = np.mod(180 + np.atan2(u, v) * 180 / np.pi, 360)
    return wind_dir_degrees


def _wind_direction_interpolation_era5(ts, height):
    # use wind direction at nearest data to turibne height (i.e. 100 m or 10 m)
    # Ref: https://confluence.ecmwf.int/pages/viewpage.action?pageId=133262398

    if np.abs(height - 100) <= np.abs(height - 10):
        z = 100
    else:
        z = 10
    wind_u = ts.data[f"u{z}"]
    wind_v = ts.data[f"v{z}"]
    wdir = _direction_from_uv(wind_u, wind_v)
    return wdir
