"""Module providing estimated power into gpx file."""
import sys
import gpxpy
import gpxpy.gpx
import requests

from lxml import etree

from forces import power

RIDER = {
    "M" : 67,
    'm' : 9
}

ELEV_COUNT = 0
GPX = None

FILENAME = "test_files/3076816628.gpx"

def get_slope(location1, location2):
    """
    Given two points, get slope
    
    :param l1: Origin point
    :param l2: Next point
    """
    # Direct method on Location object
    s = location1.elevation_angle(location2)
    recompute = False
    if not s and s != 0.0:
        print("WARNING: slope is unknown! Recomputing elevation.")
        recompute = True
    if not recompute and (-0.35 < s and s < 0.35 and s != 0.0):
        print(f"WARNING: {s} is anormal slope! Recomputing elevation.")
        recompute = True
    if recompute:
        set_point_elevation(location2)
        return get_slope(location1, location2)
    return s if s else 0

def calculate_power(speed, gradient, elevation, verbose=False):
    """
    Given speed, elevation, and slope calculate output power
    """
    p = power(speed, gradient, elevation, RIDER, verbose)
    return abs(int(p.get("power", 0)))

def point_have_power(point):
    """
    Check if a point have a power extension
    
    :param point: GPX Point
    """
    for ext in point.extensions:
        if "power" in ext.tag:
            return True
    return False

def point_has_elevation(point):
    """
    Given a point, check if it has elevation data
    """
    res = True if point.elevation else False
    return res

def get_elevation_from_api(lat, lon):
    """
    Elevation using Open Elevation API (free, no key required)
    Returns elevation in meters
    """
    global ELEV_COUNT
    url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
    try:
        response = requests.get(url, timeout=60)
        data = response.json()
        ELEV_COUNT += 1
        return data['results'][0]['elevation']
    except:
        return None

def set_point_elevation(point):
    """
    Given a point, set his elevation
    """
    global ELEV_COUNT
    global GPX
    point.elevation = get_elevation_from_api(point.latitude, point.longitude)
    if ELEV_COUNT == 10:
        write_file()
        ELEV_COUNT = 0

def set_point_power(point, next_point):
    """Given a point, set his power value"""
    speed = point.speed_between(next_point)

    slope = get_slope(point, next_point)
    if slope != 0 and slope > 8:
        print(slope)
        return False

    point.power = calculate_power(speed * 3.6, slope/100, point.elevation)
    print(f"{point.time} Point at ({point.latitude:.6f}, {point.longitude:.6f}) "
        f"{point.elevation} meters,\t"
        f"{slope:.3f} %,\t"
        f"{speed * 3.6:.2f} km/h,\t"
        f"{point.power} W")

    # Also add to extensions for GPX serialization
    power_element = etree.Element('power')
    power_element.text = str(point.power)
    point.extensions.append(power_element)
    return True

def parse_file():
    """
     Parsing an existing file
    """
    global GPX
    global ELEV_COUNT
    with open(FILENAME, 'r', encoding="utf-8") as gpx_file:
        GPX = gpxpy.parse(gpx_file)
        ELEV_COUNT = 0
        for track in GPX.tracks:
            print(f"There is {len(GPX.tracks)} track(s) in this file.")
            points_to_pop = []
            for segment in track.segments:
                print(f"There is {len(track.segments)} segment(s) in the the actual segment(s).")
                for i in range(len(segment.points) - 1):
                    point = segment.points[i]
                    if point_have_power(point):
                        print("Already have power, skipping")
                        continue
                    next_point = segment.points[i + 1]
                    if not point_has_elevation(point):
                        set_point_elevation(point)

                    good = set_point_power(point, next_point)
                    prev_point = segment.points[i-1]
                    if not good and abs(prev_point.elevation - point.elevation) < 0.7:
                        print(prev_point, prev_point.elevation)
                        print(f"{point} {point.elevation}")
                        points_to_pop.append(i)
            # FIX loop segments by index
            for index in sorted(points_to_pop, reverse=True):
                segment.remove_point(i)

def write_file():
    """
    Write in the GPX file
    
    :param fb: file buffer
    """
    global GPX
    with open(FILENAME, 'w', encoding="utf-8") as gpx_file:
        gpx_file.write(GPX.to_xml())
        print("Saving")

def get_datas():
    """
    Get datas from single point
    """

def get_power_avg():
    '''
    Get average power for an activity
    '''

def get_max():
    '''
    Get max power during an activity
    '''

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("This module needs a parameter")
        exit(1)
    ELEV_COUNT = 0
    FILENAME = sys.argv[1]
    parse_file()
    write_file()
