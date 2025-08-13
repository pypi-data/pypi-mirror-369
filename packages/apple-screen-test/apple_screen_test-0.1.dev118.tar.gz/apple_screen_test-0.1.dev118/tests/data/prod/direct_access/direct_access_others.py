from test_data_classes import UMCContent, MOVIE_BUNDLE, BOX_SET, EXTRA, BoxSet, LIVE_SERVICE
from test_data_keys import ContentTypes

apple_music_tv = UMCContent(
    name='Apple Music TV',
    id='edt.item.5fb6fd48-036a-48e6-ad5f-4a9b77d42248',
    type=ContentTypes.EDITORIAL_VIDEO_CLIP)

cat_editorial_video_clip = UMCContent(
    id='edt.item.5fb6fd48-036a-48e6-ad5f-4a9b77d42248',
    name='Cat Video',
    type=ContentTypes.EDITORIAL_VIDEO_CLIP
)

movie_bonus_extra = UMCContent(
    name='Movie Extra - Bonus',
    id='umc.cmc.1t90vm6zpy7i9o3fjgpa4yyf',
    type=EXTRA)

movie_trailer_extra = UMCContent(
    name='Movie Extra - Trailer',
    id='umc.cmc.3ihovhngh8g0nhfthpt6c8ggm',
    type=EXTRA)

movie_preview_extra = UMCContent(
    name='Movie Extra - Preview',
    id='umc.cmc.4f4ln5hvuhfczfokyfi0ktqyi',
    type=EXTRA)

tv_show_bonus_extra = UMCContent(
    name='TV Show Extra - Bonus',
    id='umc.cmc.2cusc8mraqx9381zhac82ap2f',
    type=EXTRA)

live_service = UMCContent(
    # ID retrieved from: https://uts-admin-mr22.itunes.apple.com/app/tvs-tools/live-services
    id='tvs.lvs.1017422',
    name='Apple Keynote',
    type=LIVE_SERVICE
)

box_set = BoxSet(
    id='umc.cmr.its.se.25i38fujqjkv95wfdwleniigb',
    name='Angel the complete series',
    show_id='umc.cmc.2253c7uattfsv83fcg8pz56iu',
    type=BOX_SET,
    adam_id='1352132838',
    show_reference_id='umc.cmr.its.sh.6up5du0hl882vb7vmz14td5se'
)

movie_bundle = UMCContent(
    id='umc.cmr.its.bun.5u2dc4zmqj4g1ekfaqk6tquta',
    name='Wizarding World 10 Film Collection',
    type=MOVIE_BUNDLE
)

movie_bundle_2 = UMCContent(
    id='umc.cmr.its.bun.h9j90lt2qd6gkqx8f8hhy4rg',
    name='Fantastic Four & Fantastic Four Rise of the Silver Surfer 2',
    type=MOVIE_BUNDLE,
    adam_id='1361857785'
)

# only available in ES
unavailable_movie_bundle = UMCContent(
    id='umc.cmr.its.bun.3e56912sxi6g5sjbeuaiiy6ni',
    name='Coleccion Mejor Pelicula',
    type=MOVIE_BUNDLE,
)

unavailable_for_kr_extra = UMCContent(
    id='umc.cmc.aitacxahxadzpxklh881ate4',
    name='The LEGO Movie Trailer',
    type=EXTRA
)

movie_bundle_john_wick = UMCContent(
    id='umc.cmr.its.bun.6a3w0vlhvs3co5pe3dzibbkym',
    name='John Wick 4-Film Collection',
    type=MOVIE_BUNDLE
)
