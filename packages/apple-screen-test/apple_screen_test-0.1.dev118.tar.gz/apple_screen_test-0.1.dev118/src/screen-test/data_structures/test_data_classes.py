import base64
from dataclasses import dataclass, field
from enum import Enum
from typing import List

import pytest
from database_manager import logger

from cakepy.utils.path_utils import get_json_path_matches_values
from content_types import BOX_SET, UMCContentType, SEASON, EPISODE
from locales import LocaleInfo
from test_data_keys import CanvasTypes, ContentDatas, ContentTypes, RoleTypes, \
    LeagueNames, SportNames


def encrypt_password(password):
    return base64.b64encode(bytes(password, 'utf-8'))


@dataclass
class Account:
    dsid: str
    cid: str
    email: str = field(default_factory=str)
    # b64 encoded password
    encrypted_password: bytes = field(default_factory=bytes)
    protected: bool = False

    def decrypt_password(self):
        return base64.b64decode(self.encrypted_password).decode('utf-8')


@dataclass
class LeagueProperty:
    league: LeagueNames


@dataclass
class UMCContent:
    id: str
    name: str
    type: UMCContentType

    description: str = None
    umc_tag: str = None
    roles: list[RoleTypes] = None
    adam_id: str = None
    adam_id_monthly: str = None
    adam_id_seasonal: str = None
    related_content: dict = field(default_factory=dict)
    secondary_id: str = None
    required_entitlement: list = field(default_factory=list)

    def get_content(self, content_key):
        if self.related_content:
            return self.related_content.get(content_key)

    def get_product_api_path_with_id(self, season_show_id=None, use_adam_id=False):
        if season_show_id:
            return self.type.product_api_path.format(season_show_id, self.id)
        if use_adam_id:
            return self.type.product_api_path + self.adam_id
        return self.type.product_api_path + self.id

    def get_metadata_api_path_with_id(self):
        return self.type.metadata_api_path.format(self.id)


@dataclass
class Episode(UMCContent):
    show_id: str = ""
    type: UMCContentType = field(default_factory=EPISODE)


@dataclass
class Season(UMCContent):
    show_id: str = ""
    type: UMCContentType = field(default_factory=SEASON)


@dataclass
class BoxSet(UMCContent):
    show_id: str = ""
    show_reference_id: str = ""
    type: UMCContentType = field(default_factory=BOX_SET)


@dataclass
class Sport(UMCContent):
    leagues: list[LeagueNames] = field(default_factory=dict)
    type: ContentTypes = ContentTypes.SPORT


@dataclass
class SportingEvent(UMCContent):
    league_name: str = ''


@dataclass
class LeagueAvailability(LeagueProperty):
    value: any


@dataclass
class League(UMCContent):
    competitors: dict = field(default_factory=dict)
    type: ContentTypes = ContentTypes.LEAGUE
    sport: SportNames = SportNames.UNKNOWN
    abbreviation: str = ''


@dataclass
class Person(UMCContent):
    type: ContentTypes = ContentTypes.PERSON
    roles: list = field(default_factory=list)

    def get_sports_teams(self, uts_admin_client):
        person_info = uts_admin_client.get_storage_index_debug_info(self.id)
        return get_json_path_matches_values('$.Person.debugView.sportsTeamIds[*]', person_info.resp_json)


@dataclass
class Role(UMCContent):
    type: ContentTypes = ContentTypes.OTHER
    roles: list = field(default_factory=list)


@dataclass
class Canvas:
    # generic
    canvas_type: CanvasTypes
    id: str  # edt.cvs
    name: str  # Watch Now
    media_content: dict = field(default_factory=dict)
    up_next_fallback: dict = field(default_factory=dict)
    # Get salable adam ids by going to debugger url and searching for channel_id
    # ie: https://uts-api-debugger-itms11.itunes.apple.com/US/en_US/uts/debugger/debug2/tvs.sbd.7000
    # click relations > find right locale, and click on that
    # click metadata tab, then click SubscriptionInfo and look for AdamIds
    salable_adam_id: str = ''
    parent_id: [str] = None
    child_ids: List[str] = field(default_factory=list)
    salable_adam_id_out_market: str = ''
    salable_adam_id_in_market: str = ''
    collection_items: dict = field(default_factory=dict)
    shelves_under_test: dict = field(default_factory=dict)

    # canvas
    vod_service: str = ''
    external_service_id: str = ''
    external_id: str = ''
    bundle_id: str = None
    expected_shelf_displayType_pairs: dict = field(default_factory=dict)

    # root
    displayType_chart_id_startswith: str = ''

    # channel
    is_first_party: bool = False
    is_enabled_for_editorial_featuring: bool = True
    brand_equivalence_id: str = ''

    is_sports_dynamic: bool = False

    # international canvases use specific locales
    locale_info: LocaleInfo = field(default_factory=dict)

    def get_content(self, content_key) -> UMCContent:
        if self.media_content:
            return self.media_content.get(content_key)
        else:
            pytest.skip(f"[Data] There is no data for {content_key}")

    def get_collection(self, collection_key):
        if self.collection_items:
            return self.collection_items.get(collection_key)

    def get_generic_api_path(self, umc_id):
        if self.canvas_type in [CanvasTypes.GENRE, CanvasTypes.SPORT, CanvasTypes.TEAM, CanvasTypes.PERSON]:
            return self.api_path + f"{umc_id}"


@dataclass
class Context:
    display_type: Enum
    shelf: str = field(default_factory=str)
    root: str = field(default_factory=str)
    canvas: str = field(default_factory=str)
    flavor: str = field(default_factory=str)
    brand: str = field(default_factory=str)


@dataclass
class Collection:
    collection_id: str
    context_ids: dict = field(default_factory=dict)
    category_name: str = field(default_factory=str)
    items: list = field(default_factory=list)
    conductor_published_id: str = ''

    def get_canvas_id(self, context_id=None):
        return self.context_ids[context_id].canvas if context_id \
            else self.context_ids[next(iter(self.context_ids))].canvas if len(self.context_ids) > 0 else None

    def get_shelf_id(self, context_id=None):
        return self.context_ids[context_id].shelf if context_id \
            else self.context_ids[next(iter(self.context_ids))].shelf if len(self.context_ids) > 0 else None


@dataclass
class Shelf:
    shelf_id: str
    display_type: str = field(default_factory=str)


@dataclass
class Content:
    id: str
    hidden: bool
    mcCormick: bool
    hasArt: bool
    hasNote: bool

    title: str = ''
    content_type: str = ''
    visibilityStatus: str = ''
    posterToken: str = ''
    createdAt: str = ''
    lastModifiedAt: str = ''
    deleted: bool = True
    storeFronts: list[str] = field(default_factory=list[str])
    adamIds: list[str] = field(default_factory=list[str])


@dataclass
class ItunesNotes:
    databaseId: str
    resourceId: str

    title: str = ''
    shortNote: str = ''
    longNote: str = ''
    usedId: str = ''
    startDate: int = 0
    endDate: int = 0
    locale: str = ''
    createdAt: int = 0
    lastModifiedAt: int = 0
    caption: str = ''
    hero_description: str = ''
    promo_text: str = ''
    explanation: str = ''
    accessibility: str = ''

    storefronts: list[str] = field(default_factory=list[str])


@dataclass
class EditorialData:
    id: str
    iTunesNote: list[ItunesNotes]


@dataclass
class Settings:
    personId: str
    darkMode: bool
    showWarning: bool

    storefrontPresets: field(default_factory=list[dict])
    createdAt: str = ''
    lastModifiedAt: str = ''


@dataclass
class Experiments:
    id: str
    deleted: bool

    experimentType: str = ''
    createdAt: str = ''
    lastModifiedAt: str = ''
    key: str = ''
    name: str = ''
    parentKey: str = ''


@dataclass
class EditorialEvents:
    storefronts: list[str]
    platforms: list[str]
    platformVersions: dict
    startDateTime: str
    endDateTime: str


@dataclass
class MercuryExperiment:
    campaignGroupId: str
    campaignGroupToken: str


@dataclass
class BaselineExperiment:
    areaId: str
    experimentId: str
    treatmentId: str


@dataclass
class Offer:
    id: str
    name: str
    entityId: str

    primaryIntents: list[str]
    secondaryIntents: list[str] = field(default_factory=list[str])
    editorialEvents: list[dict] = field(default_factory=list[dict])
    experiment: dict = None
    entityType: str = ''
    status: str = ''
    deleted: bool = True
    createdById: int = 0
    version: int = 0
    published: bool = True
    latest: bool = True


@dataclass
class OfferPlacement:
    name: str
    api_path: str
    json_path: str
    collection_dt_keys_pair: tuple = None

    def get_full_api_path(self, test_data, canvas_key):
        if 'shelves' in self.api_path:
            collection_key = self.get_collection_key_from_offer_placement()
            collection_id = test_data.get_canvas(canvas_key).collection_items[collection_key].collection_id
            return self.api_path.format(collection_id)
        elif 'welcome-screen' in self.api_path:
            return self.api_path
        else:
            canvas_id = test_data.get_canvas_id(canvas_key)
            return self.api_path.format(canvas_id)

    def get_full_json_path(self, channel_id, content_id=None):
        if content_id:
            return self.json_path.format(channel_id, content_id)
        return self.json_path.format(channel_id)

    def get_extra_query_params_for_offer_placement(self, test_data, canvas_key):
        collection_key, dt_key = self.get_collection_key_from_offer_placement(), \
            self.get_display_type_from_offer_placement()
        context = test_data.get_canvas(canvas_key).collection_items[collection_key].context_ids[dt_key]
        return {
            'ctx_root': context.root,
            'ctx_cvs': context.canvas,
            'ctx_shelf': context.shelf,
            'ctx_dt': context.display_type.get_display_without_flavor(),
            'ctx_ft': context.flavor
        }

    def get_display_type_from_offer_placement(self):
        return self.collection_dt_keys_pair[1]

    def get_collection_key_from_offer_placement(self):
        return self.collection_dt_keys_pair[0]


@dataclass
class UTSOffer:
    offer_name: str = ''
    ad_hoc_offer_id: str = ''
    free_duration_period: str = ''
    offer_intent: str = ''
    device_purchased: str = ''
    provider_name: str = ''
    eligibility_type: str = ''
    carrier_name: str = ''
    account_types: list = field(default_factory=list)
    product_code: str = ''
    adam_id: str = ''
    offer_type: str = ''
    subscription_bundle_id: str = ''


@dataclass
class Data:
    ACCOUNTS: dict[Enum, Account]
    CANVASES: dict[Enum, Canvas]
    COLLECTIONS: dict[Enum, Collection]
    CONTENT_DATAS: dict[Enum, any]
    DIRECT_ACCESS: dict
    UTS_OFFERS: dict[Enum, UTSOffer]

    # Internal lookup map for efficient ID-based lookups
    canvases_by_id: dict[str, Canvas] = field(default_factory=dict)

    def __post_init__(self):
        # Call the hierarchy builder right after initialization
        self._build_canvas_hierarchy()

    def _build_canvas_hierarchy(self):
        """
        Builds the internal canvases_by_id map and populates children_ids
        for all canvases based on their parent_id settings.
        This runs only once at Data initialization.
        """
        # First pass: Populate canvases_by_id for lookup
        # This iterates over self.CANVASES which contains all Canvas objects
        for canvas_enum, canvas_obj in self.CANVASES.items():
            self.canvases_by_id[canvas_obj.id] = canvas_obj
            # children_ids already defaults to [], no explicit init needed here

        # Second pass: Build the children_ids lists on parent canvases
        for canvas_enum, canvas_obj in self.CANVASES.items():
            if canvas_obj.parent_id:  # If this canvas has a parent defined
                parent_canvas = self.canvases_by_id.get(canvas_obj.parent_id)
                if parent_canvas:  # If the parent actually exists in our data
                    if canvas_obj.id not in parent_canvas.child_ids:  # Avoid duplicates
                        parent_canvas.child_ids.append(canvas_obj.id)
                else:
                    logger.debug(f'Warning: Canvas \'{canvas_obj.id}\' (Enum: {canvas_enum})'
                                 f'references non-existent parent_id \'{canvas_obj.parent_id}\'.'
                                 'Check CANVAS_DEFINITIONS.')

    def get_account(self, account_enum: Enum) -> Account:
        return self.ACCOUNTS.get(account_enum)

    def get_canvas(self, canvas_enum: Enum) -> Canvas:
        return self.CANVASES.get(canvas_enum)

    def get_canvas_id(self, canvas_enum: Enum):
        canvas = self.get_canvas(canvas_enum)
        return canvas.id

    def get_canvas_api_path(self, canvas_enum: Enum):
        canvas = self.get_canvas(canvas_enum)
        return canvas.api_path

    def get_canvas_by_id(self, canvas_id: str) -> Canvas:
        """Retrieve a Canvas object directly by ID"""
        return self.canvases_by_id.get(canvas_id)

    def get_collection(self, collection_enum) -> Collection:
        return self.COLLECTIONS.get(collection_enum)

    def get_content(self, content_enum):
        return self.CONTENT_DATAS.get(content_enum)

    def get_person(self, person_enum: Enum):
        return self.CONTENT_DATAS.get(ContentDatas.PERSONS).get(person_enum)

    def get_person_id(self, person_enum: Enum):
        person = self.get_person(person_enum)
        return person.id

    def get_direct_access(self, access_key):
        return self.DIRECT_ACCESS.get(access_key)

    def get_uts_offer(self, offer_enum: Enum) -> UTSOffer:
        return self.UTS_OFFERS.get(offer_enum)


@dataclass()
class Campaign:
    id: str
    user_id: str


@dataclass
class LocaleInfo:
    locale: str = ''
    country_alpha2_code: str = ''
    country_alpha3_code: str = ''
    store_front: int = 0
    language: str = ''
    rating_systems: list = field(default_factory=list)


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
    name= "movie",
    uts_content_type=ContentTypes.MOVIE,
    product_api_path='/uts/v3/movies/',
    metadata_api_path='/uts/v3/movies/{}/metadata',
    smartPlayableKey='smartPlayables',
)

TV_SHOW = UMCContentType(
    name = "tvShow",
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
