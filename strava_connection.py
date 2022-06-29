import os
import logging

from dotenv import load_dotenv

load_dotenv('.env')

logger = logging.getLogger(__name__)


from stravalib.client import Client

client_id = os.environ.get("STRAVA_CLIENT_ID")
client_secret = os.environ.get("STRAVA_CLIENT_SECRET")
refresh_token = os.environ.get("STRAVA_REFRESH_TOKEN")


def get_rides_from_strava():
    client = Client()

    refresh_response = client.refresh_access_token(client_id=client_id, client_secret=client_secret,refresh_token=refresh_token)
    client.access_token = refresh_response['access_token']

    return client.get_activities()

