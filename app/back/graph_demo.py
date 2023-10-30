import json

import requests
from msal import ConfidentialClientApplication

# client_id = "61afd86f-3c9f-4a5e-91b8-e00c71e9d9ec"
# client_secret ="gkS8Q~PiXgyZIKr-hz_vtjREooyGbP1F4g3lYcf0"
# tenant_id = "58f8d266-6165-48bb-afad-4f8e51286b57"

client_id = "9753e1da-5aea-4636-afae-82d14f94cb39"
client_secret ="UjJ8Q~bJIfTeySmkF8yAjtnPjG101A9MJs-Sgdyy"
tenant_id = "58f8d266-6165-48bb-afad-4f8e51286b57"

msal_authority = f"https://login.microsoftonline.com/{tenant_id}"

msal_scope = ["https://graph.microsoft.com/.default"]

msal_app = ConfidentialClientApplication(
    client_id=client_id,
    client_credential=client_secret,
    authority=msal_authority,
)

result = msal_app.acquire_token_silent(
    scopes=msal_scope,
    account=None,
)

if not result:
    result = msal_app.acquire_token_for_client(scopes=msal_scope)

if "access_token" in result:
    access_token = result["access_token"]
else:
    raise Exception("No Access Token found")

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
}

file_ids = f"https://onedrive.live.com/?id=root&cid=128F10A92846F712"

response = requests.get(
    url= f"https://graph.microsoft.com/v1.0/users/84f7287e-6431-4ded-bbf2-717397fbd45c/drives/128f10a92846f712",
    headers=headers,
)

print(json.dumps(response.json(), indent=4))
