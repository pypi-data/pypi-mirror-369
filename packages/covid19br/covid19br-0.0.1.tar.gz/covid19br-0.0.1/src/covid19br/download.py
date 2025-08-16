import pandas as pd
import requests
from typing import Literal, Optional
import urllib.error



def download_covid19(level: Level = "brazil") -> pd.DataFrame:
    """
    Downloads COVID-19 data from a web repository.

    This function downloads pandemic COVID-19 data at Brazil and World levels.
    Brazilian data is available at national, region, state, and city levels,
    whereas the world data is available at the country level.

    Parameters
    ----------
    level : {"brazil", "regions", "states", "cities", "world"}, default "brazil"
        The desired level of data aggregation.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the downloaded data at the specified level.

    Notes
    -----
    This function requires a Parquet reading engine like `pyarrow`.
    Install it with `pip install pyarrow`.

    Data Dictionary (variables common to Brazilian and world data):
    - date: date of data registry
    - epi_week: epidemiological week
    - pop: estimated population
    - accumCases: accumulative number of confirmed cases
    - newCases: daily count of new confirmed cases
    - accumDeaths: accumulative number of deaths
    - newDeaths: daily count of new deaths
    - newRecovered: daily count of new recovered patients

    Data Dictionary (variables in the Brazilian data):
    - region: regions' names
    - state: states' names.
    - city: cities' names.
    - state_code: numerical code attributed to states
    - city_code: numerical code attributed to cities
    - healthRegion_code: health region code
    - healthRegion: heald region name
    - newFollowup: daily count of new patients under follow up
    - metro_area: indicator variable for city localized in a metropolitan area
    - capital: indicator variable for capital of brazilian states

    Data Dictionary (variables in the world data):
    - country: countries' names
    - accumRecovered: accumulative number of recovered patients

    Examples
    --------
    >>> # Downloading Brazilian COVID-19 data:
    >>> # brazil_df = download_covid19(level="brazil")
    >>> # regions_df = download_covid19(level="regions")
    >>> # states_df = download_covid19(level="states")
    >>> # cities_df = download_covid19(level="cities")

    >>> # Downloading world COVID-19 data:
    >>> # world_df = download_covid19(level="world")
    """

    # Construct the base URL for the data repository, pointing to Parquet files
    BASE_URL = "https://github.com/dest-ufmg/covid19repo/blob/master/data/" 
    

    
    # Normalize input and validate against the allowed choices
    level = level.lower()
    valid_levels = ["brazil", "regions", "states", "cities", "world"]
    if level not in valid_levels:
        raise ValueError(
            f"Invalid level '{level}'. "
            f"Must be one of {valid_levels}"
        )
        
    print("Downloading COVID-19 data... please, be patient!")

    # Build the specific URL based on data_type and level
    url = f"{BASE_URL}{level}.parquet?raw=true"
    
    try:
        data = pd.read_parquet(url)
        # The source data uses different date formats, so we standardize them
        # by converting to datetime objects, handling potential errors.
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'], errors='coerce')
        return data
    except ImportError:
        print("Error: `pyarrow` is not installed. Please install it with `pip install pyarrow`.")
        return None
    except urllib.error.HTTPError:
        print(f"Error: Could not find data file at the specified URL: {url}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

