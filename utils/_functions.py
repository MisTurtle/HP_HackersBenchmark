import math


def point_in_elliptical_disk(angle, center, semi_major_r, semi_minor_r) -> tuple[float, float]:
	a, b = semi_major_r, semi_minor_r
	distance = (a * b) / math.sqrt((b * math.cos(angle)) ** 2 + (a * math.sin(angle)) ** 2)
	return center[0] + distance * math.cos(angle), center[1] + distance * math.sin(angle)
