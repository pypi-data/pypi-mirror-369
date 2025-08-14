
from test_data_classes import UMCContent, MOVIE_BUNDLE, BOX_SET, EXTRA, BoxSet
from test_data_keys import ContentTypes

purchased_itunes_interstellar = UMCContent(
    id='uts.cortrle.2DFC98A92A524D5A84D41E9030076A63',
    name='Interstellar',
    type=ContentTypes.COHORT_RULES)

purchased_itunes_inception = UMCContent(
    id='uts.cortrle.8F1CA4F5AA4DC3261127D6998BF2E893',
    name='Inception',
    type=ContentTypes.COHORT_RULES)

purchased_itunes_batman = UMCContent(
    id='uts.cortrle.000704D32E1E58EE6A18DD845EA52590',
    name='Batman',
    type=ContentTypes.COHORT_RULES)

purchased_itunes_prestige = UMCContent(
    id='uts.cortrle.0F8407D9EFCB09F6312E13CE64673A03',
    name='Prestige',
    type=ContentTypes.COHORT_RULES)

purchased_itunes_dunkirk = UMCContent(
    id='uts.cortrle.2F70CEC66FE826F5A904F9357D4C16DA',
    name='Dunkirk',
    type=ContentTypes.COHORT_RULES)

purchase_itunes_zombieland = UMCContent(
    id='uts.cortrle.b89f2077-afc7-4e0d-9ca5-a1907323126c',
    name='Zombieland',
    type=ContentTypes.COHORT_RULES)

mls_subscription = UMCContent(
    id='uts.cortrle.BDD898F4E892EADFB388FB6C672FE390',
    name='Mls Subscription',
    type=ContentTypes.COHORT_RULES)

shareplay_cat_editorial_video_clip_live = UMCContent(
    id='edt.item.64b81d33-948a-4a51-b2f6-425691150c24',
    name='Shareplay CAT Video - Live',
    type=ContentTypes.EDITORIAL_VIDEO_CLIP
)

shareplay_cat_editorial_video_clip_not_live = UMCContent(
    id='edt.item.64b81dae-cffb-4b93-91d2-c0e0faed2da1',
    name='Shareplay CAT Video - Not Live',
    type=ContentTypes.EDITORIAL_VIDEO_CLIP
)

cat_editorial_video_clip = UMCContent(
    id='edt.item.65529b40-965a-43ba-b439-8b61388a5643',
    name='Cat Video',
    type=ContentTypes.EDITORIAL_VIDEO_CLIP
)

movie_bundle = UMCContent(
    id='umc.cmr.its.bun.48rrujzfm478dy2jxjgdncrdn',
    name='47 Meters Double Feature',
    type=MOVIE_BUNDLE,
    adam_id='1482672315'
)

movie_bundle_2 = UMCContent(
    id='umc.cmr.its.bun.h9j90lt2qd6gkqx8f8hhy4rg',
    name='Fantastic Four & Fantastic Four Rise of the Silver Surfer 2',
    type=MOVIE_BUNDLE,
    adam_id='1361857785'
)

movie_bundle_3 = UMCContent(
    id='umc.cmr.its.bun.4tehtcfkqnfbqwlr85ixuwrol',
    secondary_id='edt.item.65d5013c-8ac2-4c46-a311-1f06cf7947b8',
    name='',
    type=MOVIE_BUNDLE
)

movie_bundle_exp_line_epic_stage = UMCContent(
    id='umc.cmr.its.bun.102a6fvntptb1a3z9n3yj8qaj',
    name='DC Universe 4K HDR 6-Film Collection',
    type=MOVIE_BUNDLE
)

movie_ei_bundle_exp_line_epic_stage = UMCContent(
    id='umc.cmr.its.bun.5u2dc4zmqj4g1ekfaqk6tquta',
    name='Wizarding World 10 Film Collection',
    type=MOVIE_BUNDLE
)

# only available in ES
unavailable_movie_bundle = UMCContent(
    id='umc.cmr.its.bun.3e56912sxi6g5sjbeuaiiy6ni',
    name='Coleccion Mejor Pelicula',
    type=MOVIE_BUNDLE,
)

box_set_lost = UMCContent(
    id='',
    name='',
    type=BOX_SET,
    adam_id='66012553'
)

box_set_exp_line_epic_stage = UMCContent(
    id='umc.cmr.its.se.16w19vi6n74vbbm1hj9yztr3l',
    name='The Big Bang Theory: The Complete Series',
    type=BOX_SET,
    adam_id='1450994202'
)

box_set_ei_exp_line_epic_stage = UMCContent(
    id='umc.cmr.its.se.10xzg6kirjttx6oaponhlzdpw',
    name='The Good Wife Boxset',
    type=BOX_SET,
    adam_id='1307176316'
)

box_set_purchased = UMCContent(
    id='umc.cmr.its.se.10xzg6kirjttx6oaponhlzdpw',
    name='',
    type=BOX_SET,
)

extra_ei_exp_line_epic_stage = UMCContent(
    name='Ready',
    id='umc.cmc.3e1q8vrgjv7y0lx9j1aie57oa',
    type=EXTRA)

extra_exp_line_epic_stage = UMCContent(
    name='Future: Season 1',
    id='umc.cmc.6usimyi7zbfiyr7t40z1ouxwc',
    type=EXTRA)

sports_extra_exp_line_epic_stage = UMCContent(
    name='Clip 2',
    id='umc.cmc.55kn8k5nkcbaaw79xw0zukmc6',
    type=EXTRA)

sports_extra_ei_exp_line_epic_stage = UMCContent(
    name='Goal: M. Hartel vs. LA, 49',
    id='umc.cmc.4cneobhjs4nj5o4i1jo1a6csy',
    type=EXTRA)

movie_bonus_extra = UMCContent(
    name='Movie Extra - Bonus',
    id='umc.cmc.1t90vm6zpy7i9o3fjgpa4yyf',
    type=EXTRA)

movie_trailer_extra = UMCContent(
    name='Movie Extra - Trailer',
    id='umc.cmc.3ihovhngh8g0nhfthpt6c8ggm',
    type=EXTRA)

extra_with_header_override_title = UMCContent(
    id='umc.cmc.4qkjg4oov3uqbxboh2nvrl0ar',
    name='An Inside Look',
    type=EXTRA
)

box_set = BoxSet(
    id='umc.cmr.its.se.gg8wn0yknpt6bmvgsnz1joi8',
    name='Mama\'s Family',
    type=BOX_SET,
    show_id='umc.cmc.2bs77l6sbyalpd0nkrrlqsl5r',
    adam_id='1395423950'
)

purchased_box_set = BoxSet(
    id='umc.cmr.its.se.244vv0y31rjffl0bzn28t1uge',
    name='Game of Thrones, Seasons 1-7',
    type=BOX_SET,
    show_id='umc.cmc.7htjb4sh74ynzxavta5boxuzq',
    adam_id='1252634964'
)

extra = UMCContent(
    id='umc.cmc.2anexqvqclc4k6jktab0ae4d',
    name='Jurassic World',
    type=EXTRA
)

unavailable_for_kr_extra = UMCContent(
    id='umc.cmc.aitacxahxadzpxklh881ate4',
    name='The LEGO Movie Trailer',
    type=EXTRA
)

box_set_2 = BoxSet(
    id='umc.cmr.its.se.25i38fujqjkv95wfdwleniigb',
    name='Angel the complete series',
    type=BOX_SET,
    show_id='umc.cmc.2253c7uattfsv83fcg8pz56iu',
    adam_id='1352132838',
    show_reference_id='umc.cmr.its.sh.6up5du0hl882vb7vmz14td5se'
)

federated_brand = UMCContent(
    id='tvs.sbd.12962',
    secondary_id='edt.item.65d4eeed-1cd7-42a4-bd57-56c618f94362',
    name='',
    type=ContentTypes.OTHER
)

mccormick_brand = UMCContent(
    id='tvs.sbd.11000065',
    secondary_id='edt.item.65d4fef3-bbf5-4244-9c36-dca9791c423d',
    name='',
    type=ContentTypes.OTHER
)

brand_ei_exp_line_epic_stage = UMCContent(
    id='tvs.sbd.1000051',
    secondary_id='edt.item.681b8dd3-97aa-4d28-9d58-259bc238ca33',
    name='The Home of Apple Originals',
    type=ContentTypes.OTHER
)

brand_exp_line_epic_stage = UMCContent(
    id='tvs.sbd.11000111',
    name='The Home of Apple Originals',
    type=ContentTypes.OTHER
)

room = UMCContent(
    id='edt.cvs.65d50343-aa35-401e-85cd-9c6e07769ef2',
    secondary_id='edt.item.65d501db-22fe-490e-866b-c99ab5a079aa',
    name='',
    type=ContentTypes.OTHER
)

extra = UMCContent(
    id='umc.cmc.5hfdtjhnq3qdni0aqjk4q41cv',
    name='extra',
    type=ContentTypes.OTHER
)

tennis_VOD_sporting_event = UMCContent(
    name='Fourth Round Carlos Alcaraz vs. Karen Khachanov',
    id='umc.cse.1ovg593fdo13ta5txlqrl1cy',
    type=ContentTypes.SPORTING_EVENT)
