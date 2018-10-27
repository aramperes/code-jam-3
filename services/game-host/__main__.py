import json

import itertools

if __name__ == "__main__":
    from game.world import terrain

    # print(" TERRAIN TEST")
    # print("===============")

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

    #
    # for x in range(dim):
    #     for y in range(dim):
    #         print("{:4}".format(map[x][y]), end='')
    #     print()
    #
    # print()
    #
    # for x in range(dim):
    #     for y in range(dim):
    #         print("{:4}".format(rivers[x][y]), end='')
    #     print()

    import game

    game.run()
