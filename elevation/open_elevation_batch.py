import sys

import gpxpy
import csv

GPX = None
FILENAME = None

def load_elevation_data():
    """Load elevation data from CSV"""
    elevation_data = {}
    with open('elevation_data.csv', 'r', encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            lat, lon, elev = float(row[0]), float(row[1]), float(row[2])
            elevation_data[(round(lat, 6), round(lon, 6))] = elev
    return elevation_data

def update_points(elev_data):
    """Update points with elevation data"""
    for track in GPX.tracks:
        for segment in track.segments:
            for point in segment.points:
                key = (round(point.latitude, 6), round(point.longitude, 6))
                if key in elev_data:
                    point.elevation = elev_data[key]

def parse_file():
    """
    Docstring for parse_file
    """
    global GPX
    GPX = gpxpy.parse(open(FILENAME, mode="r", encoding="utf-8"))
    for track in GPX.tracks:
        print(f"There is {len(GPX.tracks)} track(s) in this file.")
        for i, segment in enumerate(track.segments):
            

def write_file():
    """
    Docstring for write_file
    """
    with open(FILENAME, 'w', encoding="utf-8") as f:
        f.write(GPX.to_xml())

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("This module needs a parameter, the file path to process.")
        exit(1)
    FILENAME = sys.argv[1]
    parse_file()
    write_file()

# Example
# points = [
#     {"latitude": 40.7128, "longitude": -74.0060},
#     {"latitude": 34.0522, "longitude": -118.2437},
#     {"latitude": 41.8781, "longitude": -87.6298},
# ]

# elevations = batch_elevation(points)
# df = pd.DataFrame({
#     "latitude": [p["latitude"] for p in points],
#     "longitude": [p["longitude"] for p in points],
#     "elevation": elevations
# })
# print(df)
