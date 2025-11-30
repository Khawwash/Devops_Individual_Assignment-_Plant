def test_debug_plant_path(client):
    r = client.get("/api/debug/plant-path")
    assert r.status_code == 200
    assert "path" in r.json

def test_search_plants_returns_matches(client):
    r = client.get("/api/plants/search?q=Poth")
    assert r.status_code == 200
    assert any(row["name"] == "Pothos" for row in r.get_json())

def test_search_plants_empty_query(client):
    r = client.get("/api/plants/search")
    assert r.status_code == 200
    assert r.get_json() == []  

def test_page_routes_serve(client):
    assert client.get("/").status_code in (200, 304)
    assert client.get("/login.html").status_code in (200, 304)
    assert client.get("/dashboard").status_code in (200, 304)
    assert client.get("/Reminder").status_code in (200, 304)
