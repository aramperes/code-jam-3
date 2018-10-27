from pscript import RawJS


def store_token(token):
    return RawJS(
        """
        function() {
            localStorage.setItem('user_token', token);
        }()
        """
    )


def read_token():
    return RawJS(
        """
        function() {
            return localStorage.getItem('user_token');
        }()
        """
    )
