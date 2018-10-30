if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--gateway", help="starts the gateway host", action="store_true")
    parser.add_argument("--game", help="starts the game host", action="store_true")
    args = parser.parse_args()

    if args.gateway:
        import gateway

        gateway.run()

    elif args.game:
        import game

        game.run()
