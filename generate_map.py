import polyline
import logging

import os, pathlib
import matplotlib.patheffects as pe
import matplotlib

from stravalib.client import Client
from cartopy.io.img_tiles import GoogleTiles, Stamen
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

matplotlib.use("Agg")


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig()


# https://github.com/ndoornekamp/strava-plotter
# https://matplotlib.org/stable/api/_as_gen/matplotlib.lines.Line2D.html#matplotlib.lines.Line2D.set_linewidth


params = {
    "margin": 0.01,  # Margin by which bounding boxes are extended (in degrees)
    "alpha": 1,
    "resolution": 13,
    "linewidth": 0.5,
    "outline": True,
}


def get_bounding_box(coordinates, margin):
    """
    Given a list of coordinates, returns a bounding box that contains all these coordinates
    """

    longitudes = [coordinate[1] for coordinate in coordinates]
    latitudes = [coordinate[0] for coordinate in coordinates]

    return {"min_lon": min(longitudes) - margin, "max_lon": max(longitudes) + margin, "width": max(longitudes) - min(longitudes) + 2 * margin, "min_lat": min(latitudes) - margin, "max_lat": max(latitudes) + margin, "height": max(latitudes) - min(latitudes) + 2 * margin}


def parse_ride(ride):
    coordinates = polyline.decode(ride.map.summary_polyline)

    bounding_box = get_bounding_box(coordinates, params["margin"])
    return {**bounding_box, "coordinates": coordinates}


def generate_map_from_last_ride(client, root):
    # activity = next(client.get_activities(limit=1))
    activity = client.get_activity(7264144562)
    parsed_activity = parse_ride(activity)

    # tiler = Stamen("toner")
    tiler = GoogleTiles()
    mercator = tiler.crs
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection=mercator)

    logger.debug(
        f"Adding background image with resolution level {params['resolution']}"
    )
    ax.add_image(tiler, params["resolution"])

    bounding_box = [
        parsed_activity["min_lon"],
        parsed_activity["max_lon"],
        parsed_activity["min_lat"],
        parsed_activity["max_lat"],
    ]
    ax.set_extent(bounding_box, crs=ccrs.PlateCarree())

    if params["outline"]:
        path_effects = [
            pe.Stroke(linewidth=params["linewidth"] * 2.5, foreground="w"),
            pe.Normal(),
        ]
    else:
        path_effects = []

    ride_longitudes = [coordinate[1] for coordinate in parsed_activity["coordinates"]]
    ride_latitudes = [coordinate[0] for coordinate in parsed_activity["coordinates"]]
    ax.plot(
        ride_longitudes,
        ride_latitudes,
        color="#fc5200",
        alpha=params["alpha"],
        linewidth=params["linewidth"],
        transform=ccrs.PlateCarree(),
        antialiased=True,
        path_effects=path_effects,
    )

    output_path = root / "output.png"

    # plt.tight_layout()
    plt.savefig(output_path, dpi=400, bbox_inches='tight', pad_inches=-0.02)
    plt.show()


if __name__ == "__main__":
    root = pathlib.Path(__file__).parent.resolve()

    client_id = os.environ.get("STRAVA_CLIENT_ID")
    client_secret = os.environ.get("STRAVA_CLIENT_SECRET")
    refresh_token = os.environ.get("STRAVA_REFRESH_TOKEN")
    client = Client()

    refresh_response = client.refresh_access_token(
        client_id=client_id, client_secret=client_secret, refresh_token=refresh_token
    )
    client.access_token = refresh_response["access_token"]
    generate_map_from_last_ride(client, root)