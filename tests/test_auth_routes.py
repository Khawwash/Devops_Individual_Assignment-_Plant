import types

def test_signup_success(client, monkeypatch):
    # stub create_user to succeed
    import src.data.Auth as auth
    monkeypatch.setattr(auth, "create_user", lambda *a, **k: None)
    r = client.post("/signup", data={"username":"u","email":"e@e.com","password":"abcdefgh","confirm_password":"abcdefgh"})
    assert r.status_code in (302, 303)

def test_signup_conflict(client, monkeypatch):
    import src.data.Auth as auth
    def boom(*a, **k): raise ValueError("exists")
    monkeypatch.setattr(auth, "create_user", boom)
    r = client.post("/signup", data={"username":"u","email":"e@e.com","password":"abcdefgh","confirm_password":"abcdefgh"})
    assert r.status_code == 409

def test_login_ok(client, monkeypatch):
    import src.data.Auth as auth
    monkeypatch.setattr(auth, "authenticate_user", lambda e,p: True)
    r = client.post("/login", data={"email":"e@e.com","password":"abcdefgh"})
    assert r.status_code in (302, 303)

def test_login_bad(client, monkeypatch):
    import src.data.Auth as auth
    monkeypatch.setattr(auth, "authenticate_user", lambda e,p: False)
    r = client.post("/login", data={"email":"e@e.com","password":"abcdefgh"})
    assert r.status_code == 401
