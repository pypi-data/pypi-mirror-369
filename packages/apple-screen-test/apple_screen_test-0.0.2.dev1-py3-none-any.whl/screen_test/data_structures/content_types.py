from dataclasses import dataclass, field

from test_data_keys import ContentTypes


@dataclass
class UMCContentType:
    name: str = ''
    uts_content_type: str = ''
    product_api_path: str = ''
    metadata_api_path: str = ''
    smartPlayableKey: str = ''
    is_sporting_event: bool = False
    show_url_path_var: str = field(init=False)
    has_show_url: bool = field(init=False)

    def __post_init__(self):
        self.show_url_path_var = self.uts_content_type.lower()
        if self.uts_content_type == ContentTypes.MOVIE_BUNDLE:
            self.show_url_path_var = 'movie-bundle'
        self.has_show_url = self.uts_content_type in [ContentTypes.EPISODE, ContentTypes.SEASON,
                                                      ContentTypes.BOXSET]


MOVIE = UMCContentType(
    name="movie",
    uts_content_type=ContentTypes.MOVIE,
    product_api_path='/uts/v3/movies/',
    metadata_api_path='/uts/v3/movies/{}/metadata',
    smartPlayableKey='smartPlayables',
)

TV_SHOW = UMCContentType(
    name="tvShow",
    uts_content_type=ContentTypes.TV_SHOW,
    product_api_path='/uts/v3/shows/',
    metadata_api_path='/uts/v3/shows/{}/metadata',
    smartPlayableKey='smartEpisodePlayables'
)

EPISODE = UMCContentType(
    name="episode",
    uts_content_type=ContentTypes.EPISODE,
    product_api_path='/uts/v3/episodes/',
    metadata_api_path="/uts/v3/episodes/{}/metadata",
    smartPlayableKey='smartPlayables'
)

SEASON = UMCContentType(
    name="season",
    uts_content_type=ContentTypes.SEASON,
    product_api_path='/uts/v3/shows/{}/{}',
    metadata_api_path="/uts/v3/seasons/{}/metadata",
)

MOVIE_BUNDLE = UMCContentType(
    name="movieBundle",
    uts_content_type=ContentTypes.MOVIE_BUNDLE,
    product_api_path='/uts/v3/movie-bundles/',
)

LIVE_SPORTING_EVENT = UMCContentType(
    name='liveSportingEvent',
    uts_content_type=ContentTypes.SPORTING_EVENT,
    product_api_path='/uts/v3/sporting-events/',
    metadata_api_path='/uts/v3/sporting-events/{}/metadata',
    smartPlayableKey='smartPlayables'
)

UPCOMING_SPORTING_EVENT = UMCContentType(
    name='upcomingSportingEvent',
    uts_content_type=ContentTypes.SPORTING_EVENT,
    product_api_path='/uts/v3/sporting-events/',
    metadata_api_path='/uts/v3/sporting-events/{}/metadata',
    smartPlayableKey='smartPlayables'
)

PAST_SPORTING_EVENT = UMCContentType(
    name='pastSportingEvent',
    uts_content_type=ContentTypes.SPORTING_EVENT,
    product_api_path='/uts/v3/sporting-events/',
    metadata_api_path='/uts/v3/sporting-events/{}/metadata',
    smartPlayableKey='smartPlayables'
)

STATIC_SPORTING_EVENT = UMCContentType(
    name='staticSportingEvent',
    uts_content_type=ContentTypes.SPORTING_EVENT,
    product_api_path='/uts/v3/sporting-events/',
    metadata_api_path='/uts/v3/sporting-events/{}/metadata',
    smartPlayableKey='smartPlayables'
)

EXTRA = UMCContentType(
    name='extra',
    uts_content_type='Extra',
    product_api_path='/uts/v3/extra/',
)

BOX_SET = UMCContentType(
    name='box_set',
    uts_content_type=ContentTypes.BOXSET,
    product_api_path='/uts/v3/boxsets/'
)

LIVE_SERVICE = UMCContentType(
    name="liveService",
    uts_content_type=ContentTypes.LIVE_SERVICE
)

SPORTING_EVENTS = [LIVE_SPORTING_EVENT, UPCOMING_SPORTING_EVENT, PAST_SPORTING_EVENT, STATIC_SPORTING_EVENT]
