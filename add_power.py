"""
Docstring for add_power
"""
import gpxpy
from lxml import etree

FILENAME = 'test_files/3076816628 copy.gpx'
with open(FILENAME, "r", encoding="utf-8") as f:
    gpx = gpxpy.parse(f)

    # Add power calculation to each point
    for track in gpx.tracks:
        for segment in track.segments:
            for i, point in enumerate(segment.points):
                # Calculate power
                POWER = 189

                # Store directly on the point object
                point.power = POWER

                # Also add to extensions for GPX serialization
                power_element = etree.Element('power')
                power_element.text = str(POWER)
                point.extensions.append(power_element)

# Save to file
with open(FILENAME, 'w', encoding="utf-8") as f:
    f.write(gpx.to_xml())