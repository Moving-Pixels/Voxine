from math import sqrt, cos, sin

# Utility functions for Voxine development
def NOOP(*args, **kwargs):
    pass

def coordsToIso(coords):
    x = coords[0]
    y = coords[1]
    z = coords[2]
    return (x - y, (x + y) / 2 - z)

def isoToCoords(isoCoords):
    x = isoCoords[0]
    y = isoCoords[1]
    return (x + y, x - y, -y)

def pointDistance2D(point1, point2):
    return sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

def rotatePoint3D(point, pivot, rotation):
    # Point, pivot, and rotation are all tuples of (x, y, z)
    # Rotation is in degrees
    # First, translate the point to the origin
    point = (point[0] - pivot[0], point[1] - pivot[1], point[2] - pivot[2])
    # Rotate the point around the x axis
    point = (point[0], point[1] * cos(rotation[0]) - point[2] * sin(rotation[0]), point[1] * sin(rotation[0]) + point[2] * cos(rotation[0]))
    # Rotate the point around the y axis
    point = (point[0] * cos(rotation[1]) + point[2] * sin(rotation[1]), point[1], -point[0] * sin(rotation[1]) + point[2] * cos(rotation[1]))
    # Rotate the point around the z axis
    point = (point[0] * cos(rotation[2]) - point[1] * sin(rotation[2]), point[0] * sin(rotation[2]) + point[1] * cos(rotation[2]), point[2])
    # Translate the point back to its original position
    point = (point[0] + pivot[0], point[1] + pivot[1], point[2] + pivot[2])
    return point