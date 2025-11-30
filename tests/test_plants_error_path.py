def test_search_plants_handles_exception(client, monkeypatch):
    def bad_get_db(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "src.components.Backend.Repositories.db.get_db",  # adjust case/path if needed
        bad_get_db,
        raising=True,
    )

    r = client.get("/api/plants/search?q=Poth")
    assert r.status_code == 200
    assert r.get_json() == []
