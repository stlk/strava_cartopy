# Strava Cartopy

Fork of https://github.com/ndoornekamp/strava-plotter designed to use latest versions and stravalib to load data.


To get `STRAVA_CLIENT_ID` and `STRAVA_CLIENT_SECRET` create app at https://developers.strava.com/.

To run the environment:

```sh
docker-compose run --rm strava_cartopy

# When inside the container
cd app

# To get STRAVA_REFRESH_TOKEN
dotenv run python authorize.py

# To generate map of your last actvity
dotenv run python generate_map.py

# To generate heatmaps of your all rides clustered as descibed in https://nddoornekamp.medium.com/plotting-strava-data-with-python-7aaf0cf0a9c3
python strava_plotter.py
```
