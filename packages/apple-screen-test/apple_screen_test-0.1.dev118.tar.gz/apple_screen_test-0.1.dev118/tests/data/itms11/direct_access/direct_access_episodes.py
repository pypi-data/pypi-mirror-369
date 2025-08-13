from content_types import EPISODE
from test_data_classes import Episode
from test_data_keys import CanvasNames

episode_tv_plus_ted_lasso_s1e1 = Episode(
    id='umc.cmc.2sp4pbfnp4sai5qen74ub8skc',
    name='Ted Lasso S01E01',
    type=EPISODE,
    show_id='umc.cmc.vtoh0mn0xn7t3c643xqonfzy',
    required_entitlement=[CanvasNames.TV_PLUS],
)

episode_tv_plus_ted_lasso_s1e2 = Episode(
    id='umc.cmc.4rbovjxx7gmmh4nk0y8gppe4g',
    name='Ted Lasso S01E02',
    type=EPISODE,
    show_id='umc.cmc.vtoh0mn0xn7t3c643xqonfzy',
    required_entitlement=[CanvasNames.TV_PLUS],
)

# last episode of S01
episode_tv_plus_ted_lasso_s1e10 = Episode(
    id='umc.cmc.2z1m874kxcafy9erdvjm2243w',
    name='Ted Lasso S01E10',
    type=EPISODE,
    show_id='umc.cmc.vtoh0mn0xn7t3c643xqonfzy',
    required_entitlement=[CanvasNames.TV_PLUS],
)

episode_tv_plus_ted_lasso_s2e1 = Episode(
    id='umc.cmc.usy4k5ac9a76hh3rgayqt5gh',
    name='Ted Lasso S02E01',
    type=EPISODE,
    show_id='umc.cmc.vtoh0mn0xn7t3c643xqonfzy',
    required_entitlement=[CanvasNames.TV_PLUS],
)

episode_tv_plus_ted_lasso_s2e3 = Episode(
    id='umc.cmc.2xmvpye3wlv856x1oldennqa2',
    name='Ted Lasso S02E03',
    type=EPISODE,
    show_id='umc.cmc.vtoh0mn0xn7t3c643xqonfzy',
    required_entitlement=[CanvasNames.TV_PLUS],
)

episode_tv_plus_ted_lasso_last_episode = Episode(
    id='umc.cmc.1tw42m6edagsi9nssz4fek3z4',
    name='Ted Lasso S02E03',
    type=EPISODE,
    show_id='umc.cmc.vtoh0mn0xn7t3c643xqonfzy',
    required_entitlement=[CanvasNames.TV_PLUS],
)

episode_the_office = Episode(
    id='umc.cmc.46hi348gkaf8y87whf39b4eh4',
    name='The Office S1 E1',
    type=EPISODE,
    show_id='umc.cmc.455js879szmdywutf3qjewagm',
    required_entitlement=[CanvasNames.ITUNES],
)

episode_see_s1e1 = Episode(
    id='umc.cmc.6ne0pubfvxu7n3n30ngl1fafy',
    name='SEE S01E01',
    type=EPISODE,
    show_id='umc.cmc.3s4mgg2y7h95fks9gnc4pw13m',
    required_entitlement=[CanvasNames.TV_PLUS],
)

episode_see_s1_e8 = Episode(
    id='umc.cmc.1xirz9a29mh1rlk48d13zxgqf',
    name='SEE S01E08',
    type=EPISODE,
    show_id='umc.cmc.3s4mgg2y7h95fks9gnc4pw13m',
    required_entitlement=[CanvasNames.TV_PLUS],
)

episode_see_s2_e1 = Episode(
    id='umc.cmc.4tbw91jm7z0wjg3y9d0genmc4',
    name='SEE S01E08',
    type=EPISODE,
    show_id='umc.cmc.3s4mgg2y7h95fks9gnc4pw13m',
    required_entitlement=[CanvasNames.TV_PLUS],
)

episode_1_show_available_on_multiple_channels = Episode(
    id='umc.cmc.749s9lor713zctovvit59nfu9',
    name='Central Park S1, Episode 1',
    type=EPISODE,
    show_id='umc.cmc.4qe3i11erof30x0vz8nwnjkw3',
    required_entitlement=[CanvasNames.TV_PLUS, CanvasNames.PARAMOUNT_PLUS_MCCORMICK, CanvasNames.EVERGREEN_MCCORMICK],
)

episode_2_show_available_on_multiple_channels = Episode(
    id='umc.cmc.1y7wz90u5euts960i6itdhi9f',
    name='Central Park S1, Episode 2',
    type=EPISODE,
    show_id='umc.cmc.4qe3i11erof30x0vz8nwnjkw3',
    required_entitlement=[CanvasNames.TV_PLUS, CanvasNames.PARAMOUNT_PLUS_MCCORMICK, CanvasNames.EVERGREEN_MCCORMICK],
)

episode_3_show_available_on_multiple_channels = Episode(
    id='umc.cmc.4odt9w001k0buv6vj4mv6slny',
    name='Central Park S1, Episode 3',
    type=EPISODE,
    show_id='umc.cmc.4qe3i11erof30x0vz8nwnjkw3',
    required_entitlement=[CanvasNames.TV_PLUS, CanvasNames.PARAMOUNT_PLUS_MCCORMICK, CanvasNames.EVERGREEN_MCCORMICK],
)

# Has timed-metadata
episode_foundation_s1e1 = Episode(
    id='umc.cmc.ivjr6uixykbs8y3hs1ld6ya1',
    name='Foundation S1, Episode 1',
    type=EPISODE,
    show_id='umc.cmc.5983fipzqbicvrve6jdfep4x3',
    required_entitlement=[CanvasNames.TV_PLUS],
)

# Has timed-metadata
episode_ted_lasso_s1e1 = Episode(
    id='umc.cmc.2sp4pbfnp4sai5qen74ub8skc',
    name='Ted Lasso S1, Episode 1',
    type=EPISODE,
    show_id='umc.cmc.vtoh0mn0xn7t3c643xqonfzy',
    required_entitlement=[CanvasNames.TV_PLUS],
)

# Has timed-metadata
episode_ted_lasso_s1e2 = Episode(
    id='umc.cmc.4rbovjxx7gmmh4nk0y8gppe4g',
    name='Ted Lasso S1, Episode 2',
    type=EPISODE,
    show_id='umc.cmc.vtoh0mn0xn7t3c643xqonfzy',
    required_entitlement=[CanvasNames.TV_PLUS],
)

# Has timed-metadata
episode_loot_s2e1 = Episode(
    id='umc.cmc.647xpyq5v0fs701gtkao3r3s1',
    name='Loot S2, Episode 1',
    type=EPISODE,
    show_id='umc.cmc.5erbujil1mpazuerhr1udnk45',
    required_entitlement=[CanvasNames.TV_PLUS],
)

# Has timed-metadata
episode_for_all_mankind = Episode(
    id='umc.cmc.58sfmdd593tmvwp2n3vdfwykw',
    name='For All Mankind S1, Episode 1',
    type=EPISODE,
    show_id='umc.cmc.1802pn6jlq2mz70gj7mezrfg9',
    required_entitlement=[CanvasNames.TV_PLUS],
)

# Has timed-metadata
episode_the_morning_show_s1e1 = Episode(
    id='umc.cmc.1rat4b7sugk86431sdqrsb64q',
    name='The Morning Show S1, Episode 1',
    type=EPISODE,
    show_id='umc.cmc.4967ders5yx2f7prkpxmoh0kb',
    required_entitlement=[CanvasNames.TV_PLUS],
)

# Has timed-metadata
episode_invasion_s1e1 = Episode(
    id='umc.cmc.6g6bfh72siinebw0pub8qoarv',
    name='Invasion S1, Episode 1',
    type=EPISODE,
    show_id='umc.cmc.70b7z97fv7azfzn5baqnj88p6',
    required_entitlement=[CanvasNames.TV_PLUS],
)

ja_jp_episode = Episode(
    id='umc.cmc.5597q0j4xydwovvomq1ut22jr',
    name='Death Note S1E01',
    type=EPISODE,
    show_id='umc.cmc.5597q0j4xydwovvomq1ut22jr',
    required_entitlement=[CanvasNames.PLUTO_TV, CanvasNames.TUBI, CanvasNames.PRIME_VIDEO],
)

episode = Episode(
    id='umc.cmc.4rbovjxx7gmmh4nk0y8gppe4g',
    name='Ted Lasso S01E02',
    type=EPISODE,
    show_id='umc.cmc.vtoh0mn0xn7t3c643xqonfzy',
    required_entitlement=[CanvasNames.TV_PLUS],
)

next_episode = Episode(
    id='umc.cmc.2eh60p08itw0bmmp0lqpx6ig6',
    name='Ted Lasso S01E03',
    type=EPISODE,
    show_id='umc.cmc.vtoh0mn0xn7t3c643xqonfzy',
    required_entitlement=[CanvasNames.TV_PLUS],
)

episode_not_subscribed = Episode(
    id='umc.cmc.2xmvpye3wlv856x1oldennqa2',
    name='Ted Lasso S02E03',
    type=EPISODE,
    show_id='umc.cmc.vtoh0mn0xn7t3c643xqonfzy',
    required_entitlement=[CanvasNames.TV_PLUS],
)

autoplay_episode = Episode(
    id='umc.cmc.76ux7lz8y1bxez1dx1c05828y',
    name='The Morning Show S02E10',
    type=EPISODE,
    show_id='umc.cmc.hsmzusvkidbq0g135pwcfr4p',
    related_content={
        # This is generated from global_properties
        'autoplay_movie': "umc.cmc.40qrv09i2yfh8iilyi4s8vfi"
    },
    required_entitlement=[CanvasNames.TV_PLUS],
)

last_episode_before_coming_soon = Episode(
    id='umc.cmc.47qe5bf7rhy2h9g1kri0ejvpd',
    name='ATVShow64_ep4',
    type=EPISODE,
    description='Fresh Prince',
    show_id='umc.cmc.5d3hragfaafqynkv40puz6i6v',
    required_entitlement=[CanvasNames.TV_PLUS],
)

coming_soon_episode = Episode(
    id='umc.cmc.6c6op52yzcuo9wpotsggo7886',
    name='ATVShow64_ep4',
    type=EPISODE,
    description='Fresh Prince',
    show_id='umc.cmc.5d3hragfaafqynkv40puz6i6v',
    required_entitlement=[CanvasNames.TV_PLUS],
)

FAM_episode_S5E1 = Episode(
    id='umc.cmc.6qutjxgcq1lu1ijew1fx2p4dh',
    name='For all Mankind S05E01',
    type=EPISODE,
    show_id='umc.cmc.1802pn6jlq2mz70gj7mezrfg9',
    required_entitlement=[CanvasNames.TV_PLUS],
)

FAM_episode_S6E1 = Episode(
    id='umc.cmc.6i153hrrx7g8a6jfblzfglbx4',
    name='For all Mankind S06E01',
    type=EPISODE,
    show_id='umc.cmc.1802pn6jlq2mz70gj7mezrfg9',
    required_entitlement=[CanvasNames.TV_PLUS],
)

graves_episode = Episode(
    id='umc.cmc.5sq5814h2xrf6rmzful2jhr3u',
    name='Graves S03E01',
    type=EPISODE,
    show_id='umc.cmc.6q8ncg5fahjoh17himtlpemmk'
)

graves_episode_S5E1 = Episode(
    id='umc.cmc.5odg4d30mvptorr7aizjcwm21',
    name='Graves S05E01',
    type=EPISODE,
    show_id='umc.cmc.6q8ncg5fahjoh17himtlpemmk'
)

graves_episode_S6E1 = Episode(
    id='umc.cmc.2szxrny1vz2xxg5c6xmtr8weq',
    name='Graves S06E01',
    type=EPISODE,
    show_id='umc.cmc.6q8ncg5fahjoh17himtlpemmk'
)

episode_4 = Episode(
    id='umc.cmc.4t7pn0ielxmtd57dz4f5v472d',
    name='The Affair S01E101',
    type=EPISODE,
    adam_id='959222878',
    show_id='umc.cmc.7i7fj0cd4huwtfhz1gf52sapu',
    required_entitlement=[CanvasNames.PARAMOUNT_PLUS_MCCORMICK, CanvasNames.ITUNES, CanvasNames.AT_T_TV,
                          CanvasNames.PRIME_VIDEO],
)

episode_purchased = Episode(
    id='umc.cmc.5t6w20vn8j5qgi05dpgh1ir2m',
    name='NCIS S01E01',
    type=EPISODE,
    show_id='umc.cmc.3en7wd5upm1hx2sdbbr949kbj',
    adam_id='354889730',
    required_entitlement=[CanvasNames.PARAMOUNT_PLUS_MCCORMICK, CanvasNames.ITUNES, CanvasNames.PRIME_VIDEO],
)

episode_tv_plus_truth_be_told_s1_e1 = Episode(
    id='umc.cmc.1y6abvdqr20i3yyx9x9f9yla1',
    name='',
    description='Truth Be Told S01E01',
    show_id='umc.cmc.6hegr60w8pjyfcblgocjek7oo',
    type=EPISODE,
    required_entitlement=[CanvasNames.TV_PLUS],
)

episode_tv_plus_truth_be_told_s1_e3 = Episode(
    id='umc.cmc.5vh46pgqp9ipik1lfnx09vhty',
    name='',
    description='Truth Be Told S01E03',
    show_id='umc.cmc.6hegr60w8pjyfcblgocjek7oo',
    type=EPISODE,
    required_entitlement=[CanvasNames.TV_PLUS],
)

episode_5 = Episode(
    id='umc.cmc.6o4j5bd68jep6yn5e36eh5w1q',
    name='High School Musical: The Musical: The Series S01E01',
    type=EPISODE,
    show_id='umc.cmc.6qaoqfb97kqh7z8wux2mc39my',
    required_entitlement=[CanvasNames.DISNEY_PLUS],
)

episode_pennyworth = Episode(
    id='umc.cmc.6u3arz2ytr2a763bw1lkecc1d',
    type=EPISODE,
    name='Pennyworth, S1E1 Pilot',
    show_id='umc.cmc.3ehqhyoc9wz64seco1cn0lyva',
    adam_id='1478960995',
    required_entitlement=[CanvasNames.TV_PLUS, CanvasNames.AT_T_TV, CanvasNames.HBO_GO, CanvasNames.PRIME_VIDEO,
                          CanvasNames.EPIX_MCCORMICK, CanvasNames.ITUNES],
)

episode_2 = Episode(
    id='umc.cmc.5sm62qaho9mcyud2ztsx72bk1',
    name='Shameless S01E02',
    type=EPISODE,
    show_id='umc.cmc.699yz0ndcm42cxcwcbzkb6dng',
    adam_id='443916897',
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.PRIME_VIDEO],
)

VOD_episode = Episode(
    id='umc.cmc.5fy0skp0iyx2iiuj1so5cvdtx',
    name='Game of Thrones',
    type=EPISODE,
    description='Season 1, Episode 1: Winter Is Coming',
    show_id='umc.cmc.7htjb4sh74ynzxavta5boxuzq',
    adam_id='494877461',
    required_entitlement=[CanvasNames.AT_T_TV, CanvasNames.HBO_GO, CanvasNames.HULU, CanvasNames.PRIME_VIDEO,
                          CanvasNames.ITUNES],
)

episode_3 = Episode(
    id='umc.cmc.4416erjerhj3yyaxt1khjzzr7',
    name='Seinfeld S01E01',
    type=EPISODE,
    show_id='umc.cmc.7wi0fpx37shx0bfxau56ufps',
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.EVERGREEN_MCCORMICK],
)

FAM_episode = Episode(
    id='umc.cmc.134zsh8hfn49oywksmiz383pc',
    name='For all Mankind S03E01',
    type=EPISODE,
    show_id='umc.cmc.1802pn6jlq2mz70gj7mezrfg9',
    required_entitlement=[CanvasNames.TV_PLUS],
)

# Available for ES
unavailable_episode = Episode(
    id='umc.cmc.7187yuxmphbhl8eqrd6w2eqii',
    name='Merli S1E02',
    type=EPISODE,
    show_id='umc.cmc.6eumpdx74x6cq8a74tvaexuhw'
)

capella_episode = Episode(
    id='umc.cmc.60s3gfv0m1ez63l22xtazfojt',
    name='Surface S1E01',
    type=EPISODE,
    show_id='umc.cmc.dzqzvmbvizbedk91cvrq5pvw'
)

# last episode
power_book_s2_e10 = Episode(
    id='umc.cmc.7k8ua7ic09djmrk7avqvj76yo',
    name='Power Book S02E10',
    type=EPISODE,
    show_id='umc.cmc.2eonqforii7xer6suxa0wjyfc',
    required_entitlement=[CanvasNames.STARZ_MCCORMICK, CanvasNames.AT_T_TV, CanvasNames.PRIME_VIDEO],
)

ambitions_s01_e01 = Episode(
    id='umc.cmc.2tcd8v9qglsphvtfwcbynfift',
    name='Ambitions S01E01',
    type=EPISODE,
    show_id='umc.cmc.4ji4ko1xq1em8wkdbjpe1247s',
    required_entitlement=[CanvasNames.PRIME_VIDEO],
)

ambitions_s01_e02 = Episode(
    id='umc.cmc.442xtxwtm3dnqbvhsr82jk8yx',
    name='Ambitions S01E02',
    type=EPISODE,
    show_id='umc.cmc.4ji4ko1xq1em8wkdbjpe1247s',
    required_entitlement=[CanvasNames.ITUNES, CanvasNames.PRIME_VIDEO],
)

black_sails_s01_e08 = Episode(
    id='umc.cmc.3mx7pren2mqlzr64ft7aygzym',
    name='Black Sails S01E08',
    type=EPISODE,
    show_id='umc.cmc.2aq6e38r265c2z6nkjdbacqvd',
    required_entitlement=[CanvasNames.STARZ_MCCORMICK, CanvasNames.AT_T_TV, CanvasNames.HULU, CanvasNames.PRIME_VIDEO,
                          CanvasNames.ITUNES],
)

black_sails_s02_e01 = Episode(
    id='umc.cmc.3qchv2fwah9mbdbikgd9z458b',
    name='Black Sails S02E01',
    type=EPISODE,
    show_id='umc.cmc.2aq6e38r265c2z6nkjdbacqvd',
    required_entitlement=[CanvasNames.STARZ_MCCORMICK, CanvasNames.AT_T_TV, CanvasNames.HULU, CanvasNames.PRIME_VIDEO,
                          CanvasNames.ITUNES],
)

episode_exp_line_epic_stage = Episode(
    id='umc.cmc.hsmzusvkidbq0g135pwcfr4p',
    name='Final Call',
    type=EPISODE,
    show_id='umc.cmc.1dg08zn0g3zx52hs8npoj5qe3'
)

episode_ei_exp_line_epic_stage = Episode(
    id='umc.cmc.q2j08ycbxl4uhdah0j8ocpjh',
    name='3 Degrees',
    type=EPISODE,
    show_id='umc.cmc.1dg08zn0g3zx52hs8npoj5qe3'
)
