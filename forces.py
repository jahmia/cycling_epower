# coding utf-8
from math import atan, exp, cos, pow, sin

# variables
g = 9.80665

# Rolling resistance
Crr = 0.0050

# Aerodynamic drag
# Tops        0.408
# Hoods       0.324
# Drops       0.307
# Aerobars    0.2914
CdA = 0.324

w = 1   # Wind speed in km per hour(positive for headwind and negative for tailwind)

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
    assert -0.35 < slope and slope < 0.35, "The slope value is incorrect. It must be between [-0,35:0,35], given %s" % slope 
    res = g * sin(atan(slope)) * (weights['M'] + weights['m'])
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
    res = g * cos(atan(slope)) * (weights['M'] + weights['m']) * Crr
    return res

def aerodynamic_drag(v, asl, verbose=False):
    """Force of air resistance  

    Args:
        v (float): Speed in ms
        asl (integer): Elevation above sea level in metters

    Returns:
        float: Force
    """
    p = air_density(v, asl, verbose) # TO DO: Elevation above sea
    res = 0.5 * CdA * p * pow(v + w, 2)
    return res

def air_density(v, asl, verbose=False):
    """Air density

    Args:
        v (float): Speed
        h (integer): Elevation above sea in meters

    Returns:
        float: Air density
    """
    res = 1.225 * exp(-0.00011856 * asl)
    if verbose:
        print("\nAir density = %s" % res)
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
    v = v / 3.6 # To do : Dynamic
    Fg = gravity(slope, weights)
    Fr = rolling_resistance(slope, weights)
    Fa = aerodynamic_drag(v, asl, verbose)
    l =  loss()
    assert loss != 1, "Error, loss should not equals 1 !"
    P = ((Fg + Fr + Fa) * v) / (1 - l)
    P = round(P, 2)
    if verbose:
        print("\nFg = %.3f" % Fg)
        print("Fr = %.3f" % Fr)
        print("Fa = %.3f" % Fa)
        print("Loss = %s" % l)
        print("Fg + Fr + Fa = %.3f" % (Fg + Fr+ Fa))
        print("Weight=%s\tBike=%s" % (weights['M'], weights['m']))

    res = {
        'power': P,
        'speed': v * 3.6,
        'slope': slope * 100,
        'W': list(weights.values()),
        'ratio': P/weights['M']
    }
    return res
