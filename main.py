"""Module providing estimated power into gpx file."""
import sys
import gpxpy
import gpxpy.gpx
import requests
import numpy as np

from lxml import etree

from config import arg_parser
from forces import power


ELEV_COUNT = 0 # Save the file when you have requested elevation API 10 times
GPX = None

FILENAME = "test_files/3076816628.gpx"

def show_stats():
    """
    Some stats about the gpx
    """
    global GPX
    print("\n=== GPX File Analysis ===\n")
    # Tracks and points
    print(f"Number of tracks: {len(GPX.tracks)}")
    print(f"Number of waypoints: {len(GPX.waypoints)}")
    print(f"Number of routes: {len(GPX.routes)}")
    print(f"Total track points: {GPX.get_track_points_no()}")

    # Get bounds
    print("\n=== Geographic Bounds ===")
    bounds = GPX.get_bounds()
    if bounds:
        print(f"Latitude:  {bounds.min_latitude:.4f} to {bounds.max_latitude:.4f}")
        print(f"Longitude: {bounds.min_longitude:.4f} to {bounds.max_longitude:.4f}")

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

def get_slope(location1, location2):
    """
    Given two points, get slope

    :param l1: Origin point
    :param l2: Next point
    """
    # FIX Clean code
    # Direct method on Location object
    s = location1.elevation_angle(location2)
    recompute = False
    if not s and s != 0.0:
        # No elevation data
        recompute = True
        # FIX We need decimal precision with our elevation data
        # There is some scripts to begin from test_files folder
    if recompute:
        print(f"WARNING: {s*100:.2f} % is anormal slope! Recomputing elevation.")
        d = location1.distance_3d(location2)
        print(f"Distance from previous point : {d:.2f} m")
        set_point_elevation([location1, location2])
        return get_slope(location1, location2)
    return s if s else 0

def compute_power(speed, gradient, elevation, verbose=False):
    """
    Given speed, elevation, and slope calculate output power
    """
    p = power(speed, gradient, elevation, args.rider, verbose)
    return abs(int(p['power']))

def point_have_power(point):
    """
    Check if a point have a power extension

    :param point: GPX Point
    """
    for ext in point.extensions:
        if "power" in ext.tag:
            return True
    return False

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

def set_point_elevation(points):
    """
    Given a point, set his elevation
    """
    global ELEV_COUNT
    for point in points:
        elevation_before = point.elevation or None
        point.elevation = get_elevation_from_api(point.latitude, point.longitude)
        print(f"Setting elevation for ({point.latitude}, {point.longitude}) :"
               f"{point.elevation} m, previously {elevation_before} m")
        if ELEV_COUNT == 10:
            update_gpx()
            ELEV_COUNT = 0

def has_null_cadence(point):
    """
    Given a point, check if it has cadence and his value equals 0
    """
    if args.no_cad:
        return False, 87 # This is my actual prefered cadence

    res = False
    cadence = 0
    for ext in point.extensions:
        for child in ext:
            if "cad" in child.tag and child.text:
                cadence = int(child.text)
                res = True if cadence == 0 else False
    return res, cadence

def set_point_power_element(point):
    """
    Given a point with power, save it in extension
    """
    if point.power is None:
        return False
    power_element = etree.Element('power')
    power_element.text = str(point.power)
    point.extensions.append(power_element)
    return True

def set_point_power(point, next_point):
    """Given a point, set his power value.
    Set it to zero if cadence is 0 rpm.

    Returns
    ----------
    save : float
        True if we want to save changes
    """
    global GPX
    speed = point.speed_between(next_point) * 3.6

    slope = get_slope(point, next_point)
    if slope != 0 and abs(slope) > 35:
        return False

    point.power = compute_power(speed, slope / 100, point.elevation)
    null_cadence, rpm = has_null_cadence(point)
    if rpm < 30:
        point.power = 0
    # else:
        # print(f"{point.time} Point at ({point.latitude:.6f}, {point.longitude:.6f}) "
        #     f"{point.elevation} meters, "
        #     f"{slope:.3f} %,\t"
        #     f"{speed * 3.6:.2f} km/h, "
        #     f"{point.distance_3d(next_point):.2f} m, "
        #     f"{rpm} rpm "
        #     f"{point.power} W")

    if point.power > 323 and null_cadence:
        point.power = 0

    # Also add to extensions for GPX serialization
    return set_point_power_element(point)

def parse_file():
    """
     Parsing an existing file
     If there is any modification then SAVE file
    """
    global GPX
    global ELEV_COUNT
    with open(FILENAME, 'r', encoding="utf-8") as gpx_file:
        GPX = gpxpy.parse(gpx_file)
        ELEV_COUNT = 0
        update = False
        for t, track in enumerate(GPX.tracks):
            for s, segment in enumerate(track.segments):
                for i in range(len(segment.points) - 1):
                    point = segment.points[i]
                    if point_have_power(point):
                        continue
                    try:
                        next_point = segment.points[i + 1]
                    except IndexError:
                        print("out of bound " + str(i))
                        break
                    if not (point.elevation or next_point.elevation):
                        set_point_elevation([point, next_point])

                    good = set_point_power(point, next_point)
                    if good:
                        update = True
    return update

def update_gpx():
    """
    Write in the GPX file
    """

    new_file = ''.join((FILENAME[:-4], "_powered", FILENAME[-4:]))
    with open(new_file, 'w', encoding="utf-8") as gpx_file:
        gpx_file.write(GPX.to_xml())
        print("Saving")

def get_extension(p, tag):
    """
    Given a point, get value from extension with tag name
    """
    res = 0
    if p.extensions:
        for ext in p.extensions:
            if ext.tag == tag:
                res = int(ext.text)
    return res

def set_power(p, value):
    """
    Given a point, set power value in extensions
    """
    if p.extensions:
        for ext in p.extensions:
            if ext.tag == 'power':
                ext.text = str(int(value))

def smooth_max_power(mpd):
    """
    Show surrounding points of the max power point \
    and remove point with anormal power
    mpd : Max Point Data
    mpd : Max Point Data
    """
    global FILENAME
    print("Reading file for surrounding")
    edited = ""
    for i in range(mpd.point_no - 4, mpd.point_no+3):
        prev_point = GPX.tracks[mpd.track_no].segments[mpd.segment_no].points[i-1]
        point = GPX.tracks[mpd.track_no].segments[mpd.segment_no].points[i]
        next_point = GPX.tracks[mpd.track_no].segments[mpd.segment_no].points[i+1]

        point_power = get_extension(point, 'power')
        prev_power = get_extension(prev_point, 'power')
        next_power = get_extension(next_point, 'power')
        if prev_power:
            ratio = point_power / prev_power
        elif next_power:
            ratio = point_power / next_power
        else:
            ratio = 1.0

        edited = ""
        if ratio >= 2.85:
            # To do After analysis, the speed increase suddenly in 1 second, it doubles
            # Power drift may comes there
            ratio /= 2.6
            point_power = int(prev_power * ratio)
            set_power(point, point_power)
            edited = " -- ajusted"

        speed = point.speed_between(next_point)
        slope = point.elevation_angle(next_point)
        dist_delta = point.distance_2d(next_point)
        print(f"{point.time} Point at ({point.latitude:.5f}, {point.longitude:.5f}) "
            f"{point.elevation} meters,\t"
            f"{"+" if slope >= 0.0 else ""}{slope:.2f} %, "
            f"{speed * 3.6:.2f} km/h,\t"
            f"{dist_delta:.2f} m,"
            f"r={ratio:.2f} %\t"
            f"{point_power} W"
            f"{edited}"
        )
        if edited:
            break
    if edited:
        power_stats()

def power_stats():
    """
    Show some power stats
    """
    global GPX
    power_data = []
    for i, point_data in enumerate(GPX.get_points_data()):
        point = point_data.point
        if point.extensions:
            for child in point.extensions:
                if 'power' in child.tag.lower() and int(child.text) != 0:
                    power_data.append((point_data, int(child.text)))

    print("\n--- Power data ---")
    pp = len(power_data)/GPX.get_track_points_no()
    print(f"{len(power_data)} of {GPX.get_track_points_no()} points ({pp * 100:.2f} %) with power")
    print(f"rider: {args.rider["M"]} kg")
    if power_data:
        max_tuple = max(power_data, key=lambda x: x[1])
        print(f"Max: {max_tuple[1]} W")
        print(f"Avg: {np.average([item[1] for item in power_data]):.0f} W")
        smooth_max_power(max_tuple[0])

if __name__ == "__main__":
    args = arg_parser()
    ELEV_COUNT = 0
    FILENAME = sys.argv[1]
    SAVE = parse_file()
    if SAVE:
        update_gpx()
    show_stats()
    power_stats()
    update_gpx()
