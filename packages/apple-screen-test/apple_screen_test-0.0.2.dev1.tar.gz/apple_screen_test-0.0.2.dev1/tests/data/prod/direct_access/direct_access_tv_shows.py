from test_data_classes import UMCContent, TV_SHOW, Collection
from test_data_keys import CanvasNames

# Contains custom SEO fields set in Gadget
show_tv_plus_seo_fields = UMCContent(
    name='Truth Be Told',
    id='umc.cmc.6hegr60w8pjyfcblgocjek7oo',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.TV_PLUS],
)

# Multiple How To Watch options - including Paramount McCormick
show_ncis = UMCContent(
    name='NCIS',
    id='umc.cmc.3en7wd5upm1hx2sdbbr949kbj',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.PLUTO_TV, CanvasNames.PRIME_VIDEO, CanvasNames.PHILO, CanvasNames.CBS,
                          CanvasNames.DISNEY_PLUS, CanvasNames.SLING, CanvasNames.ITUNES,
                          CanvasNames.PARAMOUNT_PLUS_MCCORMICK, CanvasNames.PARAMOUNT_PLUS_FEDERATED, CanvasNames.HULU],
)

tv_show_for_all_mankind_with_post_play_shelf = UMCContent(
    id='umc.cmc.6wsi780sz5tdbqcf11k76mkp7',
    name='For All Mankind',
    type=TV_SHOW,
    related_content={
        "ar_collection": Collection(collection_id='edt.col.602fe201-dfd8-4e60-a83f-e6c28d6fecb7'),
    },
    required_entitlement=[CanvasNames.TV_PLUS],
)

tv_show_invasion = UMCContent(
    id='umc.cmc.70b7z97fv7azfzn5baqnj88p6',
    name='Invasion',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.TV_PLUS],
)

episode_prehistoric_planet_s1_e1 = UMCContent(
    id='umc.cmc.41tkahibsri90mtz06dgmaus8',
    name='Coasts',
    type=TV_SHOW
)

show_black_bird = UMCContent(
    id='umc.cmc.30gx1y8nwthydkrvhqu156p3',
    name='Black Bird',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.TV_PLUS],
)

ja_jp_show = UMCContent(
    id='umc.cmc.6usfk47irau5q1nw85rnw2yg2',
    name='',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.PRIME_VIDEO, CanvasNames.DISNEY_PLUS, CanvasNames.CRUNCHYROLL, CanvasNames.ITUNES,
                          CanvasNames.HULU],
)

show = UMCContent(
    id='umc.cmc.vtoh0mn0xn7t3c643xqonfzy',
    name='Ted Lasso',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.TV_PLUS],
)

japan_exclusive_show = UMCContent(
    id='umc.cmc.2yfxy4qy52u9q615sqoat2egi',
    name='Classroom for heroes',
    type=TV_SHOW,
)

show_5 = UMCContent(
    id='umc.cmc.91mn0jm4nlkzuqoueg22v3b1',
    name='The Boys',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.PRIME_VIDEO, CanvasNames.AMAZON_FREEVE],
)

localized_show = UMCContent(
    id='umc.cmc.11b5q1lsbgj4y6vb2jn02no7y',
    name='',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.PRIME_VIDEO, CanvasNames.SLING, CanvasNames.ITUNES,
                          CanvasNames.MAX, CanvasNames.HULU],
)

show_2 = UMCContent(
    id='umc.cmc.3nogvl483m9gtmvtpslchnqus',
    name="RuPaul's Drag Race All Stars",
    type=TV_SHOW,
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.PARAMOUNT_PLUS_MCCORMICK,
                          CanvasNames.PARAMOUNT_PLUS_FEDERATED, CanvasNames.PRIME_VIDEO],
)

show_3 = UMCContent(
    id='umc.cmc.1wt1k4lyihd7dgqzbc74brlcv',
    name='Power',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.PRIME_VIDEO, CanvasNames.PHILO, CanvasNames.STARZ_FEDERATED,
                          CanvasNames.STARZ_MCCORMICK, CanvasNames.DISNEY_PLUS, CanvasNames.SLING,
                          CanvasNames.ITUNES, CanvasNames.HULU],
)

show_4 = UMCContent(
    id='umc.cmc.4f0v8wi48lo6achj9447h755z',
    name='Atlanta',
    type=TV_SHOW,
    adam_id='1141140966',
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.HULU, CanvasNames.DISNEY_PLUS],
)

flat_show = UMCContent(
    id='umc.cmc.1wp3e52ah4t1khqohadjagrei',
    name='The Daily Show With Trevor Noah',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.PRIME_VIDEO, CanvasNames.PHILO, CanvasNames.SLING,
                          CanvasNames.PARAMOUNT_PLUS_MCCORMICK, CanvasNames.PARAMOUNT_PLUS_FEDERATED, CanvasNames.HULU],
)

coming_soon_show = UMCContent(
    id='',
    name='',
    type=TV_SHOW
)

# Available for ES
unavailable_show = UMCContent(
    id='umc.cmc.6eumpdx74x6cq8a74tvaexuhw',
    name='Merli',
    type=TV_SHOW
)

flat_show_jp = UMCContent(
    id='umc.cmc.3kjb3qrxij01mq4hfmd2cgdfg',
    name='Flat show available in Japan store',
    type=TV_SHOW,
)

show_7 = UMCContent(
    id='umc.cmc.1wp3e52ah4t1khqohadjagrei',
    name='show_7',
    type=TV_SHOW,
)

show_8 = UMCContent(
    id='umc.cmc.4w5xyauweo3gtpzl008g1ct4i',
    name='Shakugan no Shana',
    type=TV_SHOW,
)

show_9 = UMCContent(
    id='umc.cmc.79ubela7qerosmxh9uyc0kcyk',
    name='show_9',
    type=TV_SHOW,
)

show_for_verify_advisories = UMCContent(
    id='umc.cmc.3yksgc857px0k0rqe5zd4jice',
    name='show_for_verify_advisories',
    type=TV_SHOW,
    required_entitlement=[CanvasNames.TV_PLUS],
)

show_with_box_set_item = UMCContent(
    id='umc.cmc.4dxfvjbc4rdww1dcp3kbgoaqm',
    name='Friends',
    type=TV_SHOW
)
