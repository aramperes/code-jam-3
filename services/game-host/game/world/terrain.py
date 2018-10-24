import random

import noise

ZONES = {
    "S": (0.0, 0.3),  # Snow
    "F": (0.3, 0.4),  # Forest
    "P": (0.4, 0.7),  # Forest
    "D": (0.7, 1.0)  # Desert
}


def get_for_noise(noise_val):
    noise_val += 1.0
    noise_val /= 2.0
    noise_val = max(0.00, noise_val)
    noise_val = min(0.99, noise_val)

    for zone, temperature in ZONES.items():
        if temperature[0] <= noise_val < temperature[1]:
            return zone


def generate_terrain(dimensions, zone_size=15, seed=None):
    map = [["?" for x in range(dimensions)] for y in range(dimensions)]

    if not seed:
        seed = random.randrange(-1000, 1000)

    for x in range(dimensions):
        for y in range(dimensions):
            map[y][x] = get_for_noise(noise.snoise3(x / zone_size, y / zone_size, seed))

    return map
