import os
import polyline
import base64
import logging

import matplotlib
matplotlib.use('Agg')

from cartopy.io.img_tiles import GoogleTiles, Stamen
from io import BytesIO
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from group_overlapping import group_overlapping
from strava_connection import get_rides_from_strava
from constants import RESULTS_FOLDER

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig()

# https://github.com/ndoornekamp/strava-plotter
# https://matplotlib.org/stable/api/_as_gen/matplotlib.lines.Line2D.html#matplotlib.lines.Line2D.set_linewidth


def get_bounding_box(coordinates, margin):
    """
    Given a list of coordinates, returns a bounding box that contains all these coordinates
    """

    longitudes = [coordinate[1] for coordinate in coordinates]
    latitudes = [coordinate[0] for coordinate in coordinates]

    bounding_box = {}

    bounding_box["min_lon"] = min(longitudes) - margin
    bounding_box["max_lon"] = max(longitudes) + margin
    bounding_box["width"] = max(longitudes) - min(longitudes) + 2*margin
    bounding_box["min_lat"] = min(latitudes) - margin
    bounding_box["max_lat"] = max(latitudes) + margin
    bounding_box["height"] = max(latitudes) - min(latitudes) + 2*margin

    return bounding_box


def parse_rides(rides, params):
    """
    Parses the rides obtained from Strava to a list, containing a dictionary with a bounding box
    and a list of coordinates per ride
    """

    rides_parsed = []

    for ride in rides:
        if str(ride.id) in params['ids_to_skip']:
            continue

        if ride.type not in params['activity_types']:
            continue

        if ride.map.summary_polyline:  # Not all rides have a polyline
            coordinates = polyline.decode(ride.map.summary_polyline)

            bounding_box = get_bounding_box(coordinates, params['margin'])
            rides_parsed.append({**bounding_box, "coordinates": coordinates})
        
    return rides_parsed


def cluster_rides(rides, params):
    if params['clustered']:
        ride_clusters = group_overlapping(rides)
        if params['first_cluster_only']:
            ride_clusters = [ride_clusters[0]]
    else:
        ride_clusters = [rides]

    return ride_clusters


def get_ride_cluster_bounding_boxes(ride_groups, params):
    ride_group_bounding_boxes = []
    for ride_group in ride_groups:
        ride_group_coordinates = []

        for ride in ride_group:
            ride_group_coordinates += list(ride["coordinates"])

        ride_group_bounding_box = get_bounding_box(ride_group_coordinates, params['margin'])
        ride_group_bounding_boxes.append(ride_group_bounding_box)

    return ride_group_bounding_boxes


def plot_rides(ride_clusters, params):
    ride_cluster_bounding_boxes = get_ride_cluster_bounding_boxes(ride_clusters, params)
    widths = [bounding_box['width'] for bounding_box in ride_cluster_bounding_boxes]
    heights = [bounding_box['height'] for bounding_box in ride_cluster_bounding_boxes]

    nof_rows = 1
    nof_columns = len(ride_clusters)
    gs = gridspec.GridSpec(nof_rows, nof_columns, width_ratios=widths)
    images_base64 = []

    for i, ride_cluster in enumerate(ride_clusters):
        logger.debug(f"Printing cluster {i+1}/{len(ride_clusters)}, containing {len(ride_cluster)} activities")
        ride_cluster_bounding_box = ride_cluster_bounding_boxes[i]

        if not params['subplots_in_separate_files']:
            ax = plt.subplot(gs[i])
            map_ax = plot_cluster(ax, ride_cluster_bounding_box, ride_cluster, params)
        else:
            ax = plt.subplot(gridspec.GridSpec(1, 1, width_ratios=[widths[i]])[0])
            map_ax = plot_cluster(ax, ride_cluster_bounding_box, ride_cluster, params)

            if params['output_format'] == 'bytes':
                images_base64.append(plot_to_bytes(
                    plt, resolution=params['resolution'], width=widths[i], height=heights[i]))
            else:
                output_path = os.path.join(RESULTS_FOLDER, f'output{i}.png')

                if not os.path.isdir(RESULTS_FOLDER):
                    os.mkdir(RESULTS_FOLDER)

                plt.savefig(output_path, dpi=1200)

    if params['subplots_in_separate_files']:
        if params['output_format'] == 'bytes':
            return images_base64
        else:
            raise NotImplementedError(
                f"Saving subplots in separate files with output format {params['output_format']} is not yet implemented")
    else:
        plt.subplots_adjust(left=0.03, bottom=0.05, right=0.97, top=0.95, wspace=0, hspace=0)
        if params['output_format'] == 'bytes':
            return [plot_to_bytes(plt, resolution=params['resolution'])]
        elif params['output_format'] == "image":
            output_path = os.path.join(RESULTS_FOLDER, 'output.png')

            if not os.path.isdir(RESULTS_FOLDER):
                os.mkdir(RESULTS_FOLDER)

            plt.savefig(output_path, dpi=1200)
            plt.show()
        else:
            raise NotImplementedError(f"Unknown {params['output_format']}: expected either 'bytes' or 'image'")


def plot_cluster(ax, ride_cluster_bounding_box, ride_cluster, params):
    """
    Given a list of rides and its bounding box, plots this cluster the matplotlib object <ax>,
    with satellite imagery as background
    """

    # tiler = GoogleTiles()
    tiler = Stamen(style="terrain")
    mercator = tiler.crs
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection=mercator)

    bounding_box = [
        ride_cluster_bounding_box["min_lon"],
        ride_cluster_bounding_box["max_lon"],
        ride_cluster_bounding_box["min_lat"],
        ride_cluster_bounding_box["max_lat"]
    ]
    ax.set_extent(bounding_box, crs=ccrs.PlateCarree())

    logger.debug(f"Adding background image from Google with resolution level {params['resolution']}")
    ax.add_image(tiler, params['resolution'])

    for ride in ride_cluster:
        ride_longitudes = [coordinate[1] for coordinate in ride["coordinates"]]
        ride_latitudes = [coordinate[0] for coordinate in ride["coordinates"]]
        ax.plot(
            ride_longitudes,
            ride_latitudes,
            color="#fc5200",
            alpha=params["alpha"],
            linewidth=params['linewidth'],
            transform=ccrs.PlateCarree(),
            antialiased=True,
        )

    return ax


def plot_to_bytes(plt, resolution, width=None, height=None):

    scale_factor = resolution*(resolution - 4)/12

    if width and height:
        plt.gcf().set_size_inches(width*scale_factor, height*scale_factor)

    plt.gca().set_axis_off()
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=2400, bbox_inches='tight', pad_inches=0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
    buf.close()

    return image_base64


def strava_plotter():
    from settings import params

    # Set working directory to script directory
    os.chdir(os.path.dirname(__file__))
    rides_raw = get_rides_from_strava()
    rides = parse_rides(rides_raw, params)
    ride_clusters = cluster_rides(rides, params)

    logger.debug(f"Plotting {len(rides)} rides in {len(ride_clusters)} clusters")
    plot_rides(ride_clusters, params)


if __name__ == "__main__":
    strava_plotter()
