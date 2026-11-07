"""Verify actual service-account tokens, rejection and A2A access in the local lab."""

import time

import httpx

from common.config import ROOT
from common.protocol import as_dict, request


def main():
    env = dict(
        line.split("=", 1)
        for line in (ROOT / "deploy/secrets/network.env").read_text().splitlines()
        if "=" in line
    )
    issuer = "http://127.0.0.1:8080/realms/maplewood"
    with httpx.Client(timeout=5) as http:
        for _ in range(120):
            try:
                if http.get("http://127.0.0.1:8106/health").status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(1)
        else:
            raise RuntimeError("OIDC lab is not ready; check Keycloak and oidc-venue logs.")
        endpoint = issuer + "/protocol/openid-connect/token"
        credentials = {
            "grant_type": "client_credentials",
            "client_id": "concierge",
            "client_secret": env["OIDC_CLIENT_SECRET"],
        }
        assert (
            http.post(endpoint, data={**credentials, "client_secret": "wrong"}).status_code == 401
        )
        response = http.post(endpoint, data=credentials)
        response.raise_for_status()
        token = response.json()["access_token"]
        url = "http://127.0.0.1:8106/message:send"
        message = as_dict(request({"guests": 40}))
        assert http.post(url, json=message).status_code == 401
        assert (
            http.post(url, json=message, headers={"Authorization": "Bearer forged"}).status_code
            == 401
        )
        response = http.post(
            url, json=message, headers={"Authorization": "Bearer " + token, "A2A-Version": "1.0"}
        )
        response.raise_for_status()
        assert response.json()["task"]["status"]["state"] == "TASK_STATE_COMPLETED"
    print(
        "Keycloak: bad secret and forged/missing tokens rejected; real token completed the A2A quote."
    )


if __name__ == "__main__":
    main()
