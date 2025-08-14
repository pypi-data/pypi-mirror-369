from test_data_classes import UMCContent, TV_SHOW
from test_data_keys import CanvasNames

show_tv_plus_ted_lasso = UMCContent(
    id='umc.cmc.vtoh0mn0xn7t3c643xqonfzy',
    name='Ted Lasso',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.TV_PLUS],
)

show_the_office = UMCContent(
    id='umc.cmc.455js879szmdywutf3qjewagm',
    name='The Office',
    type=TV_SHOW)

show_see = UMCContent(
    id='umc.cmc.3s4mgg2y7h95fks9gnc4pw13m',
    name='SEE',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.TV_PLUS],
)

show_hijack = UMCContent(
    id='umc.cmc.1dg08zn0g3zx52hs8npoj5qe3',
    name='Hijack',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.TV_PLUS],
)

show_with_multiple_box_sets_diff_release_dates = UMCContent(
    id='umc.cmc.7htjb4sh74ynzxavta5boxuzq',
    name='Game of Thrones',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.AT_T_TV, CanvasNames.HBO_GO, CanvasNames.HULU, CanvasNames.PRIME_VIDEO,
                          CanvasNames.ITUNES],
)

show_with_multiple_box_sets_and_same_release_dates = UMCContent(
    id='umc.cmc.224vt3dmosi0331a2yc8ny3l8',
    name='Lost',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.ITUNES],
)

show_morning_show = UMCContent(
    id='umc.cmc.4967ders5yx2f7prkpxmoh0kb',
    name='The Morning Show',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.TV_PLUS],
)

show_black_bird = UMCContent(
    id='umc.cmc.5lhufd6jak39jkne94k2hxo2o',
    name='Black Bird',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.TV_PLUS],
)

ja_jp_show = UMCContent(
    id='umc.cmc.6usfk47irau5q1nw85rnw2yg2',
    name='',
    type=TV_SHOW
)

# content setup for NP play upgrade testing, setup: https://quip-apple.com/QF06AAZqh5mz
# show Central Park Show and movie A Charlie Brown Valentine are available on TV+, Paromount+ and Evergreen
show_available_on_multiple_channels = UMCContent(
    id='umc.cmc.4qe3i11erof30x0vz8nwnjkw3',
    name='Central Park Show',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.TV_PLUS, CanvasNames.PARAMOUNT_PLUS_MCCORMICK, CanvasNames.EVERGREEN_MCCORMICK],
)

show = UMCContent(
    id='umc.cmc.vtoh0mn0xn7t3c643xqonfzy',
    name='Ted Lasso',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.TV_PLUS],
)

coming_soon_show = UMCContent(
    id='umc.cmc.15riw0api0xqne1c7xx0p28ra',
    name='Coming Soon Show - TV+',
    type=TV_SHOW,
    description='ALF',
    required_entitlement=[CanvasNames.TV_PLUS],
)

show_coming_soon_episodes = UMCContent(
    id='umc.cmc.7d9yulmth1rvkwpij477qsqsk',
    name='Big Beasts',
    type=TV_SHOW,
)

show_5 = UMCContent(
    id='umc.cmc.pipey73n3wfe96uwbg7eunec',
    name='Star Wars: The Clone Wars',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.DISNEY_PLUS, CanvasNames.NETFLIX],
)

FAM_show = UMCContent(
    id='umc.cmc.1802pn6jlq2mz70gj7mezrfg9',
    name='For All Mankind',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.TV_PLUS],
)

truth_be_told_show = UMCContent(
    id='umc.cmc.6hegr60w8pjyfcblgocjek7oo',
    name='Truth Be Told',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.TV_PLUS],
)

flat_show = UMCContent(
    id='umc.cmc.1wp3e52ah4t1khqohadjagrei',
    name='The Daily Show With Trevor Noah',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.COMEDY_CENTRAL, CanvasNames.PRIME_VIDEO],
)

graves_show = UMCContent(
    id='umc.cmc.6q8ncg5fahjoh17himtlpemmk',
    name='Graves',
    type=TV_SHOW
)

immersive_tv_show = UMCContent(
    id='umc.cmc.21ppbxq70l6ifn2fc2e0wbyr',
    name='Test Show 1',
    type=TV_SHOW
)

show_2 = UMCContent(
    id='umc.cmc.699yz0ndcm42cxcwcbzkb6dng',
    name='Shameless',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.SHOWTIME_MCCORMICK, CanvasNames.PRIME_VIDEO],
)

show_3 = UMCContent(
    id='umc.cmc.7wi0fpx37shx0bfxau56ufps',
    name='Seinfeld',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.EVERGREEN_MCCORMICK],
)

show_4 = UMCContent(
    id='umc.cmc.4f0v8wi48lo6achj9447h755z',
    name='Atlanta',
    type=TV_SHOW,
    adam_id='1141140966',
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.HULU],
)

show_purchased = UMCContent(
    id='umc.cmc.25ny5ggwpzivvhs7otnx9r11r',
    name='The Good Fight',
    type=TV_SHOW,
    adam_id='1205699733',
    required_entitlement=[CanvasNames.PARAMOUNT_PLUS_MCCORMICK, CanvasNames.ITUNES, CanvasNames.PRIME_VIDEO],
)

localized_show = UMCContent(
    id='umc.cmc.11b5q1lsbgj4y6vb2jn02no7y',
    name='The Pacific',
    type=TV_SHOW,
    adam_id='474233495',
    required_entitlement=[CanvasNames.AT_T_TV, CanvasNames.HBO_GO, CanvasNames.HULU, CanvasNames.PRIME_VIDEO,
                          CanvasNames.ITUNES],
)

show_6 = UMCContent(
    id='umc.cmc.91mn0jm4nlkzuqoueg22v3b1',
    name='The Boys',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.PRIME_VIDEO],
)

show_with_box_set_item = UMCContent(
    id='umc.cmc.4dxfvjbc4rdww1dcp3kbgoaqm',
    name='Friends',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.TBS, CanvasNames.HBO_GO, CanvasNames.AT_T_TV, CanvasNames.PRIME_VIDEO],
)

# Available for ES
unavailable_show = UMCContent(
    id='umc.cmc.6eumpdx74x6cq8a74tvaexuhw',
    name='Merli',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.NETFLIX],
)

show_exp_line_epic_stage = UMCContent(
    id='umc.cmc.17vf6g68dy89kk1l1nnb6min4',
    name='Pachinko',
    type=TV_SHOW,
)

show_ei_exp_line_epic_stage = UMCContent(
    id='umc.cmc.6vwg3ce7ovsexa3a6r7f6qk49',
    name='Palm Royale',
    type=TV_SHOW,
)

peacock_brand_sample_show = UMCContent(
    id='umc.cmc.75vrenzo84ph9r4982razf9lh',
    name='Ryan Wedding',
    type=TV_SHOW,
)
