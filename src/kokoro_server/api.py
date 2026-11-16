"""Minimal dependency-free HTTP adapter for the OpenAI-style speech endpoint."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .synthesis import synthesize_wav


class Handler(BaseHTTPRequestHandler):
    server_version = "kokoro-snap-prototype/0.1"

    def respond_json(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self.respond_json(200, {"status": "ok"})
        else:
            self.respond_json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path != "/v1/audio/speech":
            return self.respond_json(404, {"error": "Not found"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 20_000:
                return self.respond_json(413, {"error": "Payload too large or empty"})
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError("JSON body must be an object")
            if data.get("model", "kokoro-82m") != "kokoro-82m":
                raise ValueError("unsupported model")
            if data.get("response_format", "wav") != "wav":
                raise ValueError("only WAV output is implemented")
            speed = data.get("speed", 1.0)
            if not isinstance(speed, (float, int)) or isinstance(speed, bool):
                raise ValueError("speed must be numeric")
            output = synthesize_wav(
                data.get("input", ""),
                data.get("voice", "af_heart"),
                float(speed),
                data.get("language", "en-us"),
            )
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            return self.respond_json(400, {"error": str(error)})
        except Exception:
            self.log_exception()
            return self.respond_json(500, {"error": "Synthesis failed"})
        self.send_response(200)
        self.send_header("Content-Type", "audio/wav")
        self.send_header("Content-Length", str(len(output)))
        self.end_headers()
        self.wfile.write(output)

    def log_exception(self):
        import traceback
        traceback.print_exc()


def main():
    host = os.environ.get("KOKORO_HOST", "127.0.0.1")
    port = int(os.environ.get("KOKORO_PORT", "8765"))
    print(f"Serving Kokoro on http://{host}:{port}", flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
