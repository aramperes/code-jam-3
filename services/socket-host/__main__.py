if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--gateway", help="overrides the WebSocket URL", action="store_true")
    args = parser.parse_args()

    if args.gateway:
        import gateway

        gateway.run()
