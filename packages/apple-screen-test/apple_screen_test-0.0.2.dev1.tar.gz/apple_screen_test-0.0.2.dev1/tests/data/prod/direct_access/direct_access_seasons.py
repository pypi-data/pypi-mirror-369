from test_data_classes import Season, SEASON

season = Season(
    id='umc.cmc.1zpr41pbvs0v8u24i4m1dt1vk',
    name='Season 1',
    type=SEASON,
    description='Ted Lasso S01',
    show_id='umc.cmc.vtoh0mn0xn7t3c643xqonfzy'
)

season_4 = Season(
    id='umc.cmc.5vh0dzpwy158ktoh4wrl4urht',
    name='Season 7',
    type=SEASON,
    adam_id='1153873479',
    description='Blue Bloods',
    show_id='umc.cmc.84g6qbryan15hhgtkq4o82r0'
)

# Available for ES
unavailable_season = Season(
    id='umc.cmc.3mrfam2zsw2d0pcnu7enm1gug',
    name='Season 1',
    type=SEASON,
    description='Merli S01',
    show_id='umc.cmc.6eumpdx74x6cq8a74tvaexuhw'
)

season_for_title = Season(
    id='umc.cmc.20rpdmxcmxb36cit7m82d0dqd',
    name='season_for_title',
    type=SEASON,
)
