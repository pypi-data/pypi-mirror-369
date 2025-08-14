![pipeline](https://gitlab.sintef.no/harald.svendsen/wind_power_timeseries/badges/main/pipeline.svg)
![coverage](https://gitlab.sintef.no/harald.svendsen/wind_power_timeseries/badges/main/coverage.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Timeseries Methods for Wind Power


This is a Python package to download timeseries data from the NORA3 reanalysis, and to convert to power time series for wind farms.

## Documentation

Documentation is provided in [GitLab Pages](https://timeseries-f6ad24.pages.sintef.no/#overview).

## Quick-start
- Install as a Python package in your preferred way, for example using `poetry`.
- Copy and adjust the example code below.

## Installation
Using conda to manage the environment, the package can be installed as follows.
```
conda create --name myenv python=3.10 
conda activate myenv 
conda install -c conda-forge poetry 
git clone https://gitlab.sintef.no/harald.svendsen/wind_power_timeseries.git 
cd wind_power_timeseries 
poetry install
```

## Example
```python
import pandas as pd
import pathlib
import wind_power_timeseries as tm

# Specify windfarms
windfarms = pd.DataFrame([
    {"id":"windfarm_1", "lat":55, "lon": 9, "orientation":None, "shape":None, "turbine_height": 150},
    {"id":"windfarm_2", "lat":60, "lon": 7, "orientation":None, "shape":None, "turbine_height": 150},
]).set_index("id")

# Download wind speed data from NORA3 and save to CSV file in specified folder
time_start = "2022-05-01"
time_end = "2022-05-05"
data_path = pathlib.Path("downloaded_nora3")
data_path.mkdir(parents=True,exist_ok=True)

# Download from server and save to files
wind_data = tm.download.retrieve_nora3(
    windfarms,time_start,time_end,use_cache=True,data_path=data_path)

# Specify function for wind speed to wind power conversion, using a pre-defined function:
my_power_function = tm.compute.func_ninja_compute_power
my_args = {"turbine_power_curve": tm.compute.get_power_curve(name="VestasV80")}

# Compute wind farm power from wind speed data
windpower = tm.compute.compute_power(windfarms,wind_data,
        power_function=my_power_function,power_function_args=my_args)

# Save to file
windpower.to_csv("windpower.csv")
```

This creates a windpower dataframe
```
                     windfarm_1  windfarm_2
time
2022-05-01 00:00:00    0.053922    0.105866
2022-05-01 01:00:00    0.065940    0.037178
2022-05-01 02:00:00    0.107095    0.009000
2022-05-01 03:00:00    0.056030    0.006256
2022-05-01 04:00:00    0.041206    0.003573
...
```

