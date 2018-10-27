import itertools
import json


from game.world import terrain

dim = 200
map, features = terrain.generate_terrain(dim)
# encode to terrain format
terrain_format = list(itertools.chain.from_iterable(map))
features_format = list(itertools.chain.from_iterable(features))
terrain_data = {
    "width": dim,
    "height": dim,
    "terrain": terrain_format,
    "features": features_format
}
with open("../client-host/project/static/terrain.json", "w") as file:
    file.write(json.dumps(terrain_data))