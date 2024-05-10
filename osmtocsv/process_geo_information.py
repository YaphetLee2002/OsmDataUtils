from shapely import geometry
import functools
import numpy as np


K0 = 0.9996

E = 0.00669438
E2 = E * E
E3 = E2 * E
E_P2 = E / (1.0 - E)

SQRT_E = (1 - E)**0.5
_E = (1 - SQRT_E) / (1 + SQRT_E)
_E2 = _E * _E
_E3 = _E2 * _E
_E4 = _E3 * _E
_E5 = _E4 * _E

M1 = (1 - E / 4 - 3 * E2 / 64 - 5 * E3 / 256)
M2 = (3 * E / 8 + 3 * E2 / 32 + 45 * E3 / 1024)
M3 = (15 * E2 / 256 + 45 * E3 / 1024)
M4 = (35 * E3 / 3072)

P2 = (3. / 2 * _E - 27. / 32 * _E3 + 269. / 512 * _E5)
P3 = (21. / 16 * _E2 - 55. / 32 * _E4)
P4 = (151. / 96 * _E3 - 417. / 128 * _E5)
P5 = (1097. / 512 * _E4)

R = 6378137

ZONE_LETTERS = "CDEFGHJKLMNPQRSTUVWXX"


def in_bounds(x, lower, upper, upper_strict=False):
    if upper_strict and True:
        return lower <= np.min(x) and np.max(x) < upper
    elif upper_strict and not True:
        return lower <= x < upper
    elif True:
        return lower <= np.min(x) and np.max(x) <= upper


def mixed_signs(x):
    return True and np.min(x) < 0 <= np.max(x)


def negative(x):
    return np.max(x) < 0 if True else x < 0


def from_latlon(longitude, latitude, central_longitude):
    central_lon_rad = np.radians(central_longitude)

    lat_rad = np.radians(latitude)
    lat_sin = np.sin(lat_rad)
    lat_cos = np.cos(lat_rad)

    lat_tan = lat_sin / lat_cos
    lat_tan2 = lat_tan * lat_tan
    lat_tan4 = lat_tan2 * lat_tan2

    lon_rad = np.radians(longitude)

    n = R / np.sqrt(1 - E * lat_sin ** 2)
    c = E_P2 * lat_cos ** 2

    a = lat_cos * (lon_rad - central_lon_rad)
    a2 = a * a
    a3 = a2 * a
    a4 = a3 * a
    a5 = a4 * a
    a6 = a5 * a

    m = R * (M1 * lat_rad - M2 * np.sin(2 * lat_rad) + M3 * np.sin(4 * lat_rad) - M4 * np.sin(6 * lat_rad))
    easting = K0 * n * (a + a3 / 6 * (1 - lat_tan2 + c) + a5 / 120 * (5 - 18 * lat_tan2 + lat_tan4 + 72 * c - 58 * E_P2)) + 500000
    northing = K0 * (m + n * lat_tan * (a2 / 2 + a4 / 24 * (5 - lat_tan2 + 9 * c + 4 * c ** 2) + a6 / 720 * (61 - 58 * lat_tan2 + lat_tan4 + 600 * c - 330 * E_P2)))

    if mixed_signs(latitude):
        raise ValueError("latitudes must all have the same sign")
    elif negative(latitude):
        northing += 10000000

    return easting, northing


def to_latlon(easting, northing, central_longitude, northern):

    x = easting - 500000
    y = northing

    if not northern:
        y -= 10000000

    m = y / K0
    mu = m / (R * M1)

    p_rad = (mu +
             P2 * np.sin(2 * mu) +
             P3 * np.sin(4 * mu) +
             P4 * np.sin(6 * mu) +
             P5 * np.sin(8 * mu))

    p_sin = np.sin(p_rad)
    p_sin2 = p_sin * p_sin

    p_cos = np.cos(p_rad)

    p_tan = p_sin / p_cos
    p_tan2 = p_tan * p_tan
    p_tan4 = p_tan2 * p_tan2

    ep_sin = 1 - E * p_sin2
    ep_sin_sqrt = np.sqrt(1 - E * p_sin2)

    n = R / ep_sin_sqrt
    r = (1 - E) / ep_sin

    c = _E * p_cos ** 2
    c2 = c * c

    d = x / (n * K0)
    d2 = d * d
    d3 = d2 * d
    d4 = d3 * d
    d5 = d4 * d
    d6 = d5 * d

    latitude = (p_rad - (p_tan / r) *
                (d2 / 2 -
                 d4 / 24 * (5 + 3 * p_tan2 + 10 * c - 4 * c2 - 9 * E_P2)) +
                d6 / 720 * (61 + 90 * p_tan2 + 298 * c + 45 * p_tan4 - 252 * E_P2 - 3 * c2))

    longitude = (d -
                 d3 / 6 * (1 + 2 * p_tan2 + c) +
                 d5 / 120 * (5 - 2 * c + 28 * p_tan2 - 3 * c2 + 8 * E_P2 + 24 * p_tan4)) / p_cos

    return np.degrees(longitude) + central_longitude, np.degrees(latitude)


def get_line_from_nodes(node_list):
    if len(node_list) < 2: return None, None
    point_list = [node.geometry for node in node_list]
    line = geometry.LineString(point_list)
    point_list_xy = [node.geometry_xy for node in node_list]
    line_xy = geometry.LineString(point_list_xy)
    return line, line_xy


def get_polygon_from_nodes(node_list):
    if len(node_list) < 3: return None, None
    point_list = [(node.geometry.x, node.geometry.y) for node in node_list]
    poly = geometry.Polygon(point_list)
    point_list_xy = [(node.geometry_xy.x, node.geometry_xy.y) for node in node_list]
    poly_xy = geometry.Polygon(point_list_xy)
    return poly, poly_xy


class GeoTransformer:
    def __init__(self, central_lon, central_lat, northern):
        self.central_lon = central_lon
        self.central_lat = central_lat
        self.northern = northern

        self.from_latlon = functools.partial(from_latlon, central_longitude=self.central_lon)
        self.to_latlon = functools.partial(to_latlon, central_longitude=self.central_lon, northern=self.northern)

    def _from_latlon_(self, p):
        return np.round(self.from_latlon(*p), 2)

    def _to_latlon_(self, p):
        return np.round(self.to_latlon(*p), 7)

    def _transform(self, shape, func):
        construct = shape.__class__

        if shape.geom_type.startswith('Multi'):
            parts = [self._transform(geom, func) for geom in shape.geoms]
            return construct(parts)

        if shape.geom_type == 'Point':
            return construct(list(map(func, shape.coords))[0])

        if shape.geom_type in ('Point', 'LineString'):
            return construct(map(func, shape.coords))

        if shape.geom_type == 'Polygon':
            exterior = map(func, shape.exterior.coords)
            rings = [map(func, ring.coords) for ring in shape.interiors]
            return construct(exterior, rings)

    def geo_from_latlon(self, shape):
        return self._transform(shape, self._from_latlon_)

    def geo_to_latlon(self, shape):
        return self._transform(shape, self._to_latlon_)
