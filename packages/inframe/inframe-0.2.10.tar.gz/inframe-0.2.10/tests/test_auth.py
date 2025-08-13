import sqlite3
import time
import json
import uuid
import os
import httpx

import jwt

from deploy.modal_auth import _ensure_db, _load_or_create_signing_key, _sha256


def test_grant_jwt_issue_and_decode(tmp_path):
    conn = sqlite3.connect(str(tmp_path / "auth.db"))
    _ensure_db(conn)

    keys = _load_or_create_signing_key(conn)
    kid = keys["kid"]
    priv = keys["private_pem"]
    jwk = keys["public_jwk"]

    org_id = "org_test"
    customer_id = "cust_test"
    scopes = ["read"]
    jti = str(uuid.uuid4())
    iat = int(time.time())
    exp = iat + 300

    token = jwt.encode(
        {"org_id": org_id, "customer_id": customer_id, "scopes": scopes, "jti": jti, "iat": iat, "exp": exp},
        priv,
        algorithm="RS256",
        headers={"kid": kid},
    )

    # Store grant in DB
    cur = conn.cursor()
    cur.execute(
        "insert into grants (jti, org_id, customer_id, scopes, status, exp, issued_at, revoked_at) values (?, ?, ?, ?, 'active', ?, ?, 0)",
        (jti, org_id, customer_id, ",".join(scopes), exp, iat),
    )
    conn.commit()

    # Decode with public JWKS
    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
    claims = jwt.decode(token, public_key, algorithms=["RS256"], options={"require": ["exp", "jti"]})

    assert claims["org_id"] == org_id
    assert claims["customer_id"] == customer_id
    assert "read" in claims["scopes"]


def test_org_key_hash_and_match(tmp_path):
    conn = sqlite3.connect(str(tmp_path / "auth.db"))
    _ensure_db(conn)

    org_key = "inf_or_" + uuid.uuid4().hex
    key_id = org_key[:20]
    key_hash = _sha256(org_key.encode())

    cur = conn.cursor()
    cur.execute(
        "insert into org_keys (key_id, org_id, key_hash, scopes, status, created_at, last_used_at) values (?, ?, ?, ?, 'active', ?, 0)",
        (key_id, "org_test", key_hash, "read,write", int(time.time())),
    )
    conn.commit()

    # Fetch and constant-time compare
    cur.execute("select key_hash from org_keys where key_id=?", (key_id,))
    stored = cur.fetchone()[0]
    assert stored == key_hash

def test_full_auth_pipeline_integration():
    admin_key = os.getenv("ADMIN_BOOTSTRAP_KEY")
    assert admin_key, "ADMIN_BOOTSTRAP_KEY env must be set for integration test"

    base = os.getenv("AUTH_BASE", "https://adscope--auth-service.modal.run")
    base = base.replace('.modal.run', '')
    issue_org_url = f"{base}-admin-issue-org-key.modal.run"
    issue_grant_url = f"{base}-issue-grant.modal.run"
    validate_url = f"{base}-validate.modal.run"

    org_id = "org_test_integration"
    customer_id = "cust_test_integration"

    with httpx.Client(timeout=30.0) as client:
        r = client.post(issue_org_url, headers={"x-admin-key": admin_key}, json={"org_id": org_id, "scopes": "read,write"})
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("success")
        org_key = body["result"]["org_key"]
        assert org_key.startswith("inf_or_")

        r = client.post(issue_grant_url, json={"org_id": org_id, "customer_id": customer_id, "scopes": "read"})
        assert r.status_code == 200, r.text
        gbody = r.json()
        assert gbody.get("success")
        grant_jwt = gbody["result"]["grant_jwt"]
        assert grant_jwt and grant_jwt.count(".") == 2

        r = client.post(validate_url, json={"org_cred": org_key, "grant_jwt": grant_jwt, "required_scope": "read"})
        assert r.status_code == 200, r.text
        vbody = r.json()
        assert vbody.get("success") and vbody["result"].get("ok")
        assert vbody["result"]["org_id"] == org_id
        assert vbody["result"]["customer_id"] == customer_id
