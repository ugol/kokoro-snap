import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

from kokoro_server import api


def test_server_http(monkeypatch):
    monkeypatch.setattr(api, "synthesize_wav", lambda *args: b"RIFFtest")
    server = ThreadingHTTPServer(("127.0.0.1", 0), api.Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        port = server.server_address[1]
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health") as response:
            assert json.load(response) == {"status": "ok"}
        request = urllib.request.Request(
            f"http://127.0.0.1:{port}/v1/audio/speech",
            data=json.dumps({"input": "Hello", "voice": "af_heart"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request) as response:
            assert response.headers["Content-Type"] == "audio/wav"
            assert response.read() == b"RIFFtest"
    finally:
        server.shutdown()
        server.server_close()
