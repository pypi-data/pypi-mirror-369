from data.itms11.direct_access import direct_access_episodes, direct_access_mlb, direct_access_seasons, direct_access_mls, direct_access_sports, direct_access_league_availability, direct_access_movies, direct_access_tv_shows, direct_access_others
from test_data_classes import UMCContentType

direct_access_locations = [
    direct_access_episodes,
    direct_access_mlb,
    direct_access_mls,
    direct_access_movies,
    direct_access_others,
    direct_access_seasons,
    direct_access_sports,
    direct_access_tv_shows
]

direct_access = {}

for location in direct_access_locations:
    for key, value in location.__dict__.items():
        if not key.startswith('__') and not (isinstance(value, type) or isinstance(value, UMCContentType)):
            if key in direct_access.keys():
                raise Exception(f'Duplicate definition of {key} in direct_access.')
            else:
                direct_access[key] = value
