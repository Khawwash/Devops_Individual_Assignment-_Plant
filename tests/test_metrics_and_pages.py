def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json.get("status") == "ok"

def test_metrics(client):
    # any request first to exercise before/after middleware
    client.get("/")
    r = client.get("/metrics")
    assert r.status_code == 200
    assert b"http_requests_total" in r.data

def test_all_pages(client):
    for path in ["/", "/login.html", "/signup", "/dashboard", "/add-plant"]:
        assert client.get(path).status_code in (200, 304)
