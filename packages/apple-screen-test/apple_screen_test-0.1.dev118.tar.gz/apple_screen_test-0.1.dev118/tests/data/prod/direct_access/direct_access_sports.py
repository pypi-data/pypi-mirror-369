from test_data_classes import SportingEvent, UPCOMING_SPORTING_EVENT, LIVE_SPORTING_EVENT, PAST_SPORTING_EVENT, \
    UMCContent, LIVE_SERVICE, STATIC_SPORTING_EVENT, EXTRA
from test_data_keys import CanvasNames
from test_data_classes import ContentTypes

nba_live_sporting_event = SportingEvent(
    id='umc.cse.65u2cvyb9qyybu9w8o5jsj41c',
    league_name='NBA',
    name='NBA 76ers at Celtics',
    type=LIVE_SPORTING_EVENT
)

team_arsenal_fc = UMCContent(
    id='umc.cst.5gx97l2c8jun1ibioji2x3i0y',
    name='Arsenal F.C.',
    type=ContentTypes.TEAM
)

live_sporting_event = SportingEvent(
    id='',
    name='',
    type=LIVE_SPORTING_EVENT
)

# DYNAMIC TEST DATA

peacock_live_sporting_event = SportingEvent(
    name='Peacock Live Sporting Event',
    id='',
    type=LIVE_SPORTING_EVENT
)

peacock_upcoming_sporting_event = SportingEvent(
    name='Peacock Upcoming Sporting Event',
    id='',
    type=UPCOMING_SPORTING_EVENT
)

peacock_VOD_sporting_event = SportingEvent(
    name='Peacock VOD Sporting Event',
    id='',
    type=PAST_SPORTING_EVENT
)

nbc_live_sporting_event = SportingEvent(
    name='NBC Sports Live Sporting Event',
    id='',
    type=LIVE_SPORTING_EVENT
)

nbc_upcoming_sporting_event = SportingEvent(
    name='NBC Sports Upcoming Sporting Event',
    id='',
    type=UPCOMING_SPORTING_EVENT
)

nbc_VOD_sporting_event = SportingEvent(
    name='NBC Sports VOD Sporting Event',
    id='',
    type=PAST_SPORTING_EVENT
)

cbs_live_sporting_event = SportingEvent(
    name='CBS Sports Live Sporting Event',
    id='',
    type=LIVE_SPORTING_EVENT
)

cbs_upcoming_sporting_event = SportingEvent(
    name='CBS Sports Upcoming Sporting Event',
    id='',
    type=UPCOMING_SPORTING_EVENT
)

cbs_VOD_sporting_event = SportingEvent(
    name='CBS Sports VOD Sporting Event',
    id='',
    type=PAST_SPORTING_EVENT
)

mlb_at_bat_live_sporting_event = SportingEvent(
    name='MLB Sports Live Sporting Event',
    id='',
    type=LIVE_SPORTING_EVENT
)

mlb_at_bat_upcoming_sporting_event = SportingEvent(
    name='MLB Sports Upcoming Sporting Event',
    id='',
    type=UPCOMING_SPORTING_EVENT
)

mlb_at_bat_VOD_sporting_event = SportingEvent(
    name='MLB Sports VOD Sporting Event',
    id='',
    type=PAST_SPORTING_EVENT
)

# Taken from rdar://138102910
unavailable_sporting_event = SportingEvent(
    id='umc.cse.4ir7p57cq0i1xkchum654xpk',
    name='',
    type=PAST_SPORTING_EVENT
)

unavailable_test_sporting_event = SportingEvent(
    id='umc.cse.57rg1x6bc83twvryfgegrbp62',
    name='',
    type=PAST_SPORTING_EVENT
)

unavailable_test_sporting_event_2 = SportingEvent(
    id='umc.cse.4tjiuedg3bpum4plxthcia80m',
    name='',
    type=PAST_SPORTING_EVENT
)

unavailable_test_sporting_event_3 = SportingEvent(
    id='umc.cse.oedv58r4bbmretm67s8zu4nm',
    name='',
    type=PAST_SPORTING_EVENT
)
