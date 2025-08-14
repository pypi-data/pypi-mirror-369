from enum import Enum, auto, StrEnum


class AccountTypes(Enum):
    CONTINUE_WATCHING_TESTS = auto()
    CONTINUE_WATCHING_TESTS_PRESET = auto()
    UP_NEXT_TESTS = auto()
    FAVORITES_TESTS = auto()
    DUMMY_PROTECTED_ACCOUNT = auto()
    UNUSED_ACCOUNT_B = auto()
    UNUSED_ACCOUNT_A = auto()
    DEFAULT_DEBUG_USER = auto()  # Default user dsid and cid to mock subscriptions
    COLD_START = auto()  # Unsigned in user, always empty dsid and cid
    SAI_DEBUGGER_USER = auto()  # User with prototype features

    # Commerce Subscribed Accounts for Offers Testing
    TV_PLUS_SUBSCRIBED = auto()
    TV_PLUS_UNSUBSCRIBED = auto()
    MLS_SUBSCRIBED = auto()
    MLS_SUBSCRIBED_ANNUALLY = auto()

    # ALLOW_LISTED ACCOUNTS
    PURPLE_ALLOW_LISTED = auto()  # User with access to purple channel

    # ETC
    IN_ALL_COHORT_RULES = auto()  # satisfies all cohort rules
    PERSONALIZATION_OPTED_OUT = auto()  # opted out personalized recommendations on device
    MLS_MONTHLY = auto()  # Not an account
    MLS_SEASON = auto()  # Not an account
    SPORTS_TASTE_PROFILE = auto()  # Account with sports taste profile
    U13_ACCOUNT = auto()  # Account with under 13 age

    # Users with manipulations for specific tests
    USER_SETTINGS_TESTS = auto()

    WITH_ITEMS_IN_UP_NEXT = auto()
    WITH_SPORTING_EVENTS_IN_UP_NEXT = auto()
    WITH_SPORT_FAVORITES = auto()
    WITH_BOX_SET_PURCHASE = auto()
    RECO_WITH_PLAY_ACTIVITY = auto()
    ITUNES_CONTENT_ENTITLED = auto()  # Account with purchased items
    MLS_TV_PLUS_SUBSCRIBED = auto()  # User subscribed to mls and tv+
    ADULT_SIMPLE_PROFILE = auto()
    CHILD_SIMPLE_PROFILE = auto()
    SPONSOR_ACCOUNT_WITH_SIMPLE_PROFILES = auto()

    SHOW_NEVER_WATCHED_SUBSCRIBED = auto()
    SHOW_CAUGHT_UP_CLEAN_SUBSCRIBED = auto()
    SHOW_2_CAUGHT_UP_CLEAN_SUBSCRIBED = auto()
    SHOW_CAUGHT_UP_DIRTY_OLD_SUBSCRIBED = auto()
    SHOW_CAUGHT_UP_DIRTY_NEW_SUBSCRIBED = auto()
    SHOW_NOT_IN_COHORT_WATCHED_WITHIN_24HR_SUBSCRIBED = auto()
    SHOW_NOT_IN_COHORT_WATCHED_LESS_THAN_15MIN_SUBSCRIBED = auto()

    # Users with play-history set up to test sidebar smart filtering of brands.
    SMART_FILTERING_PLAY_HISTORY_CASES_MCC = auto()
    SMART_FILTERING_PLAY_HISTORY_CASES_FED = auto()

    # CIP Offers
    CIP_A1_PREMIER = auto()  #
    CIP_A1_FAMILY = auto()
    CIP_A1_INDIVIDUAL = auto()
    CIP_HARD_BUNDLE = auto()
    CIP_EXTENDED_OFFER = auto()
    CIP_BARCLAYSGB_FIN_ATV_HB = auto()
    CIP_TELUSCA_MVPD_ATV_HB = auto()
    CIP_TELUSCA_MVPD_ATV_PMEO_6M = auto()
    CIP_TOTALPLAYMX_MVPD_ATV_CPAID = auto()
    CIP_TOTALPLAYMX_MVPD_ATV_HB = auto()
    CIP_TOTALPLAYMX_MVPD_ATV_PMEO_3M = auto()
    CIP_CTUS_MVPD_ATV_CPAID = auto()
    CIP_CTUSXUMO_MVPD_ATV_CPAID = auto()

    # Channel Offers
    HARMONY = auto()  # New apple device offer
    HARMONY2 = auto()  # New apple device offer
    HARMONY_WINBACK = auto()  # New apple device offer extended if never redeemed
    TV_PLUS_BURNED = auto()  # Unsubscribed user who used intro offer and now only has regular offer
    MCC1_INTRO = auto()  # Unsubscribed user with intro offer (same as DEFAULT_DEBUG)
    MCC1_BURNED = auto()  # Unsubscribed user who used intro offer and now only has regular offer
    MCC2_INTRO = auto()  # Unsubscribed user with intro offer (same as DEFAULT_DEBUG)
    MCC2_BURNED = auto()  # Unsubscribed user who used intro offer and now only has regular offer
    MLS_BURNED = auto()  # Unsubscribed user who was a subscriber and now only has regular offer
    MLS_SEASON_SUBSCRIBED = auto()
    MLS_NOT_SUBSCRIBED = auto()
    TV_PLUS_PARAMOUNT_SUBSCRIBED = auto()
    TV_PLUS_SUBSCRIBED_MLS_NOT_SUBSCRIBED = auto()
    TV_PLUS_PARAMOUNT_BURNED = auto()
    TV_PLUS_PARAMOUNT_NOT_SUBSCRIBED = auto()

    # Hardware offers
    PLAYSTATION4 = auto()  # User with PS4 hardware offer
    PLAYSTATION5 = auto()  # User with PS5 hardware offer
    LG = auto()  # User with LG hardware offer
    VIZIO = auto()  # User with Vizio hardware offer
    TELSTRA = auto()  # User with telstra hardware offer
    COMCAST = auto()  # User with comcast hardware offer


class CanvasNames(Enum):
    PLATO_TV_PLUS = auto()
    DISPLAY_TYPES_ROOM = auto()
    RICH_HEADERS_ROOM = auto()
    AE = auto()
    HBO_GO = auto()
    CATEGORY_BRICK_ROOM = auto()
    CANVAS_WITH_SPORTS_TEAMS_SHELVES = auto()
    MLB_AT_BAT = auto()
    MARCH_MADNESS_LIVE = auto()
    WITH_CHANNEL_HEADER = auto()
    COMING_TO_APPLE_TV_PLUS = auto()
    TV_PLUS = auto()
    MLB_TV = auto()
    MLS = auto()
    CHAPMAN = auto()
    SHOWTIME_MCCORMICK = auto()
    EVERGREEN_MCCORMICK = auto()
    OTHER = auto()
    SLING = auto()
    PLUTO_TV = auto()
    TUBI = auto()
    COMEDY_CENTRAL = auto()
    TBS = auto()
    TV = auto()
    MGM_PLUS = auto()
    CBS = auto()
    NETFLIX = auto()
    AMAZON_FREEVE = auto()
    AT_T_TV = auto()
    MAX = auto()
    PHILO = auto()
    ITUNES = auto()
    DISNEY_PLUS = auto()
    ESPN = auto()
    TAHOMA_SPORTS = auto()
    TAHOMA_WATCH_NOW = auto()
    TAHOMA_MOVIES = auto()
    TAHOMA_TV_SHOWS = auto()
    TAHOMA_KIDS = auto()
    TAHOMA_STORE = auto()
    TAHOMA_SEARCH_LANDING = auto()
    TAHOMA_VISION = auto()
    PURPLE = auto()
    AMETHYST = auto()
    MUSIC = auto()
    EPIC_STAGE_OFFER = auto()
    AB_CAPABILITIES_ONE_AREA_CONTROL_TREATMENT = auto()
    AB_CAPABILITIES_ONE_AREA = auto()
    AB_CAPABILITIES_MULTIPLE_AREA = auto()
    SEO_TEST_ROOM = auto()
    TNT_EAST = auto()
    CAMPAIGN_TEST_ROOM = auto()
    CANVAS_COHORT_METRICS_ROOM = auto()
    PERSONALIZATION_TEST_ROOM = auto()
    PERSONALIZATION_MODIFIED_SCORE_ROOM = auto()
    CHANNEL_CONTAINING_BPP_SHELVES = auto()
    ACORN_TV = auto()
    EPIX_MCCORMICK = auto()
    PARAMOUNT_PLUS_MCCORMICK = auto()
    PARAMOUNT_PLUS_FEDERATED = auto()
    STARZ_MCCORMICK = auto()
    STARZ_FEDERATED = auto()
    LIFETIME_MOVIE_CLUB = auto()
    HULU = auto()
    FOX_NOW = auto()
    CBS_ALL_ACCESS = auto()
    BRITBOX = auto()
    SUNDANCE_NOW = auto()
    FREEFORM = auto()
    PRIME_VIDEO = auto()
    WITH_ONDEMAND_LSE = auto()
    WITHOUT_ONDEMAND_LSE = auto()
    COOKING_CHANNEL = auto()
    MLB_ROOM = auto()
    EMPTY_CHANNEL = auto()
    NOGGIN = auto()
    DISCOVERY_PLUS = auto()
    BET_PLUS_MCCORMICK = auto()
    FEDERATED_APP_WITHOUT_CANVAS = auto()
    FEDERATED_APP_WITHOUT_EDITORIALFEATURING_FLAGS = auto()
    MCCORMICK_CHANNEL_WITHOUT_EDITORIALFEATURING_FLAGS = auto()
    AMC_PLUS_MCC = auto()
    AMC_PLUS_FED = auto()
    IFC_FILMS = auto()
    MCSMITHSONIAN = auto()
    PEACOCK = auto()
    MCPEACOCK = auto()
    NBC_SPORTS = auto()
    CBS_SPORTS = auto()
    CNBC = auto()
    RED = auto()
    SHELVES_WITH_LOCALE_AVAILABILITY = auto()
    SHOWS_WITH_BOX_SET_ITEMS_ON_SHELVES = auto()
    PERSONALIZATION_BLVR_ROOM = auto()
    HIDE_ENTITLEMENT_TEST_ROOM = auto()
    EPIC_STAGE_BRAND_INTENT = auto()
    GENERIC_SPORT = auto()
    GENERIC_PERSON = auto()
    GENERIC_TEAM = auto()
    GENERIC_GENRE = auto()
    TELEMUNDO = auto()
    HISTORY = auto()

    # Runtime Canvases
    RUNTIME_SPORTS = auto()
    RUNTIME_KIDS = auto()
    RUNTIME_TV_PLUS = auto()

    # Tier 2 Federated US
    PARAMOUNT_PLUS_TIER2_US = auto()
    ANIMAL_PLANET = auto()

    # Tier 2 Federated International
    DISNEY_PLUS_TIER2_INTERNATIONAL_1 = auto()
    DISNEY_PLUS_TIER2_INTERNATIONAL_2 = auto()
    PARAMOUNT_PLUS_TIER2_INTERNATIONAL = auto()

    # Tier 3 Federated US
    CARTOON_NETWORK = auto()
    SCIENCE_CHANNEL = auto()

    # Tier 3 Federated International
    DISNEY_PLUS_TIER3_INTERNATIONAL = auto()
    CRUNCHYROLL = auto()

    # Canvases with infinite grid shelves
    RENT_FOR_99C_ROOM = auto()
    OUTRAGEOUS_COMEDIES_ROOM = auto()


class CollectionNames(Enum):
    APPLE_ORIGINALS = auto()
    OPAL_EPISODE_LOCKUP = auto()
    WATCH_LIVE_AMC = auto()
    SEARCH_BR_SHELF = auto()
    BROWSE_ON_SEARCH_LANDING = auto()
    OPAL_MARKER_SHELF = auto()
    OPAL_SHELF_SPORTS_CARD_LOCKUP = auto()
    OPAL_SHELF_CATEGORY_BRICK = auto()
    OPAL_SHELF_BRICK_HEADING_2 = auto()
    OPAL_SHELF_BRICK_HEADING_1 = auto()
    OPAL_SHELF_BRICK_FULLBLEED = auto()
    OPAL_SHELF_CHARTS = auto()
    OPAL_SHELF_BRICK = auto()
    OPAL_SHELF_BRICK_CONTENT_SETUP = auto()
    OPAL_SHELF_LOCKUP = auto()
    OPAL_SHELF_EPIC_INLINE = auto()
    OPAL_TRAILERS_LOCKUP = auto()
    OPAL_SHELF_SPORTS_EXTRAS_LOCKUP = auto()
    BONUS_ON_PRODUCT_PAGE = auto()
    BONUS_AND_TRAILERS_ENHANCED_LOCKUP = auto()
    OPAL_SHELF_NOTES_LOCKUP = auto()
    OPAL_SHELF_NOTES_LOCKUP_MIXED = auto()
    OPAL_SHELF_NOTES_LOCKUP_NO_DIRECT_PLAYBACK_ONLY = auto()
    OPAL_SHELF_TRAILER_LOCKUP = auto()
    OPAL_SHELF_EPIC_INLINE_FLAVOR_A = auto()
    OPAL_SHELF_EPIC_INLINE_FLAVOR_B = auto()
    OPAL_SHELF_EPIC_INLINE_FLAVOR_C = auto()
    OPAL_SHELF_EPIC_INLINE_FLAVOR_D = auto()
    OPAL_SHELF_EPIC_INLINE_FLAVOR_E = auto()
    OPAL_SHELF_EPIC_SHOWCASE_FLAVOR_A = auto()
    OPAL_SHELF_EPIC_SHOWCASE_FLAVOR_B = auto()
    OPAL_SHELF_EPIC_SHOWCASE_FLAVOR_C = auto()
    OPAL_SHELF_EPIC_SHOWCASE_FLAVOR_D = auto()
    OPAL_SHELF_EPIC_SHOWCASE_FLAVOR_E = auto()
    OPAL_SHELF_EPIC_SHOWCASE_FLAVOR_F = auto()
    OPAL_SHELF_UP_NEXT_LOCKUP = auto()
    RICH_HEADER_AND_EI_WRAPPER_MOVIES = auto()
    RICH_HEADER_AND_EI_WRAPPER_MLS = auto()
    SAMSUNG_CONTINUE_WATCHING = auto()
    SAMSUNG_CONTINUE_WATCHING_UNSIGNED = auto()
    RICH_HEADERS_CONTENT_ENTITY = auto()
    RICH_HEADERS_BRAND_ENTITY = auto()
    RICH_HEADERS_PERSON_ENTITY = auto()
    RICH_HEADERS_ROOM_ENTITY = auto()
    RICH_HEADERS_ROOT_ENTITY = auto()
    MLB_LEAGUE_SHELF = auto()
    CHARTS_MOVIES_WEEKLY = auto()
    MLS_LIVE_AND_UPCOMING_SCHEDULE = auto()
    MLB_VOD_SCHEDULE = auto()
    MLB_LIVE_SCHEDULE = auto()
    MLB_UPCOMING_SCHEDULE = auto()
    MLS_KEY_PLAYS = auto()
    MLS_INTERVIEWS = auto()
    MLS_NOTABLE_MOMENTS = auto()
    SHELF_WITH_PLAYLIST = auto()
    SHELF_TRAILERS_WITH_PLAYLIST = auto()
    WHAT_TO_WATCH_SHELF = auto()
    DISPLAY_TYPE_TEST = auto()
    MOVIE_BUNDLES_COLLECTION = auto()
    CATEGORY_BRICK_WITH_ITEMS_WITHOUT_OVERRIDEN_ART = auto()
    RIVER_SHELF = auto()
    MLS_TEAMS_ROW = auto()
    SPOTLIGHT_OFFER = auto()
    EPIC_SHOWCASE_OFFER = auto()
    EPIC_INLINE_OFFER = auto()
    CHANNEL_UPSELL_OFFER = auto()
    EPIC_STAGE_WITH_UPSELL = auto()
    EPIC_STAGE_WITH_BRAND_INTENTS = auto()
    EPIC_STAGE_HIDE_HERO_DESCRIPTION_FLAG_OFF = auto()
    EPIC_STAGE_HIDE_HERO_DESCRIPTION_FLAG_ON = auto()
    EPIC_STAGE_MAX_ITEM_VALUE_NOT_SET_10 = auto()
    EPIC_STAGE_MAX_ITEM_VALUE_NOT_SET_30 = auto()
    EPIC_STAGE_MAX_ITEM_VALUE_SET_30 = auto()
    EPIC_STAGE_MAX_ITEM_VALUE_SET_20 = auto()
    EPIC_STAGE_WITH_EXTRA_SHELF = auto()
    EPIC_STAGE_EXPLAINABILITY_LINE = auto()
    TV_PLUS_MOVIES_CHART = auto()
    TV_PLUS_GENRE_CHARTS = auto()
    COMING_SOON_ON_APPLE_TV = auto()
    EPIC_SHOWCASE_FLAVOR_F = auto()
    EPIC_SHOWCASE_SPORTS_FLAVOR_F = auto()
    NOTES_LOCKUP_TO_EPIC_SHOWCASE_FLAVOR_F = auto()
    NOTES_LOCKUP_TO_EPIC_SHOWCASE_FLAVOR_F_NOTESLOCKUP_DT = auto()
    EPIC_SHOWCASE_FLAVOR_E = auto()
    EPIC_SHOWCASE_FLAVOR_D = auto()
    EPIC_SHOWCASE_FLAVOR_C = auto()
    EPIC_SHOWCASE_FLAVOR_B = auto()
    EPIC_SHOWCASE_FLAVOR_A = auto()
    EPIC_SHOWCASE_WITH_VIDEO = auto()
    EPIC_INLINE_FLAVOR_E = auto()
    EPIC_INLINE_FLAVOR_D = auto()
    EPIC_INLINE_FLAVOR_C = auto()
    EPIC_INLINE_FLAVOR_B = auto()
    EPIC_INLINE_FLAVOR_A = auto()
    CHANNEL_UPSELL = auto()
    BRAND_LOCKUP = auto()
    SPOTLIGHT = auto()
    CATEGORY_BRICK = auto()
    NAV_BRICK_ART_AND_TEXT = auto()
    NAV_BRICK_ART_ONLY = auto()
    PERSON_LOCKUP = auto()
    SPORTS_MASTER_LOCKUP = auto()
    SPORTS_LOCKUP = auto()
    SEASON_LOCKUP = auto()
    EPISODE_LOCKUP = auto()
    GRID_LOCKUP = auto()
    RECOMMENDED = auto()
    UPSELL_OFFER = auto()
    EPIC_STAGE_WITH_NO_BRAND_ASSOCIATION = auto()
    EPIC_STAGE_WITH_NEW_ENTITIES = auto()
    EPIC_STAGE = auto()
    TV_PLUS_EPIC_STAGE = auto()
    NAV_BRICK = auto()
    MLS_SPOTLIGHT = auto()
    CHANNEL_LOCKUP = auto()
    BRICK = auto()
    NOTES_LOCKUP = auto()
    SPORTS_CARD_LOCKUP = auto()
    LOCKUP = auto()
    UP_NEXT_LOCKUP = auto()
    LOCKUP_WITH_SPORT_TEAMS = auto()
    LOCKUP_WITH_MOVIES_ONE = auto()
    LOCKUP_WITH_MOVIES_TWO = auto()
    EPICINLINE_WITH_SPORT_TEAMS = auto()
    BRICK_WITH_SPORT_TEAMS = auto()
    MLS_CHANNEL_UPSELL = auto()
    MLS_EPIC_STAGE = auto()
    MLS_EPIC_SHOWCASE_FLAVOR_E = auto()
    MLS_EPIC_INLINE_FLAVOR_E = auto()
    MLS_TODAY_SHELF = auto()
    CIP_MVPD_CHANNEL_UPSELL = auto()
    CIP_MVPD_EPIC_INLINE_FLAVOR_E = auto()
    CIP_MVPD_SPOTLIGHT = auto()
    CIP_MVPD_EPIC_STAGE = auto()
    SPORTS_EXTRAS_NOTES_LOCKUP = auto()
    SPORTS_EXTRAS_LOCKUP = auto()
    SPORTS_EXTRAS_EPIC_INLINE_A = auto()
    SPORTS_EXTRAS_EPIC_INLINE_B = auto()
    SPORTS_EXTRAS_EPIC_INLINE_C = auto()
    SPORTS_EXTRAS_EPIC_INLINE_D = auto()
    SPORTS_EXTRAS_EPIC_INLINE_E = auto()
    SHELF_PAGINATION = auto()
    SPORTS_EXTRAS_HAND_PICKED = auto()
    SPORTS_EXTRAS_QUERY_ONE = auto()
    SPORTS_EXTRAS_QUERY_TWO = auto()
    MLS_ARTWORK_AUTOMATION_EPIC_STAGE_UPCOMING_SPORTING_EVENTS = auto()
    MLS_ARTWORK_AUTOMATION_SPORTS_CARD_LOCKUP_UPCOMING_SPORTING_EVENTS = auto()
    MLS_ARTWORK_AUTOMATION_EPIC_STAGE_LIVE_SPORTING_EVENTS = auto()
    MLS_ARTWORK_AUTOMATION_SPORTS_CARD_LOCKUP_LIVE_SPORTING_EVENTS = auto()
    MLS_ARTWORK_AUTOMATION_EPIC_STAGE_VOD_SPORTING_EVENTS = auto()
    MLS_ARTWORK_AUTOMATION_SPORTS_CARD_LOCKUP_VOD_SPORTING_EVENTS = auto()
    TAHOMA_WATCH_NOW_UP_NEXT_FALLBACK = auto()
    PERSONALIZED_LIVE_SPORTS = auto()
    NO_TREATMENT_CONTROL = auto()
    CONTROL_AND_TREATMENT = auto()
    AREA1_TREATMENT = auto()
    AREA2_TREATMENT = auto()
    AREA1_CONTROL = auto()
    AREA2_CONTROL = auto()
    TV_PLUS_EPIC_SHOWCASE = auto()
    TV_PLUS_LOCKUP = auto()
    TV_PLUS_SPORTS_CARD_LOCKUP = auto()
    TV_PLUS_MASTER_LOCKUP = auto()
    TV_PLUS_EPIC_INLINE = auto()
    TV_PLUS_BRAND_CHART = auto()
    MCCORMICK_1_BRAND_CHART = auto()
    MCCORMICK_2_BRAND_CHART = auto()
    DOOR_LOCKUP = auto()
    MY_TV_DOOR_LOCKUP_WITH_SECTIONS = auto()
    CAMPAIGN_TV_PLUS_NON_EXPERIMENTAL = auto()
    CAMPAIGN_TV_PLUS_EXPERIMENTAL = auto()
    ROOM_BRICK_TAKEOVER = auto()
    CONTENT_SPOTLIGHT = auto()
    ROOM_SPOTLIGHT = auto()
    EXTERNAL_LINK_BRICK = auto()
    CONTENT_BRICK = auto()
    ROOM_BRICK = auto()
    FEDERATED_APPS_WATCHNOW = auto()
    CHARTS_BLENDED = auto()
    FREE_APPLE_TVPLUS_PREMIERES = auto()
    EDITORIAL_VIDEO_CLIP_SHELF = auto()
    LOCKUP_COLLECTION_WITH_BOX_SETS = auto()
    BRICK_COLLECTION_WITH_BOX_SETS = auto()
    GRID_COLLECTION_WITH_BOX_SETS = auto()
    NOTES_LOCKUP_COLLECTION_WITH_BOX_SETS = auto()
    EPIC_INLINE_A_COLLECTION_WITH_BOX_SETS = auto()
    EPIC_INLINE_B_COLLECTION_WITH_BOX_SETS = auto()
    EPIC_INLINE_C_COLLECTION_WITH_BOX_SETS = auto()
    EPIC_INLINE_D_COLLECTION_WITH_BOX_SETS = auto()
    EPIC_SHOWCASE_A_COLLECTION_WITH_BOX_SETS = auto()
    EPIC_SHOWCASE_B_COLLECTION_WITH_BOX_SETS = auto()
    EPIC_SHOWCASE_C_COLLECTION_WITH_BOX_SETS = auto()
    EPIC_SHOWCASE_D_COLLECTION_WITH_BOX_SETS = auto()
    EPIC_STAGE_COLLECTION_WITH_BOX_SETS = auto()
    WATCH_NOW_EPIC_STAGE = auto()
    TV_PLUS_EPIC_STAGE_WITH_UPSELL = auto()
    TV_PLUS_EPIC_STAGE_MULTI_QUERY_V1 = auto()
    TV_PLUS_EPIC_STAGE_MULTI_QUERY_V2 = auto()
    STORE_EPIC_STAGE = auto()
    MLS_EPIC_STAGE_WITH_UPSELL = auto()
    CHART_COLLECTION_WITH_BOX_SETS = auto()
    CONDUCTOR_TED_LASSO = auto()
    PAGINATED_GAME_SCHEDULE_LOCKUP_LEAGUE = auto()
    PAGINATED_GAME_SCHEDULE_LOCKUP_TEAM = auto()
    GAME_SCHEDULE_LOCKUP_PINNING = auto()
    LEAGUE_STANDINGS_SHELF_WITH_CONTEXT = auto()
    CHRONOS_POSTPLAY = auto()
    CHRONOS_POSTPLAY_2 = auto()
    CHRONOS_POSTPLAY_3 = auto()
    AVAILABLE_FOR_ES_LOCALE = auto()
    BLVR_MOVIES_SHOWS_SPORTING_EVENTS = auto()
    NOT_DROP_ENTITLED_CHANNELS_FLAG_ON = auto()
    NOT_DROP_ENTITLED_CHANNELS_FLAG_OFF = auto()
    PLAY_DEMOTION_SHOWS_CHRONOS_SCORE_MODIFIER_TARGET = auto()
    PLAY_DEMOTION_SHOWS = auto()
    PlAY_DEMOTION_MOVIES = auto()
    ENTITLED_TRENDING = auto()
    SHELF_FOR_VISION_PRO = auto()
    SHELF_WITH_SPORTING_EVENTS = auto()
    SHELF_EPIC_SHOWCASE_MIXED = auto()
    TRAILERS_SHELF = auto()
    MLS_TV_PLUS_EPIC_STAGE_SPORTS_RANKER = auto()
    CAPABILITY_FLAG_SHELF_ITEM_ART_SUPPORT = auto()
    CAPABILITY_FLAG_SHELF_ITEM_SUPPORT = auto()
    GROUP_FOR_YOU = auto()
    F1_MOVIE = auto()
    F1_TRAILERS = auto()

    # Additional Values - Adjusted from String Versions
    LARGE_SPORTS_EXTRAS = auto()
    EXTRAS_AND_NON_EXTRAS_TEAM = auto()
    DISTRIBUTED_EXTRAS = auto()
    TRAILERS_AND_PAID_BONUS = auto()
    PROMOTIONAL_EXTRAS = auto()
    MOVE_TO_EXPLORE_SHELF = auto()
    _3D = auto()
    IM = auto()
    _3D_IM = auto()
    MIXED = auto()

    PLATO_NOT_SUBSCRIBED_PEACOCK = auto()
    PLATO_SUBSCRIBED_PEACOCK = auto()


class ContentTypes(StrEnum):
    NOTABLE_MOMENT = 'NotableMoment'
    PROMOTIONAL = 'Promotional'
    BRAND = 'Brand'
    GENRE = 'Genre'
    EPISODE = 'Episode'
    MOVIE = 'Movie'
    EXTRA = 'Extra'
    BONUS = 'Bonus'
    KEY_PLAY = 'KeyPlay'
    PRESS_CONFERENCE = 'PressConference'
    INTERVIEW = "Interview"
    MOVIE_BUNDLE = 'MovieBundle'
    SEASON = 'Season'
    TV_SHOW = 'Show'
    LIVE_SERVICE = 'LiveService'
    SPORTING_EVENT = 'SportingEvent'
    SPORT = auto()
    LEAGUE = auto()
    TEAM = auto()
    PERSON = auto()
    COHORT_RULES = auto()
    COHORT = auto()
    CAMPAIGN = auto()
    OTHER = auto()
    EDITORIAL_VIDEO_CLIP = auto()
    BOXSET = 'Boxset'
    ROOM = 'Room'
    PREVIEW = 'Preview'


class CanvasTypes(Enum):
    # https://uts-api-docs.itunes.apple.com/uts-api/schema/CanvasType
    CHANNEL = auto()
    ROOM = auto()
    ROOT = auto()
    CANVAS = auto()
    TEAM = auto()
    GENRE = auto()
    PERSON = auto()
    SPORT = auto()


class DisplayTypes(StrEnum):
    CONTINUE_WATCHING = 'continueWatching'
    CHANNEL_UPSELL = 'channelUpsell'
    CHANNEL_EPG = 'channelEPG'
    EPIC_INLINE = 'epicInline'
    EPIC_INLINE_A = 'epicInlineA'
    EPIC_INLINE_B = 'epicInlineB'
    EPIC_INLINE_C = 'epicInlineC'
    EPIC_INLINE_D = 'epicInlineD'
    EPIC_INLINE_E = 'epicInlineE'
    EPIC_SHOWCASE = 'epicShowcase'
    EPIC_SHOWCASE_A = 'epicShowcaseA'
    EPIC_SHOWCASE_B = 'epicShowcaseB'
    EPIC_SHOWCASE_C = 'epicShowcaseC'
    EPIC_SHOWCASE_D = 'epicShowcaseD'
    EPIC_SHOWCASE_E = 'epicShowcaseE'
    EPIC_SHOWCASE_F = 'epicShowcaseF'
    SPOTLIGHT = 'spotlight'
    EPIC_STAGE = 'epicStage'
    LOCKUP = 'lockup'
    CHART = 'chart'
    CARD_LOCKUP = 'cardLockup'
    DOOR_LOCKUP = 'doorLockup'
    DOOR_LOCKUP_WITH_SECTIONS = 'doorLockupWithSections'
    SPORTS_CARD_LOCKUP = 'sportsCardLockup'
    SPORTS_MASTER_LOCKUP = 'sportsMasterLockup'
    BRICK = 'brick'
    NAV_BRICK = 'navBrick'
    SIDE_NAV = 'sideNav'
    ENHANCED_LOCKUP = 'enhancedLockup'
    TRAILER_LOCKUP = 'trailerLockup'
    GRID_LOCKUP = 'gridLockup'
    INFINITE_GRID = 'infiniteLockup'
    INFINITE_GRID_LOCKUP = 'gridLockup'
    EPISODE_LOCKUP = 'episodeLockup'
    SEASON_LOCKUP = 'seasonLockup'
    SPORTS_LOCKUP = 'sportsLockup'
    MASTER_LOCKUP = 'masterLockup'
    SPORTS_EXTRAS_LOCKUP = 'sportsExtrasLockup'
    NOTES_LOCKUP = 'notesLockup'
    PERSON_LOCKUP = 'personLockup'
    CHANNEL_LOCKUP = 'channelLockup'
    BRAND_LOCKUP = 'brandLockup'
    LIVE_SERVICE_LOCKUP = 'liveServiceLockup'
    BRICK_ROW_TAKEOVER = 'brick'
    NAV_BRICK_ART = 'navBrickArt'
    NAV_BRICK_ART_TEXT = 'navBrickArtText'
    CATEGORY_BRICK = 'categoryBrick'
    EPIC_STAGE_WITH_UPSELL = 'epicStageWithUpsell'
    UP_NEXT = 'upNext'
    TOP_SHELF = 'topShelf'
    UP_NEXT_LOCKUP = 'upNextLockup'
    PLAY_NEXT = 'playNext'
    PLAY_HISTORY = 'playHistory'
    TOP_SHELF_LOCKUP = 'topShelfLockup'
    POST_PLAY = 'postPlay'
    CONTENT_UPSELL = 'contentUpsell'
    CHANNEL_HEADER = 'channelHeader'
    FULL_SCREEN = 'fullScreen'
    CANVAS = 'canvas'
    TEAM_LOCKUP = 'teamLockup'
    TEAM_LOCKUP_WITH_SECTIONS = 'teamLockupWithSections'
    GAME_SCHEDULE_LOCKUP = 'gameScheduleLockup'
    LEAGUE_STANDINGS = 'leagueStandings'
    RIVER = 'river'
    RIBBON = 'ribbon'
    SWOOSH = 'swoosh'
    KEY_PLAY_LOCKUP = 'keyPlayLockup'
    WEB_LANDING = 'webLanding'
    ITUNES_EXTRAS = 'iTunesExtras'
    SHARED_CONTENT_LOCKUP = 'sharedContentLockup'
    FLAVORS = 'ABCDEF'

    def __str__(self) -> str:
        return self.value

    def get_display_without_flavor(self):
        if self.value[-1] in self.FLAVORS:
            return self.value[:-1]
        return self.value

    def get_flavor_from_display(self):
        if self.value[-1] in self.FLAVORS:
            return self.value[-1]
        return ''


class ShelfTypes(Enum):
    LOCKUP = auto()
    UP_NEXT = auto()
    POST_PLAY = auto()
    TOP_SHELF = auto()
    PLAY_NEXT = auto()
    UP_NEXT_TOP_SHELF = auto()
    TOP_SHELF_WIDGET = auto()


class ContentDatas(Enum):
    LEAGUES = auto()
    SPORTS = auto()
    AB_TESTING = auto()
    PERSONS = auto()
    CAMPAIGNS = auto()


class LeagueNames(Enum):
    MLS = auto()
    MLB = auto()
    NFL = auto()
    NHL = auto()
    NBA = auto()
    EPL = auto()
    CBK = auto()
    WCBK = auto()
    UCL = auto()
    BUND = auto()
    LIGA_MX = auto()
    LALIGA = auto()
    LEAGUE1 = auto()
    SERIEA = auto()
    UECL = auto()
    WNBA = auto()
    NWSL = auto()
    NCAAF = auto()
    NCAAB = auto()
    NCAAS = auto()
    NCAACWH = auto()
    NCAACWS = auto()
    NCAACMS = auto()
    CFL = auto()
    MLSNEXT = auto()
    MLSNEXTPRO = auto()
    LEAGUECUP = auto()
    CAMPEONES = auto()
    LEAGUESCUP = auto()
    USOC = auto()
    EUCHM = auto()
    COPA = auto()


class CompetitorNames(Enum):
    TEXAS = auto()
    ST_LOUIS = auto()
    SAN_DIEGO = auto()
    PITTSBURGH = auto()
    MINNESOTA = auto()
    MILWAUKEE = auto()
    KANSAS_CITY = auto()
    HOUSTON = auto()
    DETROIT = auto()
    COLORADO = auto()
    CLEVELAND = auto()
    CINCINNATI = auto()
    ARIZONA = auto()
    TORONTO = auto()
    SEATTLE_SOUNDERS_FC = auto()
    SEATTLE_MARINERS = auto()
    SAN_JOSE = auto()
    MIAMI = auto()
    ATLANTA = auto()
    GALAXY = auto()
    LAFC = auto()
    DC = auto()
    MONTREAL = auto()
    DALLAS = auto()
    NASHVILLE = auto()
    PORTLAND = auto()
    CHICAGO = auto()
    NEW_YORK = auto()
    ARSENAL = auto()


class SportNames(Enum):
    UNKNOWN = 0
    CHESS = auto()
    GYM = auto()
    SOCCER = auto()
    SOCCER_AS_SHOW = auto()
    BASEBALL = auto()


class PersonNames(Enum):
    # Cast and crew
    JIMMY_KIMMEL = auto()
    KIRSTEN_DUNST = auto()
    PETER_DINKLAGE = auto()
    TOM_HANKS = auto()
    STEVEN_SEAGAL = auto()
    JASON_BLUM = auto()
    BRAD_BIRD = auto()
    JAMES_CAMERON = auto()
    STEVE_ROGERS = auto()
    MICHELLE_YEOH = auto()
    ZAZIE_BEETZ = auto()
    RYAN_REYNOLDS = auto()
    JUNO_TEMPLE = auto()
    JASON_SUDEIKIS = auto()
    LUCY_LIU = auto()
    AVA_KOLKER = auto()
    RAPHAEL_PERSONNAZ = auto()
    DENNIS_HAYSBERT = auto()
    MARINA_PERSON = auto()
    ANSEL_ELGORT = auto()
    LADY_GAGA = auto()
    # Sports
    IAN_FRAY = auto()
    BARTOSZ_SLISZ = auto()
    LONDON_AGHEDO = auto()
    LIONEL_MESSI = auto()
    LUIS_SUAREZ = auto()
    JASON_MOMOA = auto()


class Offers(Enum):
    QA_AUTOMATION_OFFER_2 = auto()
    QA_AUTOMATION_OFFER_FOR_EXPERIMENTS = auto()
    QA_AUTOMATION_OFFER_FOR_HISTORY = auto()
    QA_AUTOMATION_OFFER_FOR_VERSION = auto()
    QA_AUTOMATION_OFFER_FOR_REPEATED_PUBLISH = auto()
    QA_AUTOMATION_OFFER_FOR_DUPLICATION = auto()
    QA_AUTOMATION_PUBLISHED_OFFER = auto()


class UTSOfferTypes(Enum):
    MLS_SEASON = auto()
    MLS_MONTHLY = auto()
    CHAPMAN_LEAGUE_PASS = auto()
    CHAPMAN_TEAM_PASS = auto()
    MVPD_GENERIC_WIRELESS_HARD_BUNDLE_BARCLAYS = auto()
    MVPD_GENERIC_WIRELESS_HARD_BUNDLE_TOTAL_PLAY = auto()
    MVPD_GENERIC_WIRELESS_HARD_BUNDLE_STREAM_PLUS = auto()
    MVPD_GENERIC_WIRELESS_HARD_BUNDLE_COMCAST = auto()
    CTUS_MVPD_ATV_CPAID = auto()
    CTUSXUMO_MVPD_ATV_CPAID = auto()
    BARCLAYSGB_FIN_MLS_HB = auto()
    CTUS_MVPD_MLS_CPAID_SEASON = auto()
    CTUS_MVPD_MLS_CPAID = auto()
    CTUSXUMO_MVPD_MLS_CPAID = auto()
    CTUSXUMO_MVPD_MLS_CPAID_SEASON = auto()
    MLS_MONTHLY_WITHOUT_TV_PLUS = auto()
    WEB_GENERIC_PLAN_3PTV = auto()
    HARDWARE_GENERIC_PLAN_3PTV = auto()
    WIRELESS_EXTENDED_TRIAL = auto()
    WIRELESS_HARD_BUNDLE = auto()
    ARISTOTLE_GENERIC = auto()
    REGULAR = auto()
    HARMONY = auto()
    FREE_TRIAL = auto()
    PLATO_REGULAR = auto()
    PLATO_UPGRADE = auto()
    CHAMELEON_INTRO = auto()
    CHAMELEON_WINBACK = auto()
    CHAPMAN_LEAGUE_MONTHLY = auto()
    CHAPMAN_LEAGUE_ANNUALLY = auto()
    CHAPMAN_LEAGUE_OOM_MONTHLY = auto()
    CHAPMAN_LEAGUE_OOM_ANNUALLY = auto()
    CHAPMAN_ASTROS_MONTHLY = auto()
    CHAPMAN_ASTROS_ANNUALLY = auto()
    CHAPMAN_RANGERS_MONTHLY = auto()
    CHAPMAN_RANGERS_ANNUALLY = auto()
    CHAPMAN_PADRES_MONTHLY = auto()
    CHAPMAN_PADRES_ANNUALLY = auto()

class OfferSeason(Enum):
    REGULAR = auto()  # MLS regular season typically starts in late February or early March and runs through
    # mid-October
    MONTHLY = auto()
    NONE = auto()

class ChapmanOfferTiers(StrEnum):
    # https://uts-admin-itms11.itunes.apple.com/app/entity/ingester/tvs.sbd.8000/relations
    LEAGUE_PASS = 'tvs.tir.8000'
    # ARIZONA_DIAMONDBACKS = 'tvs.tir.8001'
    # CINCINNATI_REDS = 'tvs.tir.8006'
    # CLEVELAND_GUARDIANS = 'tvs.tir.8007'
    # COLORADO_ROCKIES = 'tvs.tir.8008'
    # DETROIT_TIGERS = 'tvs.tir.8010'
    HOUSTON_ASTROS = 'tvs.tir.8011'
    # KANSAS_CITY_ROYALS = 'tvs.tir.8012'
    # MILWAUKEE_BREWERS = 'tvs.tir.8016'
    # MINNESOTA_TWINS = 'tvs.tir.8017'
    # PITTSBURGH_PIRATES = 'tvs.tir.8022'
    SAN_DIEGO_PADRES = 'tvs.tir.8023'
    # SEATTLE_MARINERS = 'tvs.tir.8024'
    # ST_LOUIS_CARDINALS = 'tvs.tir.8026'
    TEXAS_RANGERS = 'tvs.tir.8028'


class RoleTypes(StrEnum):
    PERSON = "persons"
    ACTOR = "actors"
    VOICE = "voice"
    DIRECTOR = "directors"
    WRITER = "writers"
    PRODUCER = "producers"
    GUESTSTAR = "gueststars"
    CHARACTER = "characters"
    CREATOR = "creators"
    MAKER = "makers"
    # todo: change CAST value after rdar://112533513 is solved
    CAST = "actors"


class CampaignNames(Enum):
    SPORTING_EVENT_BASKETBALL = auto()

