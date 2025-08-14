from test_data_classes import UMCContent, MOVIE
from test_data_keys import CanvasNames

movie_tv_plus_seo_fields = UMCContent(
    name='Killers of the Flower Moon"',
    id='umc.cmc.5x1fg9vferlfeutzpq6rra1zf',
    type=MOVIE,
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.TV_PLUS],
)

# Multiple How To Watch options - including Paramount McCormick
movie_the_ring = UMCContent(
    name='The Ring',
    id='umc.cmc.2ksr5tpy9g97n8d3ohyqog9o5',
    type=MOVIE,
    required_entitlement=[CanvasNames.ITUNES],
)

# Multiple How To Watch options - including Paramount McCormick and Prime Video
movie_smile_2 = UMCContent(
    name='Smile 2',
    id='umc.cmc.20bo6udebibgaphdpv5jtvosm',
    type=MOVIE,
    required_entitlement=[CanvasNames.PRIME_VIDEO, CanvasNames.PHILO, CanvasNames.MGM_PLUS, CanvasNames.TV,
                          CanvasNames.ITUNES, CanvasNames.PARAMOUNT_PLUS_MCCORMICK,
                          CanvasNames.PARAMOUNT_PLUS_FEDERATED],
)

# Movie product page with videos
movie_with_videos = UMCContent(
    name='Napoleon',
    id='umc.cmc.25k80oxl3vo69c8rimk8v81s1',
    type=MOVIE,
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.TV_PLUS],
)

movie_cherry = UMCContent(
    id='umc.cmc.40gvwq6hnbilmnxuutvmejx4r',
    name='Invasion',
    type=MOVIE,
    required_entitlement=[CanvasNames.TV_PLUS],
)

movie_argylle = UMCContent(
    id='umc.cmc.3qy6j44hfqtekx6fx3yzh9w8i',
    name='Argylle',
    type=MOVIE,
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.TV_PLUS],
)

movie_f1 = UMCContent(
    id='umc.cmc.3t6dvnnr87zwd4wmvpdx5came',
    name='F1',
    type=MOVIE,
    required_entitlement=[CanvasNames.TV_PLUS],
)

movie_with_couple_languages = UMCContent(
    id='umc.cmc.4bjj3kj10p3h3pih1hi308rdc',
    name='Jurassic World Dominion',
    type=MOVIE,
    required_entitlement=[CanvasNames.PRIME_VIDEO, CanvasNames.PHILO, CanvasNames.STARZ_FEDERATED,
                          CanvasNames.STARZ_MCCORMICK, CanvasNames.SLING, CanvasNames.ITUNES, CanvasNames.HULU],
)

localized_movie = UMCContent(
    id='umc.cmc.7k0xi1816w2vnwana6bscutpq',
    name='',
    type=MOVIE,
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.PRIME_VIDEO],
)

movie_5 = UMCContent(
    id='umc.cmc.6vyttahzbdu475ju6ssx152m0',
    name='Loophole (1954)',
    type=MOVIE,
    adam_id='972055835',
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.TUBI],
)

movie_4 = UMCContent(
    id='umc.cmc.64i1q8ecdfgu2p6sqoh1u46z',
    name='22 Jump Street',
    type=MOVIE,
    required_entitlement=[CanvasNames.ITUNES],
)

movie_3 = UMCContent(
    id='umc.cmc.5zhbapthrtlgvyyq4a17eqxne',
    name='House of Gucci',
    type=MOVIE,
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.PLUTO_TV, CanvasNames.TUBI],
)

coming_soon_movie = UMCContent(
    id='',
    name='',
    type=MOVIE
)

movie = UMCContent(
    adam_id='VELQN0560101',
    id='umc.cmc.1ybrwww83rknjtwiuuemjfbvq',
    name='The Elephant Queen',
    type=MOVIE,
    required_entitlement=[CanvasNames.TV_PLUS],
)

licenced_movie = UMCContent(
    id='umc.cmc.3eh9r5iz32ggdm4ccvw5igiir',
    name='CODA',
    type=MOVIE,
    required_entitlement=[CanvasNames.TV_PLUS],
)

movie_2 = UMCContent(
    id='umc.cmc.o5z5ztufuu3uv8lx7m0jcega',
    name='Greyhound',
    type=MOVIE,
    required_entitlement=[CanvasNames.TV_PLUS],
)

movie_with_extra_content = UMCContent(
    id='umc.cmc.25k80oxl3vo69c8rimk8v81s1',
    name='Napoleon',
    type=MOVIE,
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.TV_PLUS],
)

ja_jp_movie = UMCContent(
    id='umc.cmc.5k04sjckkgo8qc38g9ngxcf5w',
    name='',
    type=MOVIE,
    required_entitlement=[CanvasNames.PEACOCK, CanvasNames.PRIME_VIDEO, CanvasNames.AMAZON_FREEVE, CanvasNames.TUBI],
)

invalid_content = UMCContent(
    id='umc.cmc.22y4k5ac9a76hh3rgayqt555',
    name='',
    type=MOVIE
)

# Available in ES
unavailable_movie = UMCContent(
    id='umc.cmc.3jnt7q1lri0id6z9d16155fn9',
    name='',
    type=MOVIE
)

content_for_rating = UMCContent(
    id='umc.cmc.26o403koqo2klixc0jtqy6tmc',
    name='',
    type=MOVIE,
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.PARAMOUNT_PLUS_MCCORMICK,
                          CanvasNames.PARAMOUNT_PLUS_FEDERATED, CanvasNames.PRIME_VIDEO],
)

movie_with_adam_id = UMCContent(
    id='umc.cmc.4wfs3tno6kih50j21qgn1n0m3',
    name='Fury',
    type=MOVIE,
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.PRIME_VIDEO, CanvasNames.AT_T_TV],
    adam_id='922628991'
)

postplay_movie = UMCContent(
    id='umc.cmc.4evmgcam356pzgxs2l7a18d7b',
    name='Tetris',
    type=MOVIE,
    required_entitlement=[CanvasNames.TV_PLUS],
)
