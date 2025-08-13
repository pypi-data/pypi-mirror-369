from data.itms11.direct_access.direct_access_mls import MLS_LEAGUE_NAME
from test_data_classes import SportingEvent, UPCOMING_SPORTING_EVENT, LIVE_SPORTING_EVENT, PAST_SPORTING_EVENT, \
    UMCContent, LIVE_SERVICE, STATIC_SPORTING_EVENT, EXTRA, TV_SHOW
from test_data_keys import CanvasNames
from test_data_classes import ContentTypes

# =======================================
#         LIVE SPORTING EVENTS
# =======================================


mls_360_live_games = SportingEvent(
    name='MLS 360 live game',
    league_name=MLS_LEAGUE_NAME,
    id='',
    type=LIVE_SPORTING_EVENT)

mls_live_sporting_event_free = SportingEvent(
    name='MLS Free Event',
    league_name=MLS_LEAGUE_NAME,
    id='',
    type=LIVE_SPORTING_EVENT)

mls_live_sporting_event_mls = SportingEvent(
    name='MLS Subscribed Event',
    league_name=MLS_LEAGUE_NAME,
    id='',
    type=LIVE_SPORTING_EVENT)

mls_live_to_VOD_sporting_event = SportingEvent(
    name='MLS Live to VOD Event',
    league_name=MLS_LEAGUE_NAME,
    id='',
    type=LIVE_SPORTING_EVENT)

mls_live_sporting_event_tv_plus = SportingEvent(
    name='MLS TV Plus Event',
    league_name=MLS_LEAGUE_NAME,
    id='',
    type=LIVE_SPORTING_EVENT)

mls_live_sporting_event_treat_as_show = SportingEvent(
    name='MLS live event with treatAsShow property',
    league_name=MLS_LEAGUE_NAME,
    id='',
    type=LIVE_SPORTING_EVENT)

# live_games = [
#     mls_360_live_games,
#     mls_live_sporting_event_free,
#     mls_live_sporting_event_mls,
#     mls_live_to_VOD_sporting_event,
#     mls_live_sporting_event_tv_plus
# ]

# =======================================
#         PAST SPORTING EVENTS
# =======================================

# Contains custom SEO fields set in Gadget
sporting_event_mls_seo_fields = SportingEvent(
    name='FC Cincinnati vs. Atlanta United',
    id='umc.cse.4j0m32z5m1li3zp0ezrlr1con',
    type=PAST_SPORTING_EVENT)

mls_VOD_sporting_event_tv_plus = SportingEvent(
    name='MLS TV Plus Event',
    id='umc.cse.58wdisuh2gbr0kore38p5hr6l',
    type=PAST_SPORTING_EVENT)

mls_VOD_campeones_cup_sporting_event_mls = SportingEvent(
    name='MLS LAFC vs Tigres',
    id='umc.cse.4b9y00y2ad0a25r8ug0czl78p',
    type=PAST_SPORTING_EVENT)

mls_sporting_event_with_sentiments = SportingEvent(
    name='MLS Sporting event with sentiments',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.4k4zosbtgyak20q7a3w50l253',
    type=PAST_SPORTING_EVENT)

mls_360_past_games = SportingEvent(
    name='MLS 360 past game',
    league_name=MLS_LEAGUE_NAME,
    id='',
    type=PAST_SPORTING_EVENT)

# sporting events without "Clubs" shelf vended
mls_VOD_sporting_event_nob_vs_mia = SportingEvent(
    id='umc.cse.5hejq9trd3rmvm9hpcrtgoaub',
    name=' MLS VOD NOP vs MIA',
    league_name=MLS_LEAGUE_NAME,
    type=PAST_SPORTING_EVENT)

mls_VOD_sporting_event_mia_vs_hil = SportingEvent(
    id='umc.cse.7k1y44exh9kcodoiq914jjo3',
    name=' MLS VOD MIA vs HIL',
    league_name=MLS_LEAGUE_NAME,
    type=PAST_SPORTING_EVENT)

mls_VOD_sporting_event_mia_vs_hks = SportingEvent(
    id='umc.cse.4rtsd65kxj368op1t9cwxa68n',
    name=' MLS VOD MIA vs HKS',
    league_name=MLS_LEAGUE_NAME,
    type=PAST_SPORTING_EVENT)

mls_VOD_sporting_event_free = SportingEvent(
    name='MLS Free Event',
    league_name=MLS_LEAGUE_NAME,
    id='',
    type=PAST_SPORTING_EVENT)

sports_extras_lockup_sporting_event_id = SportingEvent(
    name='MLS Event on Sports Extras Lockup Shelf',
    league_name=MLS_LEAGUE_NAME,
    id='',
    type=PAST_SPORTING_EVENT)

mls_VOD_sporting_event_mls = SportingEvent(
    name='MLS Mls Subscribed Event',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.5zq7qi415vil0ja0ugrrxlsv7',
    type=PAST_SPORTING_EVENT)

mls_VOD_sporting_event_treat_as_show = SportingEvent(
    name='MLS past event with treatAsShow property',
    league_name=MLS_LEAGUE_NAME,
    id='',
    type=PAST_SPORTING_EVENT)

# past_games = [
#     sporting_event_mls_seo_fields,
#     mls_VOD_sporting_event_tv_plus,
#     mls_VOD_campeones_cup_sporting_event_mls,
#     mls_sporting_event_with_sentiments,
#     mls_360_past_games,
#     mls_VOD_sporting_event_nob_vs_mia,
#     mls_VOD_sporting_event_mia_vs_hil,
#     mls_VOD_sporting_event_mia_vs_hks,
#     mls_VOD_sporting_event_free,
#     sports_extras_lockup_sporting_event_id,
#     mls_VOD_sporting_event_mls
# ]

# =======================================
#       UPCOMING SPORTING EVENTS
# =======================================

mls_360_upcoming_games = SportingEvent(
    name='MLS 360 upcoming game',
    league_name=MLS_LEAGUE_NAME,
    id='',
    type=UPCOMING_SPORTING_EVENT)

# Available for all signed-in users
mls_upcoming_sporting_event_free = SportingEvent(
    name='MLS Free Event',
    league_name=MLS_LEAGUE_NAME,
    id='',
    type=UPCOMING_SPORTING_EVENT)

# Available for tv plus and/or mls subscribed users
mls_upcoming_sporting_event_tv_plus = SportingEvent(
    name='MLS TV Plus Event',
    league_name=MLS_LEAGUE_NAME,
    id='',
    type=UPCOMING_SPORTING_EVENT)

# Available for mls subscribed users
mls_upcoming_sporting_event_mls = SportingEvent(
    name='MLS Mls Subscribed Event',
    league_name=MLS_LEAGUE_NAME,
    id='',
    type=UPCOMING_SPORTING_EVENT)

mls_upcoming_sporting_event_treat_as_show = SportingEvent(
    name='MLS upcoming event with treatAsShow property',
    league_name=MLS_LEAGUE_NAME,
    id='',
    type=UPCOMING_SPORTING_EVENT)

# upcoming_games = [
#     mls_360_upcoming_games,
#     mls_upcoming_sporting_event_free,
#     mls_upcoming_sporting_event_tv_plus,
#     mls_upcoming_sporting_event_mls
# ]

# =======================================
#                OTHERS
# =======================================

mls_tv_show = UMCContent(
    name='The Best of MLS',
    id='umc.cmc.5ltrhnwdtca180ll46pay6nwx',
    type=TV_SHOW)

mls_key_play_extra = UMCContent(
    name='MLS - Sports Extra - KeyPlay',
    id='umc.cmc.56vm8n0sckl8z13boei45vnst',
    type=EXTRA)

mls_recap_extra = UMCContent(
    name='MLS - Sports Extra - Bonus (Re-Cap)',
    id='umc.cmc.gqneitqaxgq69piwillnh097',
    type=EXTRA)

mls_interview_extra = UMCContent(
    name='MLS - Sports Extra - Interview',
    id='umc.cmc.2a5n20qimhgdebgy69p61s0ym',
    type=EXTRA)

mls_notable_moment_extra = UMCContent(
    name='MLS - Sports Extra - Notable Moment',
    id='umc.cmc.19pdjfcai38c80rr130w6eyb6',
    type=EXTRA)

mls_press_conference_extra = UMCContent(
    name='MLS - Sports Extra - Press Conference',
    id='umc.cmc.2pynli1q907ire3lkcl3hd02t',
    type=EXTRA)

epi_stage_key_play_extra = UMCContent(
    name='MLS - Sports Extra - KeyPlay',
    id='umc.cmc.1fxz9bs8kn76f7kzvkckmmt7y',
    related_content={
        'secondary_id': 'edt.item.65a83786-39dc-4803-8562-e1cafc166477'
    },
    type=EXTRA)

team_inter_miami = UMCContent(
    id='umc.cst.52peuzm5uh6ms5olnckn15i3p',
    name='Inter Miami',
    type=ContentTypes.TEAM)

team_seattle_sounders = UMCContent(
    id='umc.cst.3fsre50fs7bbhix862flzbaj4',
    name='Seattle Sounders',
    type=ContentTypes.TEAM)

team_atlanta_united = UMCContent(
    id='umc.cst.3ykg5vxse5z5ow87nssp6oojd',
    name='Atlanta United',
    type=ContentTypes.TEAM)

team_portland_timbers = UMCContent(
    id='umc.cst.36ae73uo2tfj8cb58iffcs1gc',
    name='Portland Timbers',
    type=ContentTypes.TEAM)
