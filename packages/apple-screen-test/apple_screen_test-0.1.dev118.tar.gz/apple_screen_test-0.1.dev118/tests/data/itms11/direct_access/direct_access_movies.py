from test_data_classes import UMCContent, MOVIE
from test_data_keys import CanvasNames

# has items in post-play shelf
movie_tv_plus_the_elephant_queen = UMCContent(
    id='umc.cmc.1uagm4smdgondtxfbcqy5ssmn',
    name='The Elephant Queen',
    type=MOVIE,
    required_entitlement=[CanvasNames.TV_PLUS],
)

movie_hala = UMCContent(
    id='umc.cmc.50urrw5kgscwaukyucgeuhyeq',
    name='Hala',
    type=MOVIE,
    required_entitlement=[CanvasNames.TV_PLUS],
)

movie_licorice_pizza = UMCContent(
    id='umc.cmc.up1rt33i8x6cv83q9nk1tezz',
    name='Licorice Pizza',
    type=MOVIE)

movie_baby_driver = UMCContent(
    id='umc.cmc.57luwtyoqek8x64sqrnha3u17',
    name='Baby Driver',
    type=MOVIE,
    required_entitlement=[CanvasNames.ITUNES],
)

movie_zombieland = UMCContent(
    id='umc.cmc.6wwa6bx0gi4b53riq7a3wipeb',
    name='Zombieland',
    type=MOVIE,
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.AT_T_TV],
)

movie_avatar_the_way_of_water = UMCContent(
    id='umc.cmc.1hiz2ogc47mlt614gmuuiknij',
    name='Avatar: The Way of Water',
    type=MOVIE
)

movie_interstellar = UMCContent(
    id='umc.cmc.1vrwat5k1ucm5k42q97ioqyq3',
    name='Interstellar',
    type=MOVIE,
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.AT_T_TV, CanvasNames.PRIME_VIDEO],
)

movie_jivaro = UMCContent(
    id='umc.cmc.271sngsbvxv99t0y2hpyah51p',
    name='Jivaro',
    type=MOVIE,
    required_entitlement=[CanvasNames.ITUNES],
)

movie_top_gun = UMCContent(
    id='umc.cmc.1w0a2d5hpuxqksy2uvvhkrc42',
    name='Top Gun',
    type=MOVIE,
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.TUBI, CanvasNames.PRIME_VIDEO],
)

movie_mission_impossible_fallout = UMCContent(
    id='umc.cmc.3drwjm4wydrpzfnzloeytmh8j',
    name='Mission: Impossible Fallout',
    type=MOVIE,
    adam_id='1406515547',
    required_entitlement=[CanvasNames.TV_PLUS, CanvasNames.AT_T_TV, CanvasNames.PARAMOUNT_PLUS_MCCORMICK,
                          CanvasNames.PRIME_VIDEO, CanvasNames.ITUNES],
)

movie_skyfall = UMCContent(
    id='umc.cmc.1q3urmkb5n2c7hgwp4gcteg6l',
    name='Skyfall',
    type=MOVIE,
    required_entitlement=[CanvasNames.ITUNES],
)

ja_jp_movie = UMCContent(
    id='umc.cmc.5k04sjckkgo8qc38g9ngxcf5w',
    name='',
    type=MOVIE
)

invalid_content = UMCContent(
    id='umc.cmc.22y4k5ac9a76hh3rgayqt555',
    name='',
    type=MOVIE
)

movie_available_on_multiple_channels = UMCContent(
    id='umc.cmc.nqnk5m8namtg7htr812ap9w4',
    name='A Charlie Brown Valentine',
    type=MOVIE,
    required_entitlement=[CanvasNames.TV_PLUS, CanvasNames.PARAMOUNT_PLUS_MCCORMICK],
)

# Has timed-metadata
movie_luck = UMCContent(
    id='umc.cmc.4wca7m6rme5ij7l9nlxk0wjwc',
    name='Luck',
    type=MOVIE,
    required_entitlement=[CanvasNames.TV_PLUS],
)

# Has timed-metadata
movie_greyhound = UMCContent(
    id='umc.cmc.o5z5ztufuu3uv8lx7m0jcega',
    name='Greyhound',
    type=MOVIE,
    required_entitlement=[CanvasNames.TV_PLUS],
)

# Has timed-metadata
movie_palmer = UMCContent(
    id='umc.cmc.40qrv09i2yfh8iilyi4s8vfi',
    name='Palmer',
    type=MOVIE,
    required_entitlement=[CanvasNames.TV_PLUS],
)

# Has timed-metadata
movie_tetris = UMCContent(
    id='umc.cmc.4evmgcam356pzgxs2l7a18d7b',
    name='Tetris',
    type=MOVIE,
    required_entitlement=[CanvasNames.TV_PLUS],
)

# Has timed-metadata
movie_cherry = UMCContent(
    id='umc.cmc.30ynyyc68ab5bqyq2ilr9f445',
    name='Cherry',
    type=MOVIE,
    required_entitlement=[CanvasNames.TV_PLUS],
)

# Has timed-metadata
movie_spirited = UMCContent(
    id='umc.cmc.3lp7wqowerzdbej98tveildi3',
    name='Spirited',
    type=MOVIE,
    required_entitlement=[CanvasNames.TV_PLUS],
)

movie = UMCContent(
    adam_id='VELQN0560101',
    id='umc.cmc.1uagm4smdgondtxfbcqy5ssmn',
    name='The Elephant Queen',
    type=MOVIE,
    required_entitlement=[CanvasNames.TV_PLUS],
)

movie_2 = UMCContent(
    id='umc.cmc.o5z5ztufuu3uv8lx7m0jcega',
    name='Greyhound',
    type=MOVIE,
    required_entitlement=[CanvasNames.TV_PLUS],
)

licenced_movie = UMCContent(
    id='umc.cmc.3eh9r5iz32ggdm4ccvw5igiir',
    name='CODA',
    type=MOVIE
)

coming_soon_movie = UMCContent(
    id='umc.cmc.66asp1zbge3djo5tjekuljqwi',
    name='Coming Soon Movie - TV+',
    type=MOVIE,
    description='Adventures in Babysitting',
    required_entitlement=[CanvasNames.TV_PLUS],
)

movie_with_extra_content = UMCContent(
    id='umc.cmc.1wemr2mk1elmez5vrfn426rop',
    name='Napoleon',
    type=MOVIE
)

movie_on_itunes_and_tv_plus = UMCContent(
    id='umc.cmc.3drwjm4wydrpzfnzloeytmh8j',
    name='Mission: Impossible Fallout',
    type=MOVIE
)

postplay_movie = UMCContent(
    id='umc.cmc.4evmgcam356pzgxs2l7a18d7b',
    name='Tetris',
    type=MOVIE,
    related_content={
        'autoplay_content': "umc.cmc.hsmzusvkidbq0g135pwcfr4p"
    },
    required_entitlement=[CanvasNames.TV_PLUS],
)

stereoscopic_movie = UMCContent(
    id='umc.cmc.7iqafbwlvxf6ahtrnj4tb47i0',
    name='McLobo Mulan',
    type=MOVIE
)

stereoscopic_movie_two = UMCContent(
    id='umc.cmc.1zjh5zf7wgekks85tytaavakm',
    name='Encanto Jungle',
    type=MOVIE,
    required_entitlement=[CanvasNames.TV],
)

immersive_movie = UMCContent(
    id='umc.cmc.42u1ijo4o36a4rolf4ede95h0',
    name='Bellflower',
    type=MOVIE
)

immersive_movie_two = UMCContent(
    id='umc.cmc.4s9gbxfcmebd6dk7wgbp11xmk',
    name='Bright Short Control Content',
    type=MOVIE
)

movie_5 = UMCContent(
    id='umc.cmc.6vyttahzbdu475ju6ssx152m0',
    name='Loophole',
    type=MOVIE,
    adam_id='972055835',
    required_entitlement=[CanvasNames.ITUNES],
)

movie_purchased = UMCContent(
    id='umc.cmc.5dosobblga6wezo7ptyr8dte6',
    name='The Purple Gang',
    type=MOVIE,
    adam_id='956954663',
    required_entitlement=[CanvasNames.ITUNES],
)

movie_6 = UMCContent(
    id='umc.cmc.219lnb4s678o8roez3o905h7r',
    name='Iron Man',
    type=MOVIE,
    adam_id='688163154',
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.DISNEY_PLUS],
)

VOD_movie = UMCContent(
    id='umc.cmc.4z26yth0yvea6ifblym24nshi',
    name='Live to VOD Test',
    type=MOVIE,
    required_entitlement=[CanvasNames.TV_PLUS],
)

immersive = UMCContent(
    id='umc.cmc.4373g6fc8ok2m8eo51jb8ziiz',
    name='Avatar',
    type=MOVIE
)

threeD = UMCContent(
    id='umc.cmc.4a2ypxddplsdsahwxrc5fkz4x',
    name='Into the Spiderverse',
    type=MOVIE,
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.AT_T_TV],
)

movie_3 = UMCContent(
    id='umc.cmc.3r1vekw1q5380qojcz9t1ie6a',
    name='Inglourious Basterds',
    type=MOVIE,
    adam_id='1454826860',
    required_entitlement=[CanvasNames.AT_T_TV],
)

movie_4 = UMCContent(
    id='umc.cmc.5fb5o7xuop9wei1y3z0uoglfe',
    name='Abbott and Costello Meet Frankenstein',
    type=MOVIE,
    adam_id='729876650',
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.EVERGREEN_MCCORMICK],
)

localized_movie = UMCContent(
    id='umc.cmc.2pc6f6yflq949sz8uqconamat',
    name='Locke',
    type=MOVIE,
    adam_id='860902141',
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.HULU],
)

# Available in ES
unavailable_movie = UMCContent(
    id='umc.cmc.3jnt7q1lri0id6z9d16155fn9',
    name='',
    type=MOVIE
)

content_for_rating = UMCContent(
    id='umc.cmc.4e8pvt0eezl2rnq71x4nx3atn',
    name='',
    type=MOVIE,
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.PRIME_VIDEO],
)

content_for_exp_line = UMCContent(
    id='umc.cmc.1lgibcpelgvio0ksuv1txk1tl',
    name='Coda',
    type=MOVIE,
)

movie_exp_line_epic_stage = UMCContent(
    id='umc.cmc.50urrw5kgscwaukyucgeuhyeq',
    name='Hala',
    type=MOVIE,
)

movie_ei_exp_line_epic_stage = UMCContent(
    id='umc.cmc.1uagm4smdgondtxfbcqy5ssmn',
    name='The Elephant Queen',
    type=MOVIE,
)

immersive_movie_with_immersive_bonus = UMCContent(
    id='umc.cmc.4rdp3hb4ynv08vjy3hih5q0nj',
    name='IM Movie with IM Trailer',
    type=MOVIE,
)

two_d_movie_with_immersive_bonus = UMCContent(
    id='umc.cmc.azh1293xj8b97kizqza1qsqt',
    name='2D Movie with IM Bonus',
    type=MOVIE,
)

movie_with_adam_id = UMCContent(
    id='umc.cmc.4wfs3tno6kih50j21qgn1n0m3',
    name='Fury',
    type=MOVIE,
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.PRIME_VIDEO, CanvasNames.AT_T_TV],
    adam_id='922628991'
)
