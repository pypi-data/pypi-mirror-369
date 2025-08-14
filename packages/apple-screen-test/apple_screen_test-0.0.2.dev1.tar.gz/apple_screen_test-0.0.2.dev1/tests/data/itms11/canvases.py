from data.itms11.direct_access import direct_access
from test_data_classes import Canvas, Collection, Context
from test_data_keys import CanvasNames, CanvasTypes, CollectionNames, DisplayTypes

####################################################################################################
# CANVASES => CHANNEL/ROOTS
####################################################################################################
CANVASES = {
    # test_data.CANVASES[Canvases.TV_PLUS].id
    CanvasNames.TV_PLUS: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.4000',
        is_first_party=True,
        name='AppleTV+',
        vod_service='tvs.vds.4105',
        external_service_id='com.equus.apple.svod.linear2.US',
        salable_adam_id='1472441559,1478184786,1481150412',
        media_content={  # Example of Media Content
            'movie': direct_access['movie'],
            'movie_2': direct_access['movie_2'],
            'licenced_movie': direct_access['licenced_movie'],
            'coming_soon_movie': direct_access['coming_soon_movie'],
            'movie_with_extra_content': direct_access['movie_with_extra_content'],
            'show': direct_access['show'],
            'coming_soon_show': direct_access['coming_soon_show'],
            'show_coming_soon_episodes': direct_access['show_coming_soon_episodes'],
            'season': direct_access['season'],
            'episode': direct_access['episode'],
            'next_episode': direct_access['next_episode'],
            'episode_not_subscribed': direct_access['episode_not_subscribed'],
            'autoplay_episode': direct_access['autoplay_episode'],
            'postplay_movie': direct_access['postplay_movie'],
            'coming_soon_episode': direct_access['coming_soon_episode'],
            'coming_soon_sporting_event': direct_access['coming_soon_sporting_event'],
            'movie_bundle': direct_access['movie_bundle'],
            'FAM_show': direct_access['FAM_show'],
            'FAM_episode': direct_access['FAM_episode'],
            'FAM_season': direct_access['FAM_season'],
            'FAM_episode_S5E1': direct_access['FAM_episode_S5E1'],
            'FAM_episode_S6E1': direct_access['FAM_episode_S6E1'],
            'truth_be_told_show': direct_access['truth_be_told_show'],
            'VOD_movie': direct_access['VOD_movie'],
            'flat_show': direct_access['flat_show'],
            'live_service': direct_access['live_service'],
            'box_set': direct_access['box_set'],
            'purchased_box_set': direct_access['purchased_box_set'],
            'extra': direct_access['extra'],
            'immersive': direct_access['immersive'],
            '3d': direct_access['threeD'],
            'live_sporting_event': direct_access['mlb_live_sporting_event'],
            'upcoming_sporting_event': direct_access['mlb_upcoming_sporting_event'],
            'mlb_VOD_sporting_event': direct_access['mlb_VOD_sporting_event'],
            'show_tv_plus_ted_lasso': direct_access['show_tv_plus_ted_lasso'],
            'episode_tv_plus_ted_lasso_s1e1': direct_access['episode_tv_plus_ted_lasso_s1e1'],
        },
        collection_items={
            CollectionNames.CHANNEL_UPSELL_OFFER: Collection(
                collection_id='edt.col.5db3298f-c715-44b5-910b-981242360b75',
                context_ids={
                    DisplayTypes.CHANNEL_UPSELL: Context(
                        root='',
                        canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                        shelf='edt.shelf.5db32a0b-50d5-4953-b8a4-baac80881241',
                        display_type=DisplayTypes.CHANNEL_UPSELL
                    )
                }
            ),
            CollectionNames.EPIC_INLINE_OFFER: Collection(
                collection_id='edt.col.5e6bba80-9bb8-4d57-ba28-676c5b142490',
                context_ids={
                    DisplayTypes.EPIC_INLINE: Context(
                        root='',
                        canvas='edt.cvs.5e5d69b2-224c-4fdb-a593-887eebceedcc',
                        shelf='edt.shelf.5e6bbf48-83a9-4beb-9e72-542ff4873d6c',
                        display_type=DisplayTypes.EPIC_INLINE,
                        flavor='Flavor_E'
                    )
                }
            ),
            CollectionNames.EPIC_SHOWCASE_OFFER: Collection(
                collection_id='edt.col.5e70fefe-2217-4d94-8519-87cf1c8e5a47',
                context_ids={
                    DisplayTypes.EPIC_SHOWCASE: Context(
                        root='',
                        canvas='edt.cvs.5e6b04e9-c3f6-4f99-bf1d-64f7e9c4092e',
                        shelf='edt.shelf.5e70ff3f-a3e3-409e-af50-ba0ceef91244',
                        display_type=DisplayTypes.EPIC_SHOWCASE,
                        flavor='Flavor_E'
                    )
                }
            ),
            CollectionNames.SPOTLIGHT_OFFER: Collection(
                collection_id='edt.col.5dab7762-642a-490c-9f4d-a531f7944239',
                context_ids={
                    DisplayTypes.SPOTLIGHT: Context(
                        root='',
                        canvas='edt.cvs.5d44d57c-3a1a-481c-8911-853f7615bbc4',
                        shelf='edt.shelf.5d9d443f-74ca-40de-9c36-a9571eb4903b',
                        display_type=DisplayTypes.SPOTLIGHT,
                    )
                }
            ),
            CollectionNames.EPIC_STAGE: Collection(
                collection_id='edt.col.629e7e8d-14dd-4cc4-ae4a-c9dfddc1844b',
                context_ids={
                    DisplayTypes.EPIC_STAGE: Context(
                        canvas='edt.cvs.610c550f-938a-46e7-98e3-c573fcd24208',
                        shelf='edt.shelf.62b24ec1-af42-4487-9f2b-ba6201fc11eb',
                        display_type=DisplayTypes.EPIC_STAGE
                    )
                }
            ),
            CollectionNames.EPIC_STAGE_WITH_UPSELL: Collection(
                collection_id='edt.col.62292489-5e93-4292-b04f-af0dcefbd039',
                context_ids={
                    DisplayTypes.EPIC_STAGE_WITH_UPSELL: Context(
                        canvas='edt.cvs.5d44d57c-3a1a-481c-8911-853f7615bbc4',
                        shelf='edt.shelf.6270780c-7b56-4228-bada-e5178c488893',
                        display_type=DisplayTypes.EPIC_STAGE_WITH_UPSELL
                    )
                }
            )
        },
        up_next_fallback={
            'up_next_fallback_collection_id': 'edt.col.5f4d6194-f8c7-4f7d-bc9b-dc551f6c8bab',
            'up_next_fallback_category_name': 'uts.category.no_up_next___tv+'
        }
    ),
    CanvasNames.MLS: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.7000',
        is_first_party=True,
        name='MLS Season Pass',
        vod_service='tvs.vds.7005',
        salable_adam_id='6445132388,6445132219,1472441559',
        external_service_id='MLS_Test_070123_SP',
        external_id='STATIC_MTN_ATVP_SUB_LIVE_EN',
        media_content={
            'mls_upcoming_sporting_event_free': direct_access['mls_upcoming_sporting_event_free'],
            'mls_live_sporting_event_free': direct_access['mls_live_sporting_event_free_2'],
            'mls_live_sporting_event_free_home_away_streams':
                direct_access['mls_live_sporting_event_free_home_away_streams'],
            'mls_live_sporting_event_imm_pl': direct_access['mls_live_sporting_event_imm_pl'],
            'mls_live_sporting_event_imm_2d_pl': direct_access['mls_live_sporting_event_imm_2d_pl'],
            'mls_VOD_sporting_event_free': direct_access['mls_VOD_sporting_event_free'],

            # Available for tv plus and/or mls subscribed users
            'mls_upcoming_sporting_event_tv_plus': direct_access['mls_upcoming_sporting_event_tv_plus'],
            'mls_live_sporting_event_tv_plus': direct_access['mls_live_sporting_event_tv_plus_2'],
            'mls_VOD_sporting_event_tv_plus': direct_access['mls_VOD_sporting_event_tv_plus_2'],

            # Available for mls subscribed users
            'mls_upcoming_sporting_event_mls': direct_access['mls_upcoming_sporting_event_mls_2'],
            'mls_live_sporting_event_mls': direct_access['mls_live_sporting_event_mls_4'],
            'mls_VOD_sporting_event_mls': direct_access['mls_VOD_sporting_event_mls'],
            'mls_VOD_sporting_event_mls_2': direct_access['mls_VOD_sporting_event_mls_2'],

            'mls_VOD_campeones_cup_sporting_event_mls': direct_access['mls_VOD_campeones_cup_sporting_event_mls'],

            'sports_extras_lockup_sporting_event': direct_access['sports_extras_lockup_sporting_event'],
            'mls_live_to_VOD_sporting_event': direct_access['mls_live_to_VOD_sporting_event'],

            'team_seattle_sounders_fc': direct_access['team_seattle_sounders_fc'],

        },
        collection_items={
            CollectionNames.CHANNEL_UPSELL_OFFER: Collection(
                collection_id='edt.col.5e3c958f-ba1f-4202-8a5a-91d522b09b94',
                context_ids={
                    DisplayTypes.CHANNEL_UPSELL: Context(
                        root='',
                        canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                        shelf='edt.shelf.5e3c96d2-8feb-4d57-909c-f415fea63f0e',
                        display_type=DisplayTypes.CHANNEL_UPSELL
                    )
                }
            ),
            CollectionNames.EPIC_INLINE_OFFER: Collection(
                collection_id='edt.col.6322220c-f4b0-4169-92a7-a334a8f74a46',
                context_ids={
                    DisplayTypes.EPIC_INLINE: Context(
                        root='',
                        canvas='edt.cvs.5e5d69b2-224c-4fdb-a593-887eebceedcc',
                        shelf='edt.shelf.632226f6-9dbd-4920-a986-576e6fb87b61',
                        display_type=DisplayTypes.EPIC_INLINE,
                        flavor='Flavor_E'
                    )
                }
            ),
            CollectionNames.EPIC_SHOWCASE_OFFER: Collection(
                collection_id='edt.col.5e70fefe-2217-4d94-8519-87cf1c8e5a47',
                context_ids={
                    DisplayTypes.EPIC_SHOWCASE: Context(
                        root='',
                        canvas='edt.cvs.5e6b04e9-c3f6-4f99-bf1d-64f7e9c4092e',
                        shelf='edt.shelf.5e70ff3f-a3e3-409e-af50-ba0ceef91244',
                        display_type=DisplayTypes.EPIC_SHOWCASE,
                        flavor='Flavor_E'
                    )
                }
            ),
            CollectionNames.SPOTLIGHT_OFFER: Collection(
                collection_id='edt.col.5dab7762-642a-490c-9f4d-a531f7944239',
                context_ids={
                    DisplayTypes.SPOTLIGHT: Context(
                        root='',
                        canvas='edt.cvs.5d44d57c-3a1a-481c-8911-853f7615bbc4',
                        shelf='edt.shelf.5d9d443f-74ca-40de-9c36-a9571eb4903b',
                        display_type=DisplayTypes.SPOTLIGHT,
                    )
                }
            ),
            CollectionNames.EPIC_STAGE_WITH_UPSELL: Collection(
                collection_id='edt.col.632220b4-b62a-43fa-bf19-993f3c2b6828',
                context_ids={
                    DisplayTypes.EPIC_STAGE_WITH_UPSELL: Context(
                        canvas='edt.cvs.631bd6a1-9074-409e-a3f7-35620da139c8',
                        shelf='edt.shelf.632241d8-f14e-4b8b-92e6-737feb1e5a2a',
                        display_type=DisplayTypes.EPIC_STAGE_WITH_UPSELL
                    )
                }
            )
        },
        up_next_fallback={
            'up_next_fallback_collection_id': 'edt.col.6388ec8d-5fba-4332-93f1-bf935e447eb8',
            'up_next_fallback_category_name': 'uts.category.no_up_next___mtn_channel'
        }
    ),
    CanvasNames.CHAPMAN: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.8000',
        salable_adam_id_in_market='10788601924,10788601949',
        salable_adam_id_out_market="10790120869,10790120887",
        is_first_party=True,
        name='Chapman League Pass',
        media_content={
            'team_san_diego_padres': direct_access['team_san_diego_padres'],
            'chapman_live_np_at_p': direct_access['chapman_live_np_at_p'],
            'chapman_tv_plus_live_p_at_p': direct_access['chapman_tv_plus_live_p_at_p'],
            'chapman_federated_live_p_at_p': direct_access['chapman_federated_live_p_at_p']
        }
    ),
    CanvasNames.SHOWTIME_MCCORMICK: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.11000099',
        is_first_party=True,
        name='Showtime',
        vod_service='tvs.vds.11000152',
        salable_adam_id='1455895207',
        is_enabled_for_editorial_featuring=False,
        media_content={
            'movie': direct_access['movie_3'],
            'show': direct_access['show_2'],
            'episode': direct_access['episode_2']
        },
        collection_items={
            CollectionNames.CHANNEL_UPSELL_OFFER: Collection(
                collection_id='edt.col.5e3c958f-ba1f-4202-8a5a-91d522b09b94',
                context_ids={
                    DisplayTypes.CHANNEL_UPSELL: Context(
                        root='',
                        canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                        shelf='edt.shelf.5e3c96d2-8feb-4d57-909c-f415fea63f0e',
                        display_type=DisplayTypes.CHANNEL_UPSELL
                    )
                }
            ),
            CollectionNames.EPIC_INLINE_OFFER: Collection(
                collection_id='edt.col.5efa5e5d-4c86-4054-8928-5e887f4f716a',
                context_ids={
                    DisplayTypes.EPIC_INLINE: Context(
                        root='',
                        canvas='edt.cvs.5efa4a15-7d8e-4922-ab1e-e850e373b71e',
                        shelf='edt.shelf.5efa6104-88a9-4ba6-9cb2-d534be66ec4f',
                        display_type=DisplayTypes.EPIC_INLINE,
                        flavor='Flavor_E'
                    )
                }
            ),
            CollectionNames.EPIC_SHOWCASE_OFFER: Collection(
                collection_id='edt.col.5efa5f87-dfa0-4300-87d7-d55eb33e1c42',
                context_ids={
                    DisplayTypes.EPIC_SHOWCASE: Context(
                        root='',
                        canvas='edt.cvs.5efa4a15-7d8e-4922-ab1e-e850e373b71e',
                        shelf='edt.shelf.5efa6104-e060-4caf-b8dc-cc8bcd9fec4f',
                        display_type=DisplayTypes.EPIC_SHOWCASE,
                        flavor='Flavor_E'
                    )
                }
            ),
            CollectionNames.SPOTLIGHT_OFFER: Collection(
                collection_id='edt.col.5efa514f-e6af-4cc8-bf1c-c661b488f4a3',
                context_ids={
                    DisplayTypes.SPOTLIGHT: Context(
                        root='',
                        canvas='edt.cvs.5efa4a15-7d8e-4922-ab1e-e850e373b71e',
                        shelf='edt.shelf.5efa4a15-ce1e-4ec6-9324-3162b621433f',
                        display_type=DisplayTypes.SPOTLIGHT,
                    )
                }
            )
        }
    ),
    CanvasNames.EVERGREEN_MCCORMICK: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.11000109',
        is_first_party=True,
        name='Evergreen Showtime East',
        vod_service='tvs.vds.11000166',
        salable_adam_id='2000253401',
        media_content={
            'movie': direct_access['movie_4'],
            'show': direct_access['show_3'],
            'episode': direct_access['episode_3'],
            'graves_show': direct_access['graves_show'],
            'graves_episode': direct_access['graves_episode'],
            'graves_episode_S5E1': direct_access['graves_episode_S5E1'],
            'graves_episode_S6E1': direct_access['graves_episode_S6E1'],
            'live_sporting_event': direct_access['live_sporting_event'],
            'upcoming_sporting_event': direct_access['upcoming_sporting_event'],
            'static_sporting_event': direct_access['static_sporting_event'],
            'mls_playable_sporting_event': direct_access['mls_playable_sporting_event']
        },
        collection_items={
            CollectionNames.CHANNEL_UPSELL_OFFER: Collection(
                collection_id='edt.col.5e3c958f-ba1f-4202-8a5a-91d522b09b94',
                context_ids={
                    DisplayTypes.CHANNEL_UPSELL: Context(
                        root='',
                        canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                        shelf='edt.shelf.5e3c96d2-8feb-4d57-909c-f415fea63f0e',
                        display_type=DisplayTypes.CHANNEL_UPSELL
                    )
                }
            ),
            CollectionNames.EPIC_INLINE_OFFER: Collection(
                collection_id='edt.col.6320eecb-4bc0-4d3d-a757-743cd1d0bf39',
                context_ids={
                    DisplayTypes.EPIC_INLINE: Context(
                        root='',
                        canvas='edt.cvs.5e14fd43-909a-4fca-9fe4-d9bf2ba71354',
                        shelf='edt.shelf.6320f010-79be-4d31-97f0-0c3304970b82',
                        display_type=DisplayTypes.EPIC_INLINE,
                        flavor='Flavor_E'
                    )
                }
            ),
            CollectionNames.EPIC_SHOWCASE_OFFER: Collection(
                collection_id='edt.col.5e70fe48-1ace-47f9-8a69-3d1c621feaac',
                context_ids={
                    DisplayTypes.EPIC_SHOWCASE: Context(
                        root='',
                        canvas='edt.cvs.5e6b04e9-c3f6-4f99-bf1d-64f7e9c4092e',
                        shelf='edt.shelf.5e70ff3f-9ebf-49d7-83b6-3e2e889a7be5',
                        display_type=DisplayTypes.EPIC_SHOWCASE,
                        flavor='Flavor_E'
                    )
                }
            ),
            CollectionNames.SPOTLIGHT_OFFER: Collection(
                collection_id='edt.col.5efa514f-e6af-4cc8-bf1c-c661b488f4a3',
                context_ids={
                    DisplayTypes.SPOTLIGHT: Context(
                        root='',
                        canvas='edt.cvs.5efa4a15-7d8e-4922-ab1e-e850e373b71e',
                        shelf='edt.shelf.5efa4a15-ce1e-4ec6-9324-3162b621433f',
                        display_type=DisplayTypes.SPOTLIGHT,
                    )
                }
            )
        }
    ),
    CanvasNames.ACORN_TV: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='ACorn TV',
        id='tvs.sbd.11000245',
        is_first_party=True
    ),
    CanvasNames.EPIX_MCCORMICK: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Epix',
        id='tvs.sbd.11000065',
        is_first_party=True

    ),
    CanvasNames.PARAMOUNT_PLUS_MCCORMICK: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Paramount',
        id='tvs.sbd.11000241',
        is_first_party=True,
        collection_items={
            'move_to_explore_shelf': Collection(
                collection_id='edt.col.5d0a538c-21ad-488c-9e09-b92b041248b6',
                context_ids={
                    DisplayTypes.NAV_BRICK: Context(
                        canvas='edt.cvs.5d0a7e9f-b85f-4ff8-bd22-964fb0c58a2f',
                        shelf='edt.shelf.5d0a7e9f-8b81-4113-a7b3-a6fc599ae9d6',
                        display_type=DisplayTypes.NAV_BRICK
                    )
                }
            ),
        }
    ),
    CanvasNames.PEACOCK: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.11000507',
        child_ids=['tvs.sbd.11000510'],
        is_first_party=False,
        name='Peacock',
        bundle_id='com.peacocktv.peacock'
    ),
    # MCPeacock channel has to be used for only Plato feature tests.
    # This is a sample channel and have a child parent relationship with Peacock Channel
    CanvasNames.MCPEACOCK: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.11000510',
        parent_id='tvs.sbd.11000507',
        is_first_party=True,
        name='Peacock',
        bundle_id='com.peacocktv.peacock',
        collection_items={
            CollectionNames.CHANNEL_UPSELL_OFFER: Collection(
                collection_id='edt.col.67f6b420-218a-4e92-b9e3-60b835746dec',
                context_ids={
                    DisplayTypes.CHANNEL_UPSELL: Context(
                        root='',
                        canvas='edt.cvs.67f578e5-d425-46fc-8331-75727e21e3c0',
                        shelf='edt.shelf.67f6c14e-e22b-4a83-a3f3-c0986558dac0',
                        display_type=DisplayTypes.CHANNEL_UPSELL
                    )
                }
            ),
            CollectionNames.EPIC_STAGE: Collection(
                collection_id='edt.col.67f578ba-db33-4213-bbc3-ecd1db8a1a82',
                context_ids={
                    DisplayTypes.EPIC_STAGE: Context(
                        root='',
                        canvas='edt.cvs.67f578e5-d425-46fc-8331-75727e21e3c0',
                        shelf='edt.shelf.67f578e5-9c89-415f-83d6-4097f7b1f6ee',
                        display_type=DisplayTypes.EPIC_STAGE
                    )
                }
            )
        }
    ),
    CanvasNames.PLATO_TV_PLUS: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.4000::1481150412_9_2000062287',
        name='TV Plus with Plato subscription',
        is_first_party=True
    ),
    CanvasNames.STARZ_MCCORMICK: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Starz McCormick',
        id='tvs.sbd.11000059',
        is_first_party=True,
    ),
    CanvasNames.PLUTO_TV: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.12442',
        name='Pluto TV',
        is_first_party=False,
        bundle_id='tv.pluto.ios'
    ),
    CanvasNames.NETFLIX: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Netflix',
        id='tvs.sbd.9000',
        is_first_party=False,
        bundle_id='com.netflix.Netflix'
    ),
    CanvasNames.COMEDY_CENTRAL: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Comedy Central',
        id='tvs.sbd.10400',
        is_first_party=False,
        bundle_id='com.mtvn.ccnetwork'
    ),
    CanvasNames.TBS: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='TBS',
        id='tvs.sbd.11221',
        is_first_party=False,
        bundle_id='com.turner.TBS'
    ),
    CanvasNames.AT_T_TV: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='AT&T TV',
        id='tvs.sbd.13701',
        is_first_party=False,
        bundle_id='com.att.dfw'
    ),
    CanvasNames.TV: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Apple TV',
        id='tvs.sbd.3000',
        is_first_party=True,
        bundle_id='com.apple.TVWatchList'
    ),
    CanvasNames.TUBI: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.13160',
        name='Tubi',
        is_first_party=False,
        bundle_id='com.adrise.tubitv'
    ),
    CanvasNames.NOGGIN: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Noggin',
        id='tvs.sbd.11000132',
        is_first_party=True,
        is_enabled_for_editorial_featuring=False
    ),
    CanvasNames.DISCOVERY_PLUS: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='discovery+',
        id='tvs.sbd.11000181',
        is_first_party=False,
        bundle_id='com.discovery.mobile.discoverygo'
    ),
    CanvasNames.LIFETIME_MOVIE_CLUB: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Lifetime Movie Club',
        id='tvs.sbd.11000098',
        is_first_party=True
    ),
    CanvasNames.BET_PLUS_MCCORMICK: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='BET+',
        id='tvs.sbd.11000124',
        is_first_party=True,
    ),
    CanvasNames.PURPLE: Canvas(  # https://quip-apple.com/4laMAYEsfJcn
        canvas_type=CanvasTypes.CHANNEL,
        name='Purple',
        id='tvs.sbd.4300',
        vod_service='tvs.vds.11034079',
        media_content={
            'stereoscopic_movie': direct_access['stereoscopic_movie'],
            'stereoscopic_movie_two': direct_access['stereoscopic_movie_two'],
            'immersive_tv_show': direct_access['immersive_tv_show'],
            'immersive_movie': direct_access['immersive_movie'],
            'immersive_movie_two': direct_access['immersive_movie_two']
        },
        collection_items={
            '3D': Collection(
                collection_id='edt.col.6418ad2c-7234-4147-aade-66bc53cfafc0',
            ),
            'IM': Collection(
                collection_id='edt.col.641a52f1-ba0c-4e49-8fd4-52ec3069d467',
            ),
            '3D_IM': Collection(
                collection_id='edt.col.641a53da-bd40-47ab-80f1-ad3e80c54a45',
            ),
            'Mixed': Collection(
                collection_id='edt.col.641a5467-dad9-4180-87ed-0e630e0d47ad',
            )
        }
    ),
    CanvasNames.MUSIC: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Apple Music',
        id='tvs.sbd.2000',
        is_first_party=True
    ),
    CanvasNames.ITUNES: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.9001',
        is_first_party=True,
        name='iTunes',
        media_content={
            'movie': direct_access['movie_5'],
            'movie_purchased': direct_access['movie_purchased'],
            'show': direct_access['show_4'],
            'show_purchased': direct_access['show_purchased'],
            'episode': direct_access['episode_4'],
            'episode_purchased': direct_access['episode_purchased'],
            'season': direct_access['season_2'],
            'localized_movie': direct_access['localized_movie'],
            'localized_show': direct_access['localized_show'],
            'VOD_episode': direct_access['VOD_episode'],
            'movie_bundle': direct_access['movie_bundle_2'],
            'box_set': direct_access['box_set_2']
        }
    ),
    CanvasNames.DISNEY_PLUS: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.11000111',
        is_first_party=False,
        name='Disney+',
        bundle_id='com.apple.appleevents',
        media_content={
            'movie': direct_access['movie_6'],
            'show': direct_access['show_5'],
            'episode': direct_access['episode_5']
        }
    ),
    CanvasNames.ESPN: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='ESPN',
        id='tvs.sbd.30061',
        is_first_party=False,
        external_service_id='com.espn.service.linear.espn2',
        bundle_id='com.espn.ScoreCenter',
        media_content={
            'upcoming_sporting_event': direct_access['upcoming_sporting_event_2'],
            'live_sporting_event': direct_access['live_sporting_event_2'],
            'live_sporting_event_on_federated_brand': direct_access['live_sporting_event_on_federated_brand'],
            'live_sporting_event_on_federated_brand_2': direct_access['live_sporting_event_on_federated_brand_2']
        }
    ),
    CanvasNames.MLB_TV: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.1000075',
        is_first_party=False,
        bundle_id='com.mlb.AtBatUniversal',
        name='MLB At Bat',
        media_content={
            'chapman_federated_live_p_at_p': direct_access['chapman_federated_live_p_at_p']
        }
    ),
    CanvasNames.HULU: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Hulu',
        id='tvs.sbd.10000',
        bundle_id='com.hulu.plus',
        external_service_id='com.hulu.plus',
        is_first_party=False,
    ),
    CanvasNames.HBO_GO: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='HBO Go',
        id='tvs.sbd.11000353',
        is_first_party=False,
        bundle_id='com.wbd.stream'
    ),
    CanvasNames.FOX_NOW: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Fox Now',
        id='tvs.sbd.10040',
        is_first_party=False,
        bundle_id='com.fox.now'
    ),
    CanvasNames.CBS_ALL_ACCESS: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='CBS All Access',
        id='tvs.sbd.10120',
        is_first_party=True,
        is_enabled_for_editorial_featuring=False
    ),
    CanvasNames.CBS_SPORTS: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='CBS Sports',
        id='tvs.sbd.1000188',
        bundle_id='H443NM7F8H.CBSSportsApp',
        is_sports_dynamic=True,
    ),
    CanvasNames.FEDERATED_APP_WITHOUT_CANVAS: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Federated App Without Canvas',
        id='tvs.sbd.1000002',
        is_first_party=False,
        is_enabled_for_editorial_featuring=False

    ),
    CanvasNames.FEDERATED_APP_WITHOUT_EDITORIALFEATURING_FLAGS: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Federated App Without editorialFeaturing Flags',
        id='tvs.sbd.10260',
        is_first_party=False,
        is_enabled_for_editorial_featuring=False,
        bundle_id='com.aetn.history.ios.watch'

    ),
    CanvasNames.MCCORMICK_CHANNEL_WITHOUT_EDITORIALFEATURING_FLAGS: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='UP Faith & Family',
        id='tvs.sbd.11000106',
        is_first_party=True,
        is_enabled_for_editorial_featuring=False
    ),
    CanvasNames.AE: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='A&E',
        id='tvs.sbd.10241',
        is_first_party=False,
        bundle_id='com.aetn.aetv.ios.watch'
    ),
    CanvasNames.BRITBOX: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Britbox',
        id='tvs.sbd.1000051',
        is_first_party=False,
        bundle_id='com.britbox.us'
    ),
    CanvasNames.SUNDANCE_NOW: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Sundance Now',
        id='tvs.sbd.10540',
        is_first_party=False,
        bundle_id='com.sundancenow.docclub'
    ),
    CanvasNames.FREEFORM: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Freeform',
        id='tvs.sbd.11860',
        is_first_party=False,
        bundle_id='com.abcfamily.videoplayer'
    ),
    CanvasNames.TNT_EAST: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='TNTEast',
        id='tvs.sbd.11220',
        is_first_party=False,
        bundle_id='com.turner.TNT',
        media_content={
            'nba_live_sporting_event': direct_access['nba_live_sporting_event']
        }
    ),
    CanvasNames.PRIME_VIDEO: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Prime Video',
        id='tvs.sbd.12962',
        is_first_party=False,
        bundle_id='com.amazon.aiv.AIVApp',
        media_content={
            'show': direct_access['show_6']
        }
    ),
    CanvasNames.CHANNEL_CONTAINING_BPP_SHELVES: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Channel containing BPP shelves',
        id='tvs.sbd.11000086',
        is_first_party=True,
        is_enabled_for_editorial_featuring=False,
        expected_shelf_displayType_pairs={
            'edt.col.64d65c7f-3fe8-4215-a742-c6685f4d1332': 'epicStage',
            'tvc.col.12456': 'episodeLockup',
            'tvc.col.11125': 'lockup'
        }
    ),
    CanvasNames.AMC_PLUS_MCC: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='AMC+',
        id='tvs.sbd.11000165',
        is_first_party=True,
        brand_equivalence_id='tvs.eqb.1000000'
    ),
    CanvasNames.AMC_PLUS_FED: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='AMC',
        id='tvs.sbd.11000',
        is_first_party=False,
        brand_equivalence_id='tvs.eqb.1000000',
        bundle_id='com.amctve.amcfullepisodes'
    ),
    CanvasNames.IFC_FILMS: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='IFC Films',
        id='tvs.sbd.11000122',
        is_first_party=False,
        bundle_id='com.apple.TVWatchList'
    ),
    CanvasNames.NBC_SPORTS: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='NBC Sports',
        id='tvs.sbd.1000024',
        is_first_party=False,
        bundle_id='com.nbcuni.com.nbcsports.liveextra',
        media_content={},
    ),
    CanvasNames.TAHOMA_MOVIES: Canvas(
        canvas_type=CanvasTypes.ROOT,
        name='Tahoma Movies',
        id='tahoma_movies',
        displayType_chart_id_startswith='uts.col.ItunesCharts.chart.allMovies'
    ),
    CanvasNames.TAHOMA_TV_SHOWS: Canvas(
        canvas_type=CanvasTypes.ROOT,
        name='Tahoma TV Shows',
        id='tahoma_tvshows',
        displayType_chart_id_startswith='uts.col.ItunesCharts.chart.tvSeasons'
    ),
    CanvasNames.TAHOMA_WATCH_NOW: Canvas(
        canvas_type=CanvasTypes.ROOT,
        name='Watch Now',
        id='tahoma_watchnow',
        shelves_under_test={
            'sports_marker_shelf': {
                'shelf_id': 'edt.shelf.60b97c66-3a95-4d02-83f9-282238e92368',
                'canvas_id': 'edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199'
            }
        },
        collection_items={
            CollectionNames.EPIC_STAGE: Collection(
                collection_id='edt.col.638e4768-9f51-45c9-979c-1b8fd36eee9c',
                context_ids={
                    DisplayTypes.EPIC_STAGE: Context(
                        canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                        shelf='edt.shelf.63583fcf-bbe0-4275-9d93-0a6c77b48b72',
                        display_type=DisplayTypes.EPIC_STAGE,
                        root='tahoma_watchnow'
                    )
                }
            ),
            CollectionNames.DOOR_LOCKUP: Collection(
                collection_id='edt.col.64cafb3f-3267-4df2-b55c-2f79e111a1f5',
                context_ids={
                    DisplayTypes.DOOR_LOCKUP: Context(
                        root='tahoma_watchnow',
                        display_type=DisplayTypes.DOOR_LOCKUP
                    )
                }
            )
        },
        up_next_fallback={
            'up_next_fallback_collection_id': 'edt.col.6388eb62-8138-4aae-9001-01f4b4850e5d',
            'up_next_fallback_category_name': 'uts.category.no_up_next___watch_now'
        },
    ),
    CanvasNames.TAHOMA_SPORTS: Canvas(
        canvas_type=CanvasTypes.ROOT,
        name='Sports',
        id='tahoma_sports'
    ),
    CanvasNames.TAHOMA_STORE: Canvas(
        canvas_type=CanvasTypes.ROOT,
        name='Store',
        id='tahoma_store',
        collection_items={
            CollectionNames.DOOR_LOCKUP: Collection(
                collection_id='edt.col.64cafb3f-3267-4df2-b55c-2f79e111a1f5',
                context_ids={
                    DisplayTypes.DOOR_LOCKUP: Context(
                        root='tahoma_store',
                        display_type=DisplayTypes.DOOR_LOCKUP
                    )
                }
            )
        }
    ),
    CanvasNames.TAHOMA_KIDS: Canvas(
        canvas_type=CanvasTypes.ROOT,
        name='Kids',
        id='tahoma_kids'
    ),
    CanvasNames.TAHOMA_VISION: Canvas(
        canvas_type=CanvasTypes.ROOT,
        name='Vision',
        id='tahoma_vision'
    ),
    CanvasNames.SEO_TEST_ROOM: Canvas(  # Test record set to verify seoTitle and seoDescription
        canvas_type=CanvasTypes.ROOM,
        name='',
        id='edt.item.64120318-281f-4837-819c-50bb9074f443',
    ),
    CanvasNames.CAMPAIGN_TEST_ROOM: Canvas(
        canvas_type=CanvasTypes.ROOM,
        name='',
        id='edt.item.65c58f50-c0c6-4243-98cd-da41d0b0c025'
    ),
    CanvasNames.CANVAS_COHORT_METRICS_ROOM: Canvas(
        canvas_type=CanvasTypes.ROOM,
        name='',
        id='edt.item.65c58f50-c0c6-4243-98cd-da41d0b0c025'
    ),
    CanvasNames.HIDE_ENTITLEMENT_TEST_ROOM: Canvas(
        canvas_type=CanvasTypes.ROOM,
        name='',
        id='edt.item.65de5a63-74b1-4490-b8bc-c0e13b4e71aa',
        collection_items={
            CollectionNames.NOT_DROP_ENTITLED_CHANNELS_FLAG_ON: Collection(
                collection_id='edt.col.6619a201-f0a1-4e2c-b52f-b05c2e37148a'
            ),
            CollectionNames.NOT_DROP_ENTITLED_CHANNELS_FLAG_OFF: Collection(
                collection_id='edt.col.6619a22d-8a10-4751-90f4-6769f03778dc'
            ),
        }
    ),
    CanvasNames.WITH_ONDEMAND_LSE: Canvas(
        canvas_type=CanvasTypes.CANVAS,
        id='edt.cvs.6322223f-45fe-421a-a126-0cd43ff478a6',
        name='Canvas without live sporting events on demand',
        shelves_under_test={
            'sports_extras_epic_inline': {
                'collection_id': 'edt.col.6322213c-9f82-4334-8d54-f5800d7b13c3'
            }
        },
    ),
    CanvasNames.WITHOUT_ONDEMAND_LSE: Canvas(
        canvas_type=CanvasTypes.CANVAS,
        id='edt.cvs.634c3945-a18c-410d-afbc-1847240b42d1',
        name='Canvas without live sporting events on demand',
        shelves_under_test={
            'sports_extras_epic_inline': {
                'collection_id': 'edt.col.6322213c-9f82-4334-8d54-f5800d7b13c3'
            }
        },
    ),
    CanvasNames.MLB_ROOM: Canvas(
        canvas_type=CanvasTypes.ROOM,
        id='edt.item.62327df1-6874-470e-98b2-a5bbeac509a2',
        name='Canvas without live sporting events on demand',
    ),
    CanvasNames.WITH_CHANNEL_HEADER: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='CBS All Access',
        id='tvs.sbd.1000090',
        is_first_party=True
    ),
    CanvasNames.EMPTY_CHANNEL: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='--',
        id='tvs.sbd.6000150',
    ),
    CanvasNames.MCSMITHSONIAN: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='McSmithsonian',
        id='tvs.sbd.7000028'
    ),
    CanvasNames.SHOWS_WITH_BOX_SET_ITEMS_ON_SHELVES: Canvas(
        canvas_type=CanvasTypes.ROOM,
        name='Canvas with box set items on shelves',
        id='edt.cvs.6515ff9c-8e2a-40b4-94af-bf25533e140b',
        media_content={
            'show_with_box_set_item': direct_access['show_with_box_set_item']
        }
    ),
    CanvasNames.SHELVES_WITH_LOCALE_AVAILABILITY: Canvas(
        canvas_type=CanvasTypes.CANVAS,
        id='edt.cvs.664d0f56-9862-4665-b79e-ef8f83cd6e7b',
        name='',
        collection_items={
            CollectionNames.AVAILABLE_FOR_ES_LOCALE: Collection(
                collection_id='edt.col.664d1113-c207-42c0-9f3c-9a10f175fed4'
            )
        }
    ),
    # content setup: https://quip-apple.com/LXvvAWvX4xD5
    CanvasNames.CANVAS_WITH_SPORTS_TEAMS_SHELVES: Canvas(
        canvas_type=CanvasTypes.CANVAS,
        id='edt.cvs.631bd6a1-9074-409e-a3f7-35620da139c8',
        name='',
        collection_items={
            CollectionNames.BRICK_WITH_SPORT_TEAMS: Collection(
                collection_id='edt.col.639b5d19-6bab-4829-8ae8-81ef9e14268d',
                context_ids={
                    DisplayTypes.BRICK: Context(
                        canvas='edt.cvs.631bd6a1-9074-409e-a3f7-35620da139c8',
                        shelf='edt.shelf.639b6d21-5513-4c67-8aa0-fe2482e81501',
                        display_type=DisplayTypes.BRICK
                    )
                }
            ),
            CollectionNames.EPICINLINE_WITH_SPORT_TEAMS: Collection(
                collection_id='edt.col.639b5d1b-d41e-4c55-8c93-ab14b08c4f12',
                context_ids={
                    DisplayTypes.EPIC_INLINE: Context(
                        canvas='edt.cvs.631bd6a1-9074-409e-a3f7-35620da139c8',
                        shelf='edt.shelf.639b6d21-a3b8-419b-8876-ee07086d5300',
                        display_type=DisplayTypes.EPIC_INLINE
                    )
                }
            ),
        }
    ),

    CanvasNames.PERSONALIZATION_BLVR_ROOM: Canvas(
        canvas_type=CanvasTypes.CANVAS,
        id='edt.cvs.65ea4f0f-2727-492d-ab9a-de58330a9adc',
        name='',
        collection_items={
            CollectionNames.BLVR_MOVIES_SHOWS_SPORTING_EVENTS: Collection(
                collection_id='edt.col.65ea5568-0473-4151-adbb-ef8795c3cdf8',
                context_ids={
                    DisplayTypes.LOCKUP: Context(
                        canvas='edt.cvs.65ea4f0f-2727-492d-ab9a-de58330a9adc',
                        shelf='edt.shelf.65ea5594-e4e0-407d-9030-44850be71dd5',
                        display_type=DisplayTypes.LOCKUP
                    )
                }
            )
        }
    ),

    CanvasNames.PERSONALIZATION_TEST_ROOM: Canvas(
        canvas_type=CanvasTypes.ROOM,
        id='edt.item.65669543-ea10-41d9-a6ac-047a5aef6bd8',
        name='',
    ),

    CanvasNames.PERSONALIZATION_MODIFIED_SCORE_ROOM: Canvas(
        canvas_type=CanvasTypes.ROOM,
        id='edt.cvs.67072dee-d7b6-4518-8261-30282d16254a',
        name='',
    ),
    CanvasNames.EPIC_STAGE_BRAND_INTENT: Canvas(
        canvas_type=CanvasTypes.ROOM,
        id='edt.item.6621586c-d084-4dac-bb89-1e433ab0ac80',
        name='Brand Intent Room',
        collection_items={
            CollectionNames.EPIC_STAGE_WITH_BRAND_INTENTS: Collection(
                collection_id='edt.col.66214633-9431-41b1-a38e-fc920723d707',
                context_ids={
                    DisplayTypes.EPIC_STAGE: Context(
                        canvas='edt.cvs.6621c83d-2217-4610-a223-014cd0d9626e',
                        shelf='edt.shelf.6621c83d-8499-4088-8e24-e4940f84e2a2',
                        display_type=DisplayTypes.EPIC_STAGE
                    )
                }
            )
        }
    ),

    # Room with collection with display type CategoryBrick and content wrapped EIs with no overriden art.
    # Content setup: https://quip-apple.com/EaJyAsNCJskp
    CanvasNames.CATEGORY_BRICK_ROOM: Canvas(
        canvas_type=CanvasTypes.ROOM,
        id='edt.item.65d50418-2743-4246-9e99-0158e633d573',
        name='UTS CategoryBrick Room',
        collection_items={
            CollectionNames.CATEGORY_BRICK_WITH_ITEMS_WITHOUT_OVERRIDEN_ART: Collection(
                collection_id='edt.col.65d50435-7fc1-4c7e-96a3-25c597c0bde4',
                context_ids={
                    DisplayTypes.CATEGORY_BRICK: Context(
                        canvas='edt.cvs.65d50462-16b2-4dd2-8297-0ae1b4a60eb8',
                        shelf='edt.shelf.65d50462-b85b-4975-8ba7-51706ad12fc4',
                        display_type=DisplayTypes.CATEGORY_BRICK
                    )
                }
            )
        },
        media_content={
            'federated_brand': direct_access['federated_brand'],
            'mccormick_brand': direct_access['mccormick_brand'],
            'movie_bundle': direct_access['movie_bundle_3'],
            'room': direct_access['room']
        }
    ),
    CanvasNames.RICH_HEADERS_ROOM: Canvas(
        canvas_type=CanvasTypes.ROOM,
        id='edt.item.6712d34c-42c1-455f-8c1c-5d4580464130',
        name='Rich Headers Room',
        collection_items={
            CollectionNames.RICH_HEADERS_ROOT_ENTITY: Collection(
                collection_id='edt.col.67181b44-a1ca-4cef-a0d8-b67d25e530ea',
                context_ids={
                    DisplayTypes.LOCKUP: Context(
                        canvas='edt.cvs.6712d37b-77cc-471b-93a0-07371f4975f6',
                        shelf='edt.shelf.67181b7e-29f4-4775-8a99-681db0190622',
                        root='tahoma_watchnow',
                        display_type=DisplayTypes.LOCKUP
                    )
                }
            ),
            CollectionNames.RICH_HEADERS_ROOM_ENTITY: Collection(
                collection_id='edt.col.672e74c0-3935-4d95-ad05-a03438e890bd',
                context_ids={
                    DisplayTypes.LOCKUP: Context(
                        canvas='edt.cvs.6712d37b-77cc-471b-93a0-07371f4975f6',
                        shelf='edt.shelf.672e758c-b598-43ac-a591-8d93f9d4637c',
                        root='tahoma_watchnow',
                        display_type=DisplayTypes.LOCKUP
                    )
                }
            ),
            CollectionNames.RICH_HEADERS_PERSON_ENTITY: Collection(
                collection_id='edt.col.6712d324-a1b3-4039-b975-260b10cac45e',
                context_ids={
                    DisplayTypes.LOCKUP: Context(
                        canvas='edt.cvs.6712d37b-77cc-471b-93a0-07371f4975f6',
                        shelf='edt.shelf.6712d37b-94d7-44b3-9d6a-de5f7169f62e',
                        root='tahoma_watchnow',
                        display_type=DisplayTypes.LOCKUP
                    )
                }
            ),
            CollectionNames.RICH_HEADERS_BRAND_ENTITY: Collection(
                collection_id='edt.col.67169db6-8f59-4576-9cb5-2d190da7598e',
                context_ids={
                    DisplayTypes.LOCKUP: Context(
                        canvas='edt.cvs.6712d37b-77cc-471b-93a0-07371f4975f6',
                        shelf='edt.shelf.67169e2f-5439-4a70-8646-cb80f373173d',
                        root='tahoma_watchnow',
                        display_type=DisplayTypes.LOCKUP
                    )
                }
            ),
            CollectionNames.RICH_HEADERS_CONTENT_ENTITY: Collection(
                collection_id='edt.col.6717e5ef-2bd8-4ba0-883c-cd9f5736c490',
                context_ids={
                    DisplayTypes.LOCKUP: Context(
                        canvas='edt.cvs.6712d37b-77cc-471b-93a0-07371f4975f6',
                        shelf='edt.shelf.6717f12c-2dbf-4e9a-8301-2de7942351fb',
                        root='tahoma_watchnow',
                        display_type=DisplayTypes.LOCKUP
                    )
                }
            )
        }
    ),
    CanvasNames.DISPLAY_TYPES_ROOM: Canvas(
        canvas_type=CanvasTypes.ROOM,
        id='edt.item.664c92dc-e430-4780-bd05-31c7240d5f23',
        name=''
    ),
    CanvasNames.RUNTIME_SPORTS: Canvas(
        canvas_type=CanvasTypes.CANVAS,
        name='Sports',
        id='uts.room.sports-runtime-test'
    ),
    CanvasNames.RUNTIME_TV_PLUS: Canvas(
        canvas_type=CanvasTypes.CANVAS,
        name='TV+',
        id='uts.room.tv-plus-canvas-test'
    ),
    CanvasNames.RUNTIME_KIDS: Canvas(
        canvas_type=CanvasTypes.CANVAS,
        name='Kids',
        id='uts.room.kids-landing-page'
    )
}
