import json

import requests
import msal
client_id = "9753e1da-5aea-4636-afae-82d14f94cb39"
client_secret ="R3C8Q~JD3.IQUw4ySDhcRKb_w.cxn8akA-XGhcUo"
tenant_id = "58f8d266-6165-48bb-afad-4f8e51286b57"

#msal_authority = f"https://login.microsoftonline.com/{tenant_id}"

msal_authority = f"https://login.microsoftonline.com/common"

msal_scope = ["https://graph.microsoft.com/.default"]

msal_app = msal.ConfidentialClientApplication(
    client_id=client_id,
    authority=msal_authority,
    client_credential=client_secret
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

file_ids = '128F10A92846F712%21106'
user_id="84f7287e-6431-4ded-bbf2-717397fbd45c"

response = requests.get(
    url=f"https://graph.microsoft.com/v1.0/drives/{user_id}/items/{file_ids}/children/?select=name,id",
    headers=headers,
)

print(json.dumps(response.json(), indent=4))
