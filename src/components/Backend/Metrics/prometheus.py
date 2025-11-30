import time
import logging
from flask import g, request, Response

try:
    from prometheus_client import Counter, Histogram, REGISTRY, generate_latest, CONTENT_TYPE_LATEST
    http_requests = Counter("http_requests_total", "HTTP requests", ["method", "endpoint", "status"])
    http_latency = Histogram(
        "http_request_duration_seconds",
        "Latency sec",
        ["method", "endpoint", "status"],
        buckets=[0.05, 0.1, 0.3, 0.5, 1, 2, 5],
    )
except ImportError:
    class _Noop:
        def labels(self, *_, **__):
            return self
        def inc(self, *_, **__):
            return None
        def observe(self, *_, **__):
            return None

    http_requests = http_latency = _Noop()
    REGISTRY = None
    CONTENT_TYPE_LATEST = "text/plain"
    logging.warning("prometheus_client not installed; metrics middleware disabled")

    def generate_latest(_=None) -> bytes:
        return b"metrics_disabled"

def before_request():
    g._start = time.perf_counter()

def after_request(resp):
    dur = time.perf_counter() - getattr(g, "_start", time.perf_counter())
    status = str(resp.status_code)
    endpoint = request.endpoint or request.path
    http_requests.labels(request.method, endpoint, status).inc()
    http_latency.labels(request.method, endpoint, status).observe(dur)
    return resp

def metrics():
    return Response(generate_latest(REGISTRY), mimetype=CONTENT_TYPE_LATEST)
