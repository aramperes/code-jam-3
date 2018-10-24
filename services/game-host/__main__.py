if __name__ == "__main__":
    from game.world import terrain

    print(" TERRAIN TEST")
    print("===============")

    dim = 30
    map = terrain.generate_terrain(dim)

    for x in range(dim):
        for y in range(dim):
            print("{:4}".format(map[x][y]), end='')
        print()

    import game

    game.run()
