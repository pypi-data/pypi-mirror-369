"""Methods for retrieving wind data from public sources."""

from metocean_api import ts

from . import utils


def retrieve_nora3(locations, time_start, time_end, use_cache=True, data_path=None, reload=True, save_csv=True):
    """Download or reload NORA3 wind speed and wind direction data. Save to csv files

    Arguments:
        locations (pandas.DataFrame): Locations for which to get data. Columns are lat,lon
        time_start, time_end (str): time period to download data for
        use_cache (boolean): Whether to use local cache
        data_path (pathlib.Path): Location of where to save downloaded data (csv files)
        reload (boolean): If True, try to reload data from local CSV files
        save_csv (boolean): If True, save data to CSV files

    Returns:
        dictionary of metocean_api.ts.TimeSeries objects for each location
    """
    all_ts = retrieve_wind_data(
        locations,
        time_start,
        time_end,
        source="NORA3",
        variables=None,
        use_cache=use_cache,
        data_path=data_path,
        reload=reload,
        save_csv=save_csv,
    )
    return all_ts


def retrieve_era5(locations, time_start, time_end, use_cache=True, data_path=None, reload=True, save_csv=True):
    """Download or reload ERA5 wind speed and wind direction data. Save to csv files

    Arguments:
        locations (pandas.DataFrame): Locations for which to get data. Columns are lat,lon
        time_start, time_end (str): time period to download data for
        use_cache (boolean): Whether to use local cache
        data_path (pathlib.Path): Location of where to save downloaded data (csv files)
        reload (boolean): If True, try to reload data from local CSV files
        save_csv (boolean): If True, save data to CSV files

    Returns:
        dict of metocean_api.ts.TimeSeries objects for each location

        Columns are wind speed in u and v directions at 10 and 100 m (u100,v100,u10,v10)
    """
    era5_variables = [
        "100m_u_component_of_wind",
        "100m_v_component_of_wind",
        "10m_u_component_of_wind",
        "10m_v_component_of_wind",
    ]
    all_ts = retrieve_wind_data(
        locations,
        time_start,
        time_end,
        source="ERA5",
        variables=era5_variables,
        use_cache=use_cache,
        data_path=data_path,
        reload=reload,
        save_csv=save_csv,
    )
    return all_ts


def retrieve_wind_data(
    locations,
    time_start,
    time_end,
    source,
    variables=None,
    use_cache=True,
    data_path=None,
    reload=True,
    save_csv=True,
):
    """Retrieve wind speed and wind direction data. Save to csv files

    Arguments:
        locations (pandas.DataFrame): Locations for which to get data. Columns are lat,lon
        time_start, time_end (str): time period to download data for
        use_cache (boolean): Whether to use local cache
        data_path (pathlib.Path): Location of where to save downloaded data (csv files)
        reload (boolean): If True, reload data from local CSV files
        save_csv (boolean): If True, save data to CSV files
        source (str): Which data source ("ERA5" or "NORA3")
        variables (list of str): Which variables to retreive from the dataset. None=get all

    Returns:
        dict of metocean_api.ts.TimeSeries objects for each location
    """

    # Check input data and raise exception if invalid
    utils.validate_windfarm_data(locations)

    if source == "ERA5":
        product = utils.Timeseries_products.ERA5
    elif source == "NORA3":
        product = utils.Timeseries_products.NORA3
    else:
        raise ValueError(f"Unknown source {source}.")

    if data_path is not None:
        # create folder if it does not exist:
        data_path.mkdir(parents=True, exist_ok=True)
    all_ts = dict()
    for i, row in locations.iterrows():
        lat = row["lat"]
        lon = row["lon"]
        ts_data = ts.TimeSeries(
            lon=lon,
            lat=lat,
            start_time=time_start,
            end_time=time_end,
            product=product,
            variable=variables,
            datafile=None,
        )
        if data_path is not None:
            ts_data.datafile = data_path / ts_data.datafile
        if reload:
            try:
                ts_data.load_data(local_file=ts_data.datafile)
            except FileNotFoundError:
                # local file not found, import from server.
                ts_data.import_data(save_csv=save_csv, save_nc=False, use_cache=use_cache)
        else:
            ts_data.import_data(save_csv=save_csv, save_nc=False, use_cache=use_cache)
        all_ts[i] = ts_data
    return all_ts
