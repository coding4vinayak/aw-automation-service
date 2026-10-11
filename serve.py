#!/usr/bin/env python3
"""Production-ish static server for the AutoFlow site (:3102).

Why not `python -m http.server`: it is single-threaded, so under any
concurrent load (a launch-day spike, two tabs) every request queues behind
the one in flight — measured p95 2.7s at c=50. ThreadingHTTPServer handles
each connection on its own thread; static files are the easy case.
Run: python3 serve.py  (PORT env overrides, default 3102)
"""
import functools
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("PORT", "3102"))
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "website")


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):  # access logs go to the supervisor, not stdout
        pass


if __name__ == "__main__":
    handler = functools.partial(Quiet, directory=HERE)
    # Default backlog is 5 — a launch spike parks connections in retransmit
    # hell. 128 is boring and correct for a static site.
    ThreadingHTTPServer.request_queue_size = 128
    ThreadingHTTPServer.allow_reuse_address = True
    with ThreadingHTTPServer(("127.0.0.1", PORT), handler) as httpd:
        print(f"serving {HERE} on :{PORT} (threaded)", flush=True)
        httpd.serve_forever()
