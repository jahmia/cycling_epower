# coding utf-8
import math
from math import atan, exp, cos, sin

# variables
G = 9.80665

# Rolling resistance
CRR = 0.0050

# Aerodynamic drag
# Tops        0.408
# Hoods       0.324
# Drops       0.307
# Aerobars    0.2914
CDA = 0.324

# TODO Dynamic
w = 0   # Wind speed in km per hour(positive for headwind and negative for tailwind)

# Air density
# p0 = 1.225 # Air density at the sea level
# M0 = 0.0289644 # Molar mass of Earth's air
# R = 8.3144598 # Universal gas constant of a air
# T0 = 288.15 # Standard temparature




def gravity(slope, weights):
    """Ressisting force due to gravity.
    Naturally, if you're going downhill, gravity will actually help you,
    making you accelerate without any additional effort.

    Args:
        slope (float): Slop of the hill expressed as a percentage
        weights (dict): Weight
    Returns:
        float: 
    """
    assert -0.35 < slope and slope < 0.35, (
        f"The slope value is incorrect. It must be between [-0,35:0,35], given {slope}"
    )
    res = G * sin(atan(slope)) * (weights['M'] + weights['m'])
    return res

def rolling_resistance(slope, weights):
    """Rolling resistance force.
    Frictions between tires and surface.

    Args:
        slope (float): Gradient in percentage
        weights (dict): Weight

    Returns:
        float: Force
    """
    res = G * cos(atan(slope)) * (weights['M'] + weights['m']) * CRR
    return res

def aerodynamic_drag(v, asl, verbose=False):
    """Force of air resistance  

    Args:
        v (float): Speed in ms
        asl (integer): Elevation above sea level in metters

    Returns:
        float: Force
    """
    p = air_density(asl, verbose)
    res = 0.5 * CDA * p * math.pow(v + w, 2)
    return res

def air_density(asl, verbose=False):
    """Air density

    Args:
        v (float): Speed
        h (integer): Elevation above sea in meters

    Returns:
        float: Air density
    """
    res = 1.225 * exp(-0.00011856 * asl)
    return res

def loss():
    """We assume a constant 1.5% loss on your pulleys.

    The losses on the chain are dependent on its condition:
    0.03 New, well-oiled chain
    0.04 Dry chain
    0.05 Dry cahin that is so old
    """
    return (1.5 + 3)/100


def power(v, slope, asl, weights, verbose=False):
    """Returns the cycling wattage based on parameters.

    Args:
        v (float): speed in km per hour
        slope (float): Gradient/Slope
        asl (integer): Elevation above sea
        weights (dict): Cyclist weight and Bike weight (kg)
        verbose (bool): More logs if true
    """
    v = v / 3.6
    fg = gravity(slope, weights)
    fr = rolling_resistance(slope, weights)
    fa = aerodynamic_drag(v, asl, verbose)
    l =  loss()
    assert l != 1, "Error, loss should not equals 1 !"
    pow = ((fg + fr + fa) * v) / (1 - l)
    pow = round(pow, 2)
    res = {
        'power': pow,
        'speed': v * 3.6,
        'slope': slope * 100,
        'W': list(weights.values()),
        'ratio': pow/weights['M'],
        'Fa': fa,
        'Fg': fg,
        'Fr': fr
    }
    if verbose:
        print(f"Power for {res['speed']:.2f} km/h at\t{res['slope']:.3f}% "
            f"with weights {res.get('W')} kg is\t{res['power']} Watts\t(Ratio {res['ratio']:.3f} W/kg)"
        )

    return res
