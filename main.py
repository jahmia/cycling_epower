"""Module providing estimated power into gpx file."""
import gpxpy
import gpxpy.geo as geo
import gpxpy.gpx

from lxml import etree

from forces import power

# Parsing an existing file:
# -------------------------
RIDER = {
    "M" : 67,
    'm' : 9
}

FILENAME = "test_files/3076816628 copy.gpx"

def get_slope(location1, location2):
    """
    Docstring for get_slope
    
    :param l1: Origin point
    :param l2: Next point
    """
    # Direct method on Location object
    slope = location1.elevation_angle(location2)
    return slope

def calculate_power(speed, slope, elevation):
    """
    Given speed, elevation, and slope calculate_power
    """
    P = power(speed, slope, elevation, RIDER, verbose=False)
    return abs(int(P.get("power", 0)))

def point_have_power(point):
    """
    Check if a point have a power extension
    
    :param point: GPX Point
    """
    for ext in point.extensions:
        if "power" in ext.tag:
            return True
    return False

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

                speed = point.speed_between(next_point)
                # if speed:
                #     speed_kmh = speed * 3.6  # 1 m/s = 3.6 km/h

                slope = get_slope(point, next_point)

                point.power = calculate_power(speed * 3.6, slope/100, point.elevation)
                # Also add to extensions for GPX serialization
                power_element = etree.Element('power')
                power_element.text = str(point.power)
                point.extensions.append(power_element)

                print(f"{point.time} Point at ({point.latitude:.6f}, {point.longitude:.6f}) "
                    f"{point.elevation} meters,\t"
                    f"{slope:.3f} %,\t"
                    f"{speed * 3.6:.2f} km/h,\t"
                    f"{point.power} W")

with open(FILENAME, 'w', encoding="utf-8") as gpx_file:
    gpx_file.write(gpx.to_xml())
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
