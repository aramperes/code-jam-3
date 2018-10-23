from pscript import RawJS


def load_jquery():
    return RawJS(
        """
        function() {
            var xhrObj = new XMLHttpRequest();
            xhrObj.open('GET', 'https://code.jquery.com/jquery-3.3.1.min.js', false);
            xhrObj.send('');
            var se = document.createElement('script');
            se.type = 'text/javascript';
            se.innerHTML = xhrObj.responseText;
            document.getElementsByTagName('head')[0].appendChild(se);
        }();
        """
    )


def call_http(method, url, callback):
    return RawJS(
        """
        $.ajax({
            url: url,
            method: method,
            success: callback
        });
        """
    )
