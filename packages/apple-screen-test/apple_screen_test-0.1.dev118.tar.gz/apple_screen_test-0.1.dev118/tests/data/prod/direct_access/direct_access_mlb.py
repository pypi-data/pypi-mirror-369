from test_data_classes import SportingEvent, UPCOMING_SPORTING_EVENT, LIVE_SPORTING_EVENT, PAST_SPORTING_EVENT, \
    UMCContent, LIVE_SERVICE, STATIC_SPORTING_EVENT
from test_data_keys import CanvasNames
from test_data_classes import ContentTypes

mlb_VOD_sporting_event = SportingEvent(
    name='MLB VOD FNB event',
    league_name='MLB',
    id='umc.cse.18nkg5o290h6ctp249kglywdd',
    type=PAST_SPORTING_EVENT,
    required_entitlement=[CanvasNames.TV_PLUS],
)
