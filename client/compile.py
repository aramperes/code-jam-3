import os

if __name__ == '__main__':
    import flexx_app

    flexx_app.app.export(
        os.path.join('..', 'services', 'client-host', 'project', 'templates', '_flexx_output.html'),
        link=0
    )

    print("Application exported.")
