"""Module providing estimated power into gpx file."""
import sys
import gpxpy
import gpxpy.gpx

from lxml import etree

from forces import power

RIDER = {
    "M" : 67,
    'm' : 9
}

FILENAME = "test_files/3076816628.gpx"

def get_slope(location1, location2):
    """
    Docstring for get_slope
    
    :param l1: Origin point
    :param l2: Next point
    """
    # Direct method on Location object
    s = location1.elevation_angle(location2)
    if not s:
        s = 0
        print(0)
    return s

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
    res = point.elevation if point.elevation else False
    return res

def set_point_power(point, next_point):
    """Given a point, set his power value"""
    speed = point.speed_between(next_point)

    slope = get_slope(point, next_point)

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

def parse_file():
    """
     Parsing an existing file
    """
    with open(FILENAME, 'r', encoding="utf-8") as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        for track in gpx.tracks:
            print(f"There is {len(gpx.tracks)} track(s) in this file.")
            for segment in track.segments:
                print(f"There is {len(track.segments)} segment(s) in the the actual segment(s).")
                for i in range(len(segment.points) - 1):
                    point = segment.points[i]
                    if point_have_power(point):
                        print("Already have power, skipping")
                        continue
                    next_point = segment.points[i + 1]
                    if not point_has_elevation(point):
                        point.elevation = 1003

                    set_point_power(point, next_point)
                    
        return gpx

def write_file(fb):
    """
    Docstring for write_file
    
    :param fb: file buffer
    """
    with open(FILENAME, 'w', encoding="utf-8") as gpx_file:
        gpx_file.write(fb.to_xml())
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
    FILENAME = sys.argv[1]
    file = parse_file()
    write_file(file)
