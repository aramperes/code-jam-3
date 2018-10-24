import os

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="overrides the WebSocket URL")
    args = parser.parse_args()

    import flexx_app

    if args.url:
        flexx_app.WS_URL = args.url

    flexx_app.app.export(
        os.path.join('..', 'services', 'client-host', 'project', 'templates', '_flexx_output.html'),
        link=0
    )

    print("Application exported.")
