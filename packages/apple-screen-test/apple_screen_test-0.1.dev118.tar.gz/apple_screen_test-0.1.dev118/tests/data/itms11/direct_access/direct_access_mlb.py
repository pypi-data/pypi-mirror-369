# Zebra games https://quip-apple.com/phc1AgQRy0Yg#temp:C:HDF32bf3ed892e0415698d935dd1
from test_data_classes import SportingEvent, UPCOMING_SPORTING_EVENT, LIVE_SPORTING_EVENT, PAST_SPORTING_EVENT, \
    UMCContent, LIVE_SERVICE, STATIC_SPORTING_EVENT
from test_data_keys import CanvasNames
from test_data_classes import ContentTypes


mlb_upcoming_sporting_event = SportingEvent(
    name='Athletics at Phillies',
    league_name='MLB',
    id='umc.cse.8d4bofq747u3mdhhrdk4w6w6',
    type=UPCOMING_SPORTING_EVENT,
    required_entitlement=[CanvasNames.TV_PLUS],
)

mlb_live_sporting_event = SportingEvent(
    name='MLB Blue Jays at Mariners',
    league_name='MLB',
    id='umc.cse.4iyfxpv4iyavccjttkhrjb4jd',
    type=LIVE_SPORTING_EVENT
)

mlb_VOD_sporting_event = SportingEvent(
    name='MLB VOD FNB event',
    league_name='MLB',
    id='umc.cse.vw0qfy1aswa6d0a8sz7qdr86',
    type=PAST_SPORTING_EVENT,
    required_entitlement=[CanvasNames.TV_PLUS],
)

# Chapman Games https://quip-apple.com/JO1yATKJaUcN

chapman_upcoming_p_at_p = SportingEvent(
    name='Texas Rangers at Houston Astros',
    league_name='MLB',
    id='umc.cse.3azahsv1ia8bw19erm6jsrdpu',
    type=UPCOMING_SPORTING_EVENT
)

chapman_live_p_at_p = SportingEvent(
    name='Texas Rangers at Houston Astros',
    league_name='MLB',
    id='umc.cse.5xto9i109j0cuucw4srqkoho6',
    type=LIVE_SPORTING_EVENT
)

chapman_upcoming_np_at_p = SportingEvent(
    name='San Francisco Giants at San Diego Padres',
    league_name='MLB',
    id='umc.cse.57nvsa5yeps2wqi58posnf410',
    type=UPCOMING_SPORTING_EVENT
)

chapman_live_np_at_p = SportingEvent(
    name='San Francisco Giants at San Diego Padres',
    league_name='MLB',
    id='umc.cse.59pm4zh2sr26xi6zs1kv0farw',
    type=LIVE_SPORTING_EVENT
)

chapman_upcoming_np_at_np = SportingEvent(
    name='San Francisco Giants at New York Yankees',
    league_name='MLB',
    id='umc.cse.ln3vojkgkamlc14k0j8exax7',
    type=UPCOMING_SPORTING_EVENT
)

chapman_live_np_at_np = SportingEvent(
    name='San Francisco Giants at New York Yankees',
    league_name='MLB',
    id='umc.cse.3dl474abu5j09y9th97krr797',
    type=UPCOMING_SPORTING_EVENT
)

# game with Chapman and AppleTV+ availabilities
chapman_tv_plus_live_p_at_p = SportingEvent(
    name='Chapman Live Astros at Rangers participating at participating',
    league_name='MLB',
    id='umc.cse.6oc8l1w4jeskst9n7pwcnne4n',
    type=LIVE_SPORTING_EVENT
)
# Chapman VOD Games, frozen in 90min holdback window

p_vs_p__tx_rangers_at_sd_padres__vod_sporting_event = SportingEvent(
    id='umc.cse.4xfgcyzvvudq52ned9v9xjumd',
    name='Texas Rangers VS San Diego Padres',
    type=PAST_SPORTING_EVENT
)

p_vs_p__ho_astros_at_tx_rangers__embargo_sporting_event = SportingEvent(
    id='umc.cse.5cdg1ry6ake134vicjz1yfbf3',
    name='Houston Astros VS Texas Rangers',
    type=PAST_SPORTING_EVENT
)

p_vs_np__sd_padres_at_oakland_ath__embargo_sporting_event = SportingEvent(
    id='umc.cse.17n129lag71vhpwop34n8yq8',
    name='San Diego Padres VS Oakland Athletics',
    type=PAST_SPORTING_EVENT
)

np_vs_p__sf_giants_at_tx_rangers__embargo_sporting_event = SportingEvent(
    id='umc.cse.2ecr085s9n4os4niogp08nf4m',
    name='San Francisco Giants VS Texas Rangers',
    type=PAST_SPORTING_EVENT
)

np_vs_np__sf_giants_at_oakland_ath__embargo_sporting_event = SportingEvent(
    id='umc.cse.214rjbdit6e31d3z3s7ci4v9r',
    name='San Francisco Giants VS Oakland Athletics',
    type=PAST_SPORTING_EVENT
)

# Chapman VOD Games, after 90min holdback window

p_vs_np__ho_astros_at_ny_yankees__post_embargo_sporting_event = SportingEvent(
    id='umc.cse.35bzdrv5rx8tr9p2799asbxy7',
    name='Houston Astros VS New York Yankees',
    type=PAST_SPORTING_EVENT
)

np_vs_np__sf_giants_at_oakland_ath__post_embargo_sporting_event = SportingEvent(
    id='umc.cse.4qthsdfax0e4rs4oexowyy1fw',
    name='San Francisco Giants VS Oakland Athletics',
    type=PAST_SPORTING_EVENT
)

np_vs_np__oakland_as_at_sf_giants__post_embargo_sporting_event = SportingEvent(
    id='umc.cse.5wynzmpweb39am3c6a50l4c65',
    name='Oakland Athletics VS San Francisco Giants',
    type=PAST_SPORTING_EVENT
)  # missing PvsP

p_vs_p__tx_rangers_at_sd_padres__post_embargo_sporting_event = SportingEvent(
    id='umc.cse.4xfgcyzvvudq52ned9v9xjumd',
    name='Texas Rangers VS San Diego Padres',
    type=PAST_SPORTING_EVENT
)

chapman_live_np_at_np_athletics_at_giants = SportingEvent(
    id='umc.cse.2nh70sg5vwgsbipmrc2bk8eze',
    name='Oakland Athletics at San Francisco Giants',
    type=LIVE_SPORTING_EVENT
)

#

mlb_sporting_event = SportingEvent(
    id='umc.cse.ng138ier2w1d2jcemgg7tcqn',
    name='Pittsburgh Pirates at Milwaukee Brewers',
    type=STATIC_SPORTING_EVENT)

coming_soon_sporting_event = SportingEvent(
    id='umc.cse.8d4bofq747u3mdhhrdk4w6w6',
    league_name='MLB',
    name='Oakland Athletics at Philadelphia Phillies',
    type=LIVE_SPORTING_EVENT,
    description='Athletics at Phillies',
    required_entitlement=[CanvasNames.TV_PLUS],
)

live_service = UMCContent(
    id='tvs.lvs.24331847',
    name='MLB Linear Game 1 US Apple',
    type=LIVE_SERVICE
)

team_san_diego_padres = UMCContent(
    id='umc.cst.63df5l7qvspk1ulnsbkte43ln',
    name='San Diego Padres',
    type=ContentTypes.TEAM,
    adam_id_monthly="10788601654",
    adam_id_seasonal="10788601682"
)

team_houston_astros = UMCContent(
    id='umc.cst.3jdd8u3sm085xxagevgjgeehp',
    name='Houston Astros',
    type=ContentTypes.TEAM,
    adam_id_monthly="10788601647",
    adam_id_seasonal="10788601669"
)

team_texas_rangers = UMCContent(
    id='umc.cst.6d346uaal3ldt7z3oerfl71k8',
    name='Texas Rangers',
    type=ContentTypes.TEAM,
    adam_id_monthly="10788601661",
    adam_id_seasonal="10788601683"
)

team_oakland_athletics = UMCContent(
    id='umc.cst.3dds1ciz81ezzcpibzfvc64ti',
    name='Oakland Athletics',
    type=ContentTypes.TEAM
)

team_toronto_blue_jays = UMCContent(
    id='umc.cst.759rfvi2tf95aivbpxoj34l5n',
    name='Toronto Blue Jays',
    type=ContentTypes.TEAM
)

PARTICIPATING_TEAMS = [team_san_diego_padres, team_houston_astros, team_texas_rangers]
NON_PARTICIPATING_TEAMS = [team_oakland_athletics, team_toronto_blue_jays]
CHAPMAN_TEAMS = PARTICIPATING_TEAMS + NON_PARTICIPATING_TEAMS

live_sporting_event_on_federated_brand = SportingEvent(
    name='Marlins at Rays',
    league_name='MLB',
    id='umc.cse.1sha4nncu4t27hw4z6jfqy2ml',
    type=LIVE_SPORTING_EVENT,
    required_entitlement=[CanvasNames.ESPN],
)

live_sporting_event_on_federated_brand_2 = SportingEvent(
    name='Nationals at Diamondbacks',
    league_name='MLB',
    id='umc.cse.4txfoqolf1i14ejmlzp9l0kas',
    type=LIVE_SPORTING_EVENT,
    required_entitlement=[CanvasNames.ESPN],
)

chapman_federated_live_p_at_p = SportingEvent(
    name='San Diego Padres at Houston Astros',
    league_name='MLB',
    id='umc.cse.yteafiigy4zyq66lbzuf6aja',
    type=LIVE_SPORTING_EVENT,
    required_entitlement=[CanvasNames.MLB_TV],
)

mlb_live_sporting_event_with_opal_image = SportingEvent(
    name='',
    league_name='MLB',
    id='umc.cse.63joglk2n5y9nnici72gqxrgv',
    type=LIVE_SPORTING_EVENT
)

mlb_past_sporting_event_with_opal_image = SportingEvent(
    name='',
    league_name='MLB',
    id='umc.cse.bgbalpjsow1yosuesw39o5x1',
    type=PAST_SPORTING_EVENT
)

mlb_upcoming_sporting_event_with_opal_image = SportingEvent(
    name='',
    league_name='MLB',
    id='umc.cse.1vee5f519t43nl3blk95hma2y',
    type=UPCOMING_SPORTING_EVENT
)
