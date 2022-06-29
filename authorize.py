import os
from stravalib.client import Client

client_id = os.environ.get("STRAVA_CLIENT_ID")
client_secret = os.environ.get("STRAVA_CLIENT_SECRET")

client = Client()
authorize_url = client.authorization_url(
    client_id=client_id, redirect_uri="http://localhost:8000/authorized"
)

# Have the user click the authorization URL, a 'code' param will be added to the redirect_uri
print(
    "Authorise the app in your browser and copy the 'code' parameter from the URL you are redirected to, then press Enter"
)
print(authorize_url)

authorisation_code = input("code:")

token_response = client.exchange_code_for_token(
    client_id=client_id, client_secret=client_secret, code=authorisation_code
)
access_token = token_response["access_token"]
refresh_token = token_response["refresh_token"]
expires_at = token_response["expires_at"]
print(token_response)
