from pscript import RawJS


def create_websocket_connection(ws_url, ws_message_callback):
    return RawJS(
        """
        function() {
            const ws = new WebSocket(ws_url);
            ws.onmessage = ws_message_callback;
            return ws;
        }()
        """
    )
