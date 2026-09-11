import json
import os
import sys
import urllib.request
import urllib.parse

sci_tenant_url = os.environ.get("SCI_TENANT_URL", "")
sci_client_id = os.environ.get("SCI_CLIENT_ID", "")

# --- Validate inputs ---
errors = []
if not sci_tenant_url:
    errors.append("input 'SCI_TENANT_URL' is required but not set")
if not sci_client_id:
    errors.append("input 'SCI_CLIENT_ID' is required but not set")
if not os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL"):
    errors.append("ACTIONS_ID_TOKEN_REQUEST_URL is not set — ensure 'id-token: write' permission is granted to the job")
if not os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN"):
    errors.append("ACTIONS_ID_TOKEN_REQUEST_TOKEN is not set — ensure 'id-token: write' permission is granted to the job")
if not os.environ.get("GITHUB_OUTPUT"):
    errors.append("GITHUB_OUTPUT is not set — this script must run inside a GitHub Actions job")
if errors:
    for e in errors:
        print(f"Error: {e}")
    sys.exit(1)

# --- Get short-lived GitHub-issued OIDC JWT ---
token_request_url = os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"]
token_request_token = os.environ["ACTIONS_ID_TOKEN_REQUEST_TOKEN"]

req = urllib.request.Request(
    f"{token_request_url}&audience={sci_tenant_url}",
    headers={
        "Authorization": f"Bearer {token_request_token}",
        "Accept": "application/json; api-version=2.0",
        "Content-Type": "application/json",
    },
)
try:
    with urllib.request.urlopen(req) as resp:
        github_jwt = json.loads(resp.read())["value"]
except urllib.error.HTTPError as e:
    print(f"Error: Failed to fetch GitHub OIDC token: {e.code}: {e.read().decode()}")
    sys.exit(1)

# --- Exchange GitHub JWT for SCI token ---
payload = urllib.parse.urlencode({
    "grant_type": "client_credentials",
    "client_id": sci_client_id,
    "resource": "urn:sap:identity:application:provider:name:build",
    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
    "client_assertion": github_jwt,
}).encode()

req = urllib.request.Request(
    f"{sci_tenant_url}/oauth2/token",
    data=payload,
    method="POST",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
)
try:
    with urllib.request.urlopen(req) as resp:
        response = json.loads(resp.read())
except urllib.error.HTTPError as e:
    print(f"Error: SCI token request failed with status {e.code}: {e.read().decode()}")
    sys.exit(1)

sci_token = response.get("access_token")
if not sci_token:
    print(f"Error: sci_token was not retrieved. Response: {response}")
    sys.exit(1)

print("sci_token successfully retrieved")

# Write output for downstream jobs
with open(os.environ["GITHUB_OUTPUT"], "a") as f:
    f.write(f"sciToken={sci_token}\n")
