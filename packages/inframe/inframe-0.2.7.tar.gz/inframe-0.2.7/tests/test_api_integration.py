import os
import json
import httpx


def _normalize_base(s: str) -> str:
    s = s.strip()
    if s.startswith("http://") or s.startswith("https://"):
        s = s.split("://", 1)[1]
    if s.endswith(".modal.run"):
        s = s[: -len(".modal.run")]
    if s.endswith("/"):
        s = s[:-1]
    return s


def test_issue_keys_and_call_query_endpoint():
    admin_key = os.getenv("ADMIN_BOOTSTRAP_KEY")
    assert admin_key, "ADMIN_BOOTSTRAP_KEY must be set for this integration test"

    auth_base = _normalize_base(os.getenv("AUTH_BASE", "https://adscope--auth-service"))
    query_base = _normalize_base(os.getenv("QUERY_BASE", "https://adscope--query-service"))

    issue_org_url = f"https://{auth_base}-admin-issue-org-key.modal.run"
    issue_grant_url = f"https://{auth_base}-issue-grant.modal.run"
    query_url = f"https://{query_base}-query-v1.modal.run"

    org_id = "org_test_e2e"
    customer_id = "cust_test_e2e"

    with httpx.Client(timeout=30.0) as client:
        r = client.post(issue_org_url, headers={"x-admin-key": admin_key}, json={"org_id": org_id, "scopes": "read,write"})
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("success"), body
        org_key = body["result"]["org_key"]

        g = client.post(issue_grant_url, headers={"authorization": f"Bearer {org_key}"}, json={"org_id": org_id, "customer_id": customer_id, "scopes": "read"})
        assert g.status_code == 200, g.text
        gbody = g.json()
        assert gbody.get("success"), gbody
        grant_jwt = gbody["result"]["grant_jwt"]

        q = client.post(
            query_url,
            headers={"authorization": f"Bearer {org_key}", "x-grant": grant_jwt, "content-type": "application/json"},
            json={"question": "What happened?", "session_id": customer_id, "top_k": 3, "min_similarity": 0.2},
        )
        assert q.status_code == 200, q.text
        qbody = q.json()
        assert isinstance(qbody, dict)
        assert "success" in qbody
        # It may return success False if no frames are present; that's acceptable for this auth/path test


