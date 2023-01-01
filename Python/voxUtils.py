from math import sqrt

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