import os

if __name__ == '__main__':
    WS_URL = "ws://localhost:8080/game/"

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="overrides the WebSocket URL")
    args = parser.parse_args()

    import flexx_app

    if args.url:
        WS_URL = args.url

    app = flexx_app.init(WS_URL)

    app.export(
        os.path.join('..', 'services', 'client-host', 'project', 'templates', '_flexx_output.html'),
        link=0
    )

    print("Application exported.")
