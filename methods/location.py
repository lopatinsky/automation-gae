import math


def distance(p1, p2):
    def d2r(deg):
        return deg * math.pi / 180

    delta_lat = p2.lat - p1.lat
    delta_lon = p2.lon - p1.lon

    earth_radius = 6372.795477598

    alpha = delta_lat / 2
    beta = delta_lon / 2
    a = math.sin(d2r(alpha)) ** 2 + math.cos(d2r(p1.lat)) * math.cos(d2r(p2.lat)) * math.sin(d2r(beta)) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(earth_radius * c, 4)
