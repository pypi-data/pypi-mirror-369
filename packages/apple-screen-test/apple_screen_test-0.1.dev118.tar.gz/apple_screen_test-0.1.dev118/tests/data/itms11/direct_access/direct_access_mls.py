from test_data_classes import SportingEvent, UPCOMING_SPORTING_EVENT, LIVE_SPORTING_EVENT, PAST_SPORTING_EVENT, \
    UMCContent, LIVE_SERVICE, STATIC_SPORTING_EVENT, EXTRA
from test_data_keys import CanvasNames
from test_data_classes import ContentTypes


MLS_LEAGUE_NAME = "Major League Soccer"

mls_upcoming_sporting_event_free = SportingEvent(
    name='Free Event',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.cnfj625eujc8s00yx9xx3943',
    type=UPCOMING_SPORTING_EVENT)

mls_live_sporting_event_free = SportingEvent(
    name='MLS Free Event',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.5awj7v4upncvs0ubruik5p0ki',
    type=LIVE_SPORTING_EVENT)

mls_VOD_campeones_cup_sporting_event_mls = SportingEvent(
    name='MLS LAFC vs Tigres',
    id='umc.cse.4b9y00y2ad0a25r8ug0czl78p',
    type=PAST_SPORTING_EVENT)

mls_VOD_sporting_event_free = SportingEvent(
    name='MLS Free Event',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.7bhl1cywq3nv3l8b54p2njbae',
    type=PAST_SPORTING_EVENT)

# Available for tv plus and/or mls subscribed users
mls_upcoming_sporting_event_tv_plus = SportingEvent(
    name='MLS TV Plus Event',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.279bg3pkdgtuat1pl185c9xfp',
    type=UPCOMING_SPORTING_EVENT)

mls_live_sporting_event_tv_plus = SportingEvent(
    name='MLS TV Plus Event',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.534h0fsk4uzuq7rnyxtr3oath',
    type=LIVE_SPORTING_EVENT)

mls_immersive_live_sporting_event = SportingEvent(
    name='MLS TV Plus Event',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.58r7aqu4c0xm0dojavcs2r1g2',
    type=LIVE_SPORTING_EVENT,
    description='https://quip-apple.com/0gbNANAuQHwI')

mls_immersive_live_sporting_event_locales = SportingEvent(
    name='MLS TV Plus Event',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.25aawldo4v3bs8lvatb4ulwnv',
    type=LIVE_SPORTING_EVENT,
    description='https://quip-apple.com/0gbNANAuQHwI')

mls_VOD_sporting_event_tv_plus = SportingEvent(
    name='MLS TV Plus Event',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.1y8e7ga2a9575j5dr4b97ndqe',
    type=PAST_SPORTING_EVENT)

# Available for mls subscribed users
mls_upcoming_sporting_event_mls = SportingEvent(
    name='MLS Subscribed Event',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.5n1h2huuoqa0mv8opf55gwwrs',
    type=UPCOMING_SPORTING_EVENT)

mls_upcoming_sporting_event_mls_2 = SportingEvent(
    name='MLS Subscribed Event',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.25aawldo4v3bs8lvatb4ulwnv',
    type=UPCOMING_SPORTING_EVENT)

mls_live_sporting_event_mls = SportingEvent(
    name='MLS Subscribed Event',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.2jsisftio8ftzu01go11m12it',
    type=LIVE_SPORTING_EVENT)

mls_live_sporting_event_mls_2 = SportingEvent(
    name='MLS Subscribed Event 2',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.6c4c8p87pk52r9aag3d14lfdf',
    type=LIVE_SPORTING_EVENT)

mls_live_sporting_event_mls_3 = SportingEvent(
    name='MLS Subscribed Event 3',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.3qppnbvs8den1lxpncl43ngnk',
    type=LIVE_SPORTING_EVENT)

mls_live_sporting_event_with_key_plays_mls = SportingEvent(
    name='MLS Subscribed Event with key plays',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.4bqgz1vyuaf1vf4shbepanmfu',
    type=LIVE_SPORTING_EVENT)

mls_VOD_sporting_event_mls = SportingEvent(
    name='MLS Subscribed Event',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.52pnfe17tgz6qurfg2k5k8ne7',
    type=PAST_SPORTING_EVENT)

mls_VOD_sporting_event_mls_2 = SportingEvent(
    name='MLS Subscribed Event 2',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.30ic5lnmms0iaxhmla76xoawa',
    type=PAST_SPORTING_EVENT)

mls_VOD_no_artwork_automation_sporting_event = SportingEvent(
    name='MLS No Artwork Automation Event',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.3k06h9ak01dke5bahsvorj5l',
    type=PAST_SPORTING_EVENT)

mls_sporting_event = SportingEvent(
    id='umc.cse.7bhl1cywq3nv3l8b54p2njbae',
    name='MLS Free Event',
    type=STATIC_SPORTING_EVENT)

mls_live_sporting_event_free_2 = SportingEvent(
    name='MLS Free Event',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.6nrcjhls5fuxgshig6ueqt0yk',
    type=LIVE_SPORTING_EVENT)

mls_live_sporting_event_free_home_away_streams = SportingEvent(
    name='MLS Free Event',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.6nrcjhls5fuxgshig6ueqt0yk',
    type=LIVE_SPORTING_EVENT)

# This is old event doesn't vend clock-score
mls_live_sporting_event_tv_plus_2 = SportingEvent(
    name='MLS TV Plus Event',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.3cg7jpsjowdz9cz3hx9r500b5',
    type=LIVE_SPORTING_EVENT)

mls_VOD_sporting_event_tv_plus_2 = SportingEvent(
    name='MLS TV Plus Event',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.3k06h9ak01dke5bahsvorj5l',
    type=PAST_SPORTING_EVENT)

mls_live_sporting_event_mls_4 = SportingEvent(
    name='MLS Mls Subscribed Event 4',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.2yc9fl62zx3iljvadzfp17blk',
    type=LIVE_SPORTING_EVENT)

mls_VOD_sporting_event_mls_3 = SportingEvent(
    name='MLS Mls Subscribed Event 3',
    id='umc.cse.6fu4cgpis6dhxgmw25fd47bfm',
    type=PAST_SPORTING_EVENT)

sports_extras_lockup_sporting_event = SportingEvent(
    name='MLS Event on Sports Extras Lockup Shelf',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.6fu4cgpis6dhxgmw25fd47bfm',
    type=PAST_SPORTING_EVENT)

mls_live_to_VOD_sporting_event = SportingEvent(
    name='MLS Live to VOD Event',
    league_name=MLS_LEAGUE_NAME,
    id='',
    type=LIVE_SPORTING_EVENT)

mls_playable_sporting_event = SportingEvent(
    name='Los Angeles FC vs. Philadelphia Union',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.23icyftsk2g4qaphqngvyrhg7',
    adam_id='2489849',
    type=LIVE_SPORTING_EVENT)

live_sporting_event = SportingEvent(
    id='umc.cse.2gk5p7ms93odjd8k2xrmnv96q',
    league_name=MLS_LEAGUE_NAME,
    name='Real Salt Lake vs. Sporting Kansas City',
    type=LIVE_SPORTING_EVENT)

mls_key_play_extra = UMCContent(
    name='MLS - Sports Extra - KeyPlay',
    id='umc.cmc.6x6fgdca3ia123qwcmuiang12',
    type=EXTRA)

epi_stage_key_play_extra = UMCContent(
    name='MLS - Sports Extra - KeyPlay',
    id='umc.cmc.1fxz9bs8kn76f7kzvkckmmt7y',
    related_content={
        'secondary_id': 'edt.item.65a83786-39dc-4803-8562-e1cafc166477'
    },
    type=EXTRA)

team_seattle_sounders_fc = UMCContent(
    id='umc.cst.3fsre50fs7bbhix862flzbaj4',
    name='Seattle Sounders FC',
    type=ContentTypes.TEAM)

team_dallas = UMCContent(
    id='umc.cst.5o0zsc41gl10rvafh3anhqicp',
    name='Dallas',
    type=ContentTypes.TEAM,
    required_entitlement=[CanvasNames.MLS],
)

mls_VOD_sporting_event_mls_4 = SportingEvent(
    name='MLS Subscribed Event 2',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.5awj7v4upncvs0ubruik5p0ki',
    type=PAST_SPORTING_EVENT)

mls_upcoming_sporting_event_mls_3 = SportingEvent(
    name='MLS Subscribed Event',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.572v5ik6u8emqpifz8nrwkqd1',
    type=UPCOMING_SPORTING_EVENT)

# Event with immersive playables only, playback available on vision only
mls_live_sporting_event_imm_pl = SportingEvent(
    name='Inter Miami CF vs. Atlanta United',
    league_name='Major League Soccer',
    id='umc.cse.58r7aqu4c0xm0dojavcs2r1g2',
    type=LIVE_SPORTING_EVENT,
    required_entitlement=[CanvasNames.TV_PLUS, CanvasNames.MLS],
)

# Event with both immersive and 2d playables payback available on all devices
mls_live_sporting_event_imm_2d_pl = SportingEvent(
    name='Seattle Sounders FC vs. San Jose Earthquakes',
    league_name='Major League Soccer',
    id='umc.cse.25aawldo4v3bs8lvatb4ulwnv',
    type=LIVE_SPORTING_EVENT,
    required_entitlement=[CanvasNames.MLS],
)

mls_VOD_sporting_event_mtl_vs_dal_tv_plus = SportingEvent(
    name='MTL vs. DAL sporting event available on both MLS and TV+',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.1duhao4b4awt19k2jw1kgv6v3',
    type=PAST_SPORTING_EVENT)

mls_live_sporting_event_sj_vs_tor_tv_plus = SportingEvent(
    name='SJ vs. TOR sporting event available on both MLS and TV+',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.279bg3pkdgtuat1pl185c9xfp',
    type=LIVE_SPORTING_EVENT)

mls_upcoming_sporting_event_mtl_vs_por_tv_plus = SportingEvent(
    name='MTL vs. POR sporting event available on both MLS and TV+',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.2vuvr74hgg81igf2afx45af33',
    type=UPCOMING_SPORTING_EVENT)

mls_live_sporting_event_tx_vs_hst = SportingEvent(
    name='Texas Rangers at Houston Astros',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.1zfjahj65bfer9h350yo04pc4',
    type=LIVE_SPORTING_EVENT
)

mls_upcoming_sporting_event_with_opal_image = SportingEvent(
    name='',
    league_name='MLB',
    id='umc.cse.5890e52rq5eotzf9r0jt1n9r7',
    type=UPCOMING_SPORTING_EVENT
)

mls_past_sporting_event_with_opal_image = SportingEvent(
    name='',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.2qnyi34eedt41bzrv197e04lg',
    type=PAST_SPORTING_EVENT
)

mls_live_sporting_event_with_opal_image = SportingEvent(
    name='',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.mz3s95mwjk4h3tvqnk69zhj0',
    type=LIVE_SPORTING_EVENT
)

mls_ei_upcoming_sporting_event_exp_line_epic_stage = SportingEvent(
    name='',
    league_name=MLS_LEAGUE_NAME,
    id='edt.item.681b8e29-7ef2-45f0-aa84-1be3486f63e3',
    type=UPCOMING_SPORTING_EVENT
)

mls_upcoming_sporting_event_exp_line_epic_stage = SportingEvent(
    name='',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.2yc9fl62zx3iljvadzfp17blk',
    type=UPCOMING_SPORTING_EVENT
)

mls_live_sporting_event_exp_line_epic_stage = SportingEvent(
    name='',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.279bg3pkdgtuat1pl185c9xfp',
    type=LIVE_SPORTING_EVENT
)

mls_ei_live_sporting_event_exp_line_epic_stage = SportingEvent(
    name='',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.2jsisftio8ftzu01go11m12it',
    type=LIVE_SPORTING_EVENT
)

mls_vod_sporting_event_exp_line_epic_stage = SportingEvent(
    name='',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.52pnfe17tgz6qurfg2k5k8ne7',
    type=PAST_SPORTING_EVENT
)

mls_ei_vod_sporting_event_exp_line_epic_stage = SportingEvent(
    name='',
    league_name=MLS_LEAGUE_NAME,
    id='umc.cse.19h4c05g2w4tdh0xdh8hwg057',
    type=PAST_SPORTING_EVENT
)
