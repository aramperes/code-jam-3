import itertools
import json

if __name__ == "__main__":
    from game.world import terrain

    dim = 100
    map = terrain.generate_terrain(dim)
    # encode to terrain format
    terrain_format = list(itertools.chain.from_iterable(map))
    terrain_format.insert(0, dim)
    terrain_format.insert(1, dim)
    terrain_data = {
        "terrain": terrain_format
    }
    with open("../client-host/project/static/terrain.json", "w") as file:
        file.write(json.dumps(terrain_data))

    import game

    game.run()
