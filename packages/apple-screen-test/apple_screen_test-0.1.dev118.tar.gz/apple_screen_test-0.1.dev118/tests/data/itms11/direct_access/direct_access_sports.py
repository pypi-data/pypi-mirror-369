from test_data_classes import SportingEvent, UPCOMING_SPORTING_EVENT, LIVE_SPORTING_EVENT, PAST_SPORTING_EVENT, \
    UMCContent, LIVE_SERVICE, STATIC_SPORTING_EVENT, EXTRA
from test_data_keys import CanvasNames
from test_data_classes import ContentTypes


upcoming_sporting_event_2 = SportingEvent(
    id='umc.cse.1qmzr2rhzs267qs6czmj9xi0r',  # this event expires
    name='',
    type=LIVE_SPORTING_EVENT
)

live_sporting_event_2 = SportingEvent(
    id='umc.cse.2pcp03qppu15kxs1xeesluf4r',  # this event expires
    name='',
    type=LIVE_SPORTING_EVENT
)

nba_live_sporting_event = SportingEvent(
    name='NBA Denver at Chicago Bulls',
    league_name='NBA',
    id='umc.cse.29xk5lbypjrvdwc7bs2oz0obk',
    type=LIVE_SPORTING_EVENT
)

next_pro_league_sporting_event = SportingEvent(
    id='umc.cse.4pqj8kg2l1x2kxle3yndz301k',
    name='Next Pro League VOD Event',
    type=PAST_SPORTING_EVENT
)

team_arsenal_fc = UMCContent(
    id='umc.cst.5gx97l2c8jun1ibioji2x3i0y',
    name='Arsenal F.C.',
    type=ContentTypes.TEAM
)

upcoming_sporting_event = SportingEvent(
    id='umc.cse.sveptydyqtimx9si228ui8vq',
    name='',
    type=UPCOMING_SPORTING_EVENT
)

static_sporting_event = SportingEvent(
    id='umc.cse.64mtncayrv272ay668s5pst70',
    league_name='NBA',
    name='Milwaukee Bucks at Philadelphia 76ers',
    type=STATIC_SPORTING_EVENT
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

sports_extra_with_header_override_title = UMCContent(
    id='umc.cmc.2gviravxb9bl1pxwd7pnediss',
    name='B. Cremaschi, 8.6.23',
    type=EXTRA
)

live_sports_with_editorial_boost = UMCContent(
    id='umc.cse.3c1lrij4je4lzd7x7qnk3h63i',
    name='Montréal vs. Chicago',
    type=LIVE_SPORTING_EVENT
)

upcoming_sports_with_editorial_boost = UMCContent(
    id='umc.cse.279bg3pkdgtuat1pl185c9xfp',
    name='',
    type=UPCOMING_SPORTING_EVENT
)

nba_content_event = UMCContent(
    id='umc.cse.485qicxa1wor48k3ineryh53l',
    name='Miami Heat at Dallas Mavericks',
    type=ContentTypes.SPORTING_EVENT
)

game_with_no_availability = UMCContent(
    id='umc.cse.3cg7jpsjowdz9cz3hx9r500b5',
    name='San Jose Earthquakes vs. Toronto FC',
    type=ContentTypes.SPORTING_EVENT
)

sport_event_with_team_ranking_1 = UMCContent(
    id='umc.cse.15v6jt2shkfxxzcdx7y7qas8h',
    name='',
    type=LIVE_SPORTING_EVENT
)

sport_event_with_team_ranking_2 = UMCContent(
    id='umc.cse.4x1me2575ky59feug233bldj',
    name='',
    type=LIVE_SPORTING_EVENT
)

sport_event_with_team_ranking_3 = UMCContent(
    id='umc.cse.2vnc1wbpf81vgv1hp1n0577et',
    name='',
    type=LIVE_SPORTING_EVENT
)
