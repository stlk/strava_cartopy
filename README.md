# Strava Cartopy

Fork of https://github.com/ndoornekamp/strava-plotter designed to use latest versions and stravalib to load data.


To get `STRAVA_CLIENT_ID` and `STRAVA_CLIENT_SECRET` create app at https://developers.strava.com/.

To run the environment:

```sh
docker-compose run --rm readme

# When inside the container
cd app

# To get STRAVA_REFRESH_TOKEN
dotenv run python authorize.py

# To generate map of your last actvity
dotenv run python generate_map.py

# To generate heatmaps of your all rides clustered as descibed in https://nddoornekamp.medium.com/plotting-strava-data-with-python-7aaf0cf0a9c3
python strava_plotter.py
```


## Future

I would love to try automating zoom selection. This snippet from SO might do the trick.

```c#
/// <summary>
/// Zoom map to fit the desired distance from point
/// </summary>
/// <param name="mapSize">The size of the control (map size in pixels)</param>
/// <param name="coverage">Ratio of the map, normally 70 (70%)</param>
/// <param name="latitude">Latitude where the point to draw is located</param>
/// <param name="distance">Distance to show from this point in meters</param>
/// <param name="minZoomLevel">Min level of zoom (normally 18)</param>
/// <param name="maxZoomLevel">Max level of zoom (normally 1)</param>
/// <returns>Zoom level</returns>
static double CalculateGMapZoom(Size mapSize, int coverage, double latitude, double distance, int minZoomLevel, int maxZoomLevel)
{
    int pixels = mapSize.Width >= mapSize.Height ? mapSize.Height : mapSize.Width; //get the shortest dimmension of the map   
    double k = (double)pixels * 156543.03392 * Math.Cos(latitude * Math.PI / 180); 
    int zoom = (int)((Math.Round(Math.Log((coverage * k) / (distance * 100)) / 0.6931471805599453)) - 1);
    return (zoom > maxZoomLevel ? (double)maxZoomLevel: (zoom < minZoomLevel ? (double)minZoomLevel: (double)zoom));
}
```