import requests
import urllib.parse

def get_elevation_from_api(lat, lon):
    """Queries the USGS API for the elevation at a given lat/lon."""
    url = r'https://epqs.nationalmap.gov/v1/json?'
    params = {
        'output': 'json',
        'x': lon,
        'y': lat,
        'units': 'Meters'
    }
    # Format query string and make the request
    result = requests.get((url + urllib.parse.urlencode(params)))

    # Extract the elevation value
    if result.status_code == 200:
        data = result.json()
        elevation = data['value']
        return elevation
    else:
        return f"Error: {result.status_code}"

# Example usage
latitude = 19.739153
longitude = 47.9847034
elevation = get_elevation_from_api(latitude, longitude)
print(f"Elevation at ({latitude}, {longitude}): {elevation} meters")
