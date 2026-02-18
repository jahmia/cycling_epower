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
        print("WARNING: slope is unknown! You have to recompute elevation manually.")
        recompute = True
        # FIX We need decimal precision with our elevation data
        # There is some scripts to begin from test_files folder
        exit(1)
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
    point.elevation = get_elevation_from_api(point.latitude, point.longitude)
    if ELEV_COUNT == 10:
        write_file()
        ELEV_COUNT = 0

def set_point_power(point, next_point):
    """Given a point, set his power value"""
    speed = point.speed_between(next_point)

    slope = get_slope(point, next_point)
    if slope != 0 and slope > 35:
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
            for j, segment in enumerate(track.segments):
                print(f"There is {len(track.segments)} segment(s) in the the actual segment(s).")
                for i in range(len(segment.points) - 1):
                    point = segment.points[i]
                    if point_have_power(point):
                        # print("Already have power, skipping")
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
                # for index in sorted(points_to_pop, reverse=True):
                #     track.segments[j].remove_point(index)
                points_to_pop = []

def write_file():
    """
    Write in the GPX file

    :param fb: file buffer
    """
    with open(FILENAME, 'w', encoding="utf-8") as gpx_file:
        gpx_file.write(GPX.to_xml())
        print("Saving")

def mean_power():
    """
     Parsing an existing file
    """
    global GPX
    global ELEV_COUNT
    with open(FILENAME, 'r', encoding="utf-8") as gpx_file:
        GPX = gpxpy.parse(gpx_file)
        ELEV_COUNT = 0
        for track in GPX.tracks:
            for j, segment in enumerate(track.segments):
                for i in range(len(segment.points)):
                    continue

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

def show_stats():
    """
    Some stats about the gpx
    """
    global GPX
    print("\n=== GPX File Analysis ===\n")

    # Total distance (2D: lat/lon only)
    distance_2d = GPX.length_2d()
    print(f"Distance (2D): {distance_2d / 1000:.2f} km")

    # Total distance (3D: includes elevation)
    distance_3d = GPX.length_3d()
    print(f"Distance (3D): {distance_3d / 1000:.2f} km\n")

    # Elevation data
    min_elev, max_elev = GPX.get_elevation_extremes()
    print(f"Min elevation: {min_elev}m")
    print(f"Max elevation: {max_elev}m\n")

    # Uphill/Downhill
    uphill, downhill = GPX.get_uphill_downhill()
    print(f"Total uphill:\t{uphill:.0f}m")
    print(f"Total downhill: {downhill:.0f}m\n")

    # Time information
    start_time, end_time = GPX.get_time_bounds()
    print(f"Started:\t{start_time}")
    print(f"Ended:\t\t{end_time}\n")

    # Duration
    duration = GPX.get_duration()
    print(f"Duration: {duration:.0f} seconds ({duration/3600:.2f} hours)")

    # Total points
    total_points = GPX.get_track_points_no()
    print(f"Total points: {total_points}")

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("This module needs a parameter")
        exit(1)
    ELEV_COUNT = 0
    FILENAME = sys.argv[1]
    parse_file()
    show_stats()
    # mean_power()
    write_file()
