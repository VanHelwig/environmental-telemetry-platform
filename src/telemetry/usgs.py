import httpx

USGS_API_URL = 'https://api.waterdata.usgs.gov/ogcapi/v1/collections/latest-continuous/items'

def get_latest_usgs_observations(parameter_code: str, state_code: str, limit: int = 5) -> dict:
    """
    Fetches the latest USGS observations for a given parameter code and state code.

    Args:
        parameter_code (str): The USGS parameter code to query.
        state_code (str): The state code to filter the data.
        limit (int): The maximum number of records to return.

    Returns:
        dict: The JSON response from the USGS API.
    """
    
    params = {'parameter_code': parameter_code, 'state_code': state_code, 'limit': limit}
    r = httpx.get(USGS_API_URL, params=params)
    r.raise_for_status()
    
    return r.json()