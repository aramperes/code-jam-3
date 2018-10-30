import math
from typing import Tuple

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


def noise_octave(noise_func=None, octaves: int = 1, persistence: float = 1.0, coordinates: Tuple[float, ...] = ()):
    total = 0.0
    frequency = 1.0
    amplitude = 1.0
    max_value = 0.0
    for _ in range(octaves):
        noise_value = noise_func(*tuple(coord * frequency for coord in coordinates)) * amplitude
        total += noise_value
        max_value += amplitude

        amplitude *= persistence
        frequency *= 2

    return total / max_value


def generate_terrain(dimensions, zone_size=15, spawn_range=50, seed=None):
    # map_middle = dimensions // 2
    # map = [["?" for x in range(dimensions)] for y in range(dimensions)]
    # features = [[None for x in range(dimensions)] for y in range(dimensions)]
    #
    # if not seed:
    #     seed = random.randrange(-1000, 1000)
    #
    # for x in range(dimensions):
    #     for y in range(dimensions):
    #         # within_spawn_range = spawn_range > math.sqrt((x - map_middle) ** 2 + (y - map_middle) ** 2)
    #         pass

    pass


def tile_terrain(x: int, y: int, seed: int, map_size: int, spawn_range=50):
    map_middle = map_size // 2
    terrain_data = get_for_noise(
        noise_octave(
            noise_func=noise.snoise3,
            octaves=2,
            persistence=0.1,
            coordinates=(x / 40, y / 40, seed)
        )
    )
    feature = ""

    # Since we want to avoid having a lot of water near the spawn range, we can use
    # a down-pointing elliptic paraboloid to represent the probability of a river at
    # that position.

    # This is all ad-hoc. Not a lot of thought went into the math.

    # check if the coordinates are within the spawn range (pythagoras theorem)
    max_noise_range = 0.15
    within_spawn_range = spawn_range > math.sqrt((x - map_middle) ** 2 + (y - map_middle) ** 2)
    if within_spawn_range:
        max_noise_range /= 2
        # max_noise_range = ((x ** 2) / 16 + (y ** 2) / 16) / 100000
    river_val = noise_octave(
        noise_func=noise.snoise3,
        octaves=1,
        persistence=0.1,
        coordinates=(x / 50, y / 50, seed)
    )

    if max_noise_range > river_val > 0.0:
        terrain_data = "W"

    # For cities, we will base it off the river noise (cities are typically close to water bodies).
    # But since we don't want cities everywhere, we will do a noise cross between the river noise
    # and a new noise (nRiver X nCities) = nCoastCities.

    city_val = noise_octave(
        noise_func=noise.snoise3,
        octaves=2,
        persistence=0.2,
        coordinates=(x / 30, y / 30, seed)
    )

    if max_noise_range + 0.2 > river_val > max_noise_range > city_val > 0:
        feature = "fC"

    # For shelters, we'll try to keep them pretty far from the cities for the added challenge.
    # The generation is done by making a highly sparse (+octave) noise and using an invert treshold from
    # the cities

    shelter_val = noise_octave(
        noise_func=noise.snoise3,
        octaves=4,
        persistence=0.4,
        coordinates=(x, y, seed)
    )

    if max_noise_range + 0.8 > shelter_val > max_noise_range + 0.75:
        feature = "fS"

    return terrain_data, feature
