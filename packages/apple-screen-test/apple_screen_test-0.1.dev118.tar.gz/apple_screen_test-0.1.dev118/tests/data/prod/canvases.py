from data.itms11.direct_access import direct_access
from test_data_classes import Canvas, Collection, Context
from test_data_keys import CanvasNames, CanvasTypes, CollectionNames, DisplayTypes
from locales import *

####################################################################################################
# CANVASES => CHANNEL/ROOTS
####################################################################################################
CANVASES = {
    CanvasNames.TV_PLUS: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.4000',
        is_first_party=True,
        name='AppleTV+',
        external_service_id='com.equus.svod.linear1.US',
        vod_service='',
        salable_adam_id='',
        media_content={
            'movie': direct_access['movie'],
            'licenced_movie': direct_access['licenced_movie'],
            'movie_2': direct_access['movie_2'],
            'movie_with_extra_content': direct_access['movie_with_extra_content'],
            'season': direct_access['season'],
            'show': direct_access['show'],
            'episode': direct_access['episode'],
            'next_episode': direct_access['next_episode'],
            'episode_not_subscribed': direct_access['episode_not_subscribed'],
            'subscribed_episode': direct_access['subscribed_episode'],
            'free_episode': direct_access['free_episode'],
            'live_service': direct_access['live_service'],
            'live_sporting_event': direct_access['live_sporting_event'],
            'japan_exclusive_show': direct_access['japan_exclusive_show'],
            'movie_bundle': direct_access['movie_bundle'],
            'coming_soon_movie': direct_access['coming_soon_movie'],
            'coming_soon_show': direct_access['coming_soon_show'],
            'mlb_VOD_sporting_event': direct_access['mlb_VOD_sporting_event'],
            'flat_show': direct_access['flat_show'],
            'show_tv_plus_ted_lasso': direct_access['show'],
            'episode_tv_plus_ted_lasso_s1e1': direct_access['episode_tv_plus_ted_lasso_s1e1'],
            'box_set': direct_access['box_set']
        },
        collection_items={
            CollectionNames.EPIC_STAGE_WITH_UPSELL: Collection(
                collection_id='edt.col.629e7e8d-14dd-4cc4-ae4a-c9dfddc1844b',
                context_ids={
                    DisplayTypes.EPIC_STAGE_WITH_UPSELL: Context(
                        canvas='edt.cvs.610c550f-938a-46e7-98e3-c573fcd24208',
                        shelf='edt.shelf.62b24ec1-af42-4487-9f2b-ba6201fc11eb',
                        display_type=DisplayTypes.EPIC_STAGE_WITH_UPSELL
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
            CollectionNames.TV_PLUS_EPIC_STAGE: Collection(
                collection_id='uts.col.tv-plus-epic-stage',
                context_ids={
                    DisplayTypes.EPIC_STAGE: Context(
                        canvas='edt.cvs.610c550f-938a-46e7-98e3-c573fcd24208',
                        shelf='edt.shelf.678aa053-1104-45c4-97ce-16a4031b2221',
                        display_type=DisplayTypes.EPIC_STAGE
                    )
                }
            )
        },
        up_next_fallback={
            'up_next_fallback_collection_id': 'edt.col.5f4d6194-f8c7-4f7d-bc9b-dc551f6c8bab',
            'up_next_fallback_category_name': 'uts.category.tv+_free_offer_collection'
        }
    ),
    CanvasNames.MLS: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.7000',
        is_first_party=True,
        name='MLS Season Pass',
        vod_service='',
        salable_adam_id='1481150412,1478184786,6445132388,6445132219,1472441559',
        external_service_id='tvs.sbd.7000:2341680_EN',
        media_content={
            # Available for all signed-in users
            'mls_upcoming_sporting_event_free': direct_access['mls_upcoming_sporting_event_free'],
            'mls_live_sporting_event_free': direct_access['mls_live_sporting_event_free'],
            'mls_VOD_sporting_event_free': direct_access['mls_VOD_sporting_event_free'],

            # Available for tv plus and/or mls subscribed users
            'mls_upcoming_sporting_event_tv_plus': direct_access['mls_upcoming_sporting_event_tv_plus'],
            'mls_live_sporting_event_tv_plus': direct_access['mls_live_sporting_event_tv_plus'],
            'mls_VOD_sporting_event_tv_plus': direct_access['mls_VOD_sporting_event_tv_plus'],

            # Available for mls subscribed users
            'mls_upcoming_sporting_event_mls': direct_access['mls_upcoming_sporting_event_mls'],
            'mls_live_sporting_event_mls': direct_access['mls_live_sporting_event_mls'],
            'mls_VOD_sporting_event_mls': direct_access['mls_VOD_sporting_event_mls'],

            'mls_VOD_campeones_cup_sporting_event_mls': direct_access['mls_VOD_campeones_cup_sporting_event_mls'],

            'sports_extras_lockup_sporting_event_id': direct_access['sports_extras_lockup_sporting_event_id'],

            'mls_live_to_VOD_sporting_event': direct_access['mls_live_to_VOD_sporting_event'],

            'mls_tv_show': direct_access['mls_tv_show'],

            'mls_tv_show_episode': direct_access['mls_tv_show_episode'],
            'mls_360_live_games': direct_access['mls_360_live_games'],
            'mls_360_upcoming_games': direct_access['mls_360_upcoming_games'],
            'mls_360_past_games': direct_access['mls_360_past_games'],

            # MLS games with treatAsShow property
            'mls_live_sporting_event_treat_as_show': direct_access['mls_live_sporting_event_treat_as_show'],
            'mls_upcoming_sporting_event_treat_as_show': direct_access['mls_upcoming_sporting_event_treat_as_show'],
            'mls_VOD_sporting_event_treat_as_show': direct_access['mls_VOD_sporting_event_treat_as_show']

        },
        collection_items={
            CollectionNames.CHANNEL_UPSELL_OFFER: Collection(
                collection_id='edt.col.63bf2052-50b9-44c8-a67e-30e196e19c60',
                context_ids={
                    DisplayTypes.CHANNEL_UPSELL: Context(
                        root='',
                        canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                        shelf='edt.shelf.63d1c3c4-b45f-46c3-a8b1-1044c5d9da09',
                        display_type=DisplayTypes.CHANNEL_UPSELL
                    )
                }
            ),
            CollectionNames.EPIC_INLINE_OFFER: Collection(
                collection_id='',
                context_ids={
                    DisplayTypes.EPIC_INLINE: Context(
                        root='',
                        canvas='',
                        shelf='',
                        display_type=DisplayTypes.EPIC_INLINE,
                        flavor=''
                    )
                }
            ),
            CollectionNames.EPIC_SHOWCASE_OFFER: Collection(
                collection_id='',
                context_ids={
                    DisplayTypes.EPIC_SHOWCASE: Context(
                        root='',
                        canvas='',
                        shelf='',
                        display_type=DisplayTypes.EPIC_SHOWCASE,
                        flavor=''
                    )
                }
            ),
            CollectionNames.SPOTLIGHT_OFFER: Collection(
                collection_id='',
                context_ids={
                    DisplayTypes.SPOTLIGHT: Context(
                        root='',
                        canvas='',
                        shelf='',
                        display_type=DisplayTypes.SPOTLIGHT,
                    )
                }
            ),
            CollectionNames.EPIC_STAGE_WITH_UPSELL: Collection(
                collection_id='edt.col.63b50945-b5c1-42a5-9d15-6500817d78ef',
                context_ids={
                    DisplayTypes.EPIC_STAGE_WITH_UPSELL: Context(
                        canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47',
                        shelf='edt.shelf.64fa239b-6bcd-466e-8cb0-5ea90d751e02',
                        display_type=DisplayTypes.EPIC_STAGE_WITH_UPSELL
                    )
                }
            ),
            CollectionNames.EPIC_STAGE: Collection(
                collection_id='edt.col.63b50945-b5c1-42a5-9d15-6500817d78ef',
                context_ids={
                    DisplayTypes.EPIC_STAGE: Context(
                        canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47',
                        shelf='edt.shelf.64fa239b-6bcd-466e-8cb0-5ea90d751e02',
                        display_type=DisplayTypes.EPIC_STAGE
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
        is_first_party=True,
        name='Chapman League Pass',
        vod_service='',
        salable_adam_id='',
        external_service_id=''
    ),
    CanvasNames.AMETHYST: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.1000539',
        is_first_party=True,
        name='MLS Amethyst Season Pass',
        vod_service='',
        salable_adam_id='',
        external_service_id='',
        media_content={},
        collection_items={}

    ),
    CanvasNames.RED:
        Canvas(
            canvas_type=CanvasTypes.CHANNEL,
            id='tvs.sbd.1000533',
            is_first_party=True,
            name='Apple TV Test Red',
            vod_service='',
            salable_adam_id='',
            external_service_id='',
            media_content={},
            collection_items={}
        ),

    CanvasNames.MUSIC: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.2000',
        is_first_party=True,
        name='Apple Music',
        vod_service='',
        salable_adam_id='',
        external_service_id='',
        media_content={},
        collection_items={}

    ),
    CanvasNames.PARAMOUNT_PLUS_MCCORMICK: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.1000230',
        is_first_party=True,
        name='Paramount',
        vod_service='',
        salable_adam_id='1460219043',
        media_content={
            'movie': direct_access['movie_3'],
            'show': direct_access['show_2'],
            'episode': direct_access['episode_2']
        },
        collection_items={
            'channel_upsell_offer_canvas_id': {},
            'epic_inline_offer_canvas_id': {},
            'epic_showcase_offer_canvas_id': {},
            'spotlight_offer_canvas_id': {},
            'epic_stage_offer_canvas_id': {},
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
    CanvasNames.PARAMOUNT_PLUS_FEDERATED: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.10120',
        name='Paramount+',
        is_first_party=False,
        bundle_id='com.cbsvideo.app'
    ),
    CanvasNames.STARZ_MCCORMICK: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.1000231',
        is_first_party=True,
        name='Starz',
        vod_service='',
        salable_adam_id='',
        media_content={
            'movie': direct_access['movie_4'],
            'show': direct_access['show_3'],
            'episode': direct_access['episode_3'],
            'live_sporting_event': {},
            'upcoming_sporting_event': {}
        },
        collection_items={
            'channel_upsell_offer_canvas_id': {},
            'epic_inline_offer_canvas_id': {},
            'epic_showcase_offer_canvas_id': {},
            'spotlight_offer_canvas_id': {},
            'epic_stage_offer_canvas_id': {},
        }
    ),
    CanvasNames.STARZ_FEDERATED: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.10200',
        name='Starz',
        is_first_party=False,
        bundle_id='com.starz.starzplay'
    ),
    CanvasNames.ITUNES: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.9001',
        is_first_party=True,
        name='iTunes',
        media_content={
            'movie': direct_access['movie_5'],
            'show': direct_access['show_4'],
            'season': direct_access['season_4'],
            'movie_purchased': {},
            'movie_rented': {},
            'episode_purchased': {},
            'show_purchased': {},
            'episode': direct_access['episode_4'],
            'subscribed_episode': direct_access['subscribed_episode_2'],
            'free_episode': direct_access['free_episode_2'],
            'localized_movie': direct_access['localized_movie'],
            'localized_show': direct_access['localized_show'],
            'movie_bundle': direct_access['movie_bundle_2'],
            'box_set': direct_access['box_set']
        }
    ),
    CanvasNames.ESPN: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.30061',
        is_first_party=False,
        name='ESPN',
        external_service_id='com.espn.service.linear.espn2',
        media_content={
            'upcoming_sporting_event': {},  # this event expires
            'live_sporting_event': {},  # this event expires
            'live_services': {
                "ACC Network": "tvs.lvs.1020475",
                "ESPN": "tvs.lvs.30040",
                "ESPN Deportes": "tvs.lvs.30046",
                "ESPN2": "tvs.lvs.30041",
                "ESPNews": "tvs.lvs.30044"
            },
        },

    ),
    CanvasNames.TNT_EAST: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='TNTEast',
        id='tvs.sbd.11220',
        is_first_party=False,
        media_content={
            'nba_live_sporting_event': direct_access['nba_live_sporting_event'],
        }
    ),
    CanvasNames.PRIME_VIDEO: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Prime Video',
        id='tvs.sbd.12962',
        bundle_id='com.amazon.aiv.AIVApp',
        media_content={
            'show': direct_access['show_5'],
        },
        is_first_party=False,
    ),
    CanvasNames.SLING: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.12381',
        name='Sling',
        is_first_party=False,
        bundle_id='com.dishdigital.sling'
    ),
    CanvasNames.PLUTO_TV: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.12442',
        name='Pluto TV',
        is_first_party=False,
        bundle_id='tv.pluto.ios'
    ),
    CanvasNames.TUBI: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.13160',
        name='Tubi',
        is_first_party=False,
        bundle_id='com.adrise.tubitv'
    ),
    CanvasNames.AMAZON_FREEVE: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.1000503',
        name='Amazon Freeve',
        is_first_party=False,
        bundle_id='com.amazon.cosmiccrisp'
    ),
    CanvasNames.TV: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.1000185',
        name='TV',
        is_first_party=True,
        bundle_id='com.apple.TVWatchList'
    ),
    CanvasNames.MGM_PLUS: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.1000272',
        name='MGM+',
        is_first_party=False,
        bundle_id='com.epix.epixnow'
    ),
    CanvasNames.CBS: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.1000452',
        name='CBS',
        is_first_party=False,
        bundle_id='com.cbsbrand.video'
    ),
    CanvasNames.CRUNCHYROLL: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.11160',
        name='Crunchyroll',
        is_first_party=False,
        bundle_id='com.crunchyroll.iphone'
    ),
    CanvasNames.MAX: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.1000566',
        name='MAX',
        is_first_party=False,
        bundle_id='com.wbd.stream'
    ),
    CanvasNames.DISNEY_PLUS: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.1000216',
        name='Disney+',
        is_first_party=False,
        bundle_id='com.disney.disneyplus'
    ),
    CanvasNames.PHILO: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.1000030',
        name='Philo',
        is_first_party=False,
        bundle_id='com.philo.tv.philo',
    ),
    CanvasNames.COOKING_CHANNEL: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Cooking Channel',
        id='tvs.sbd.10304',
        media_content={}
    ),
    CanvasNames.PEACOCK: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.1000371',
        is_first_party=False,
        name='Peacock',
        bundle_id='com.peacocktv.peacock',
        is_sports_dynamic=True,
        media_content={
            'peacock_live_sporting_event': direct_access['peacock_live_sporting_event'],
            'peacock_upcoming_sporting_event': direct_access['peacock_upcoming_sporting_event'],
            'peacock_VOD_sporting_event': direct_access['peacock_VOD_sporting_event'],
        }
    ),
    CanvasNames.NBC_SPORTS: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='NBC Sports',
        id='tvs.sbd.1000024',
        bundle_id='com.nbcuni.com.nbcsports.liveextra',
        is_sports_dynamic=True,
        media_content={
            'nbc_live_sporting_event': direct_access['nbc_live_sporting_event'],
            'nbc_upcoming_sporting_event': direct_access['nbc_upcoming_sporting_event'],
            'nbc_VOD_sporting_event': direct_access['nbc_VOD_sporting_event'],
        },
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
        media_content={
            'cbs_live_sporting_event': direct_access['cbs_live_sporting_event'],
            'cbs_upcoming_sporting_event': direct_access['cbs_upcoming_sporting_event'],
            'cbs_VOD_sporting_event': direct_access['cbs_VOD_sporting_event'],
        },
    ),
    CanvasNames.CNBC: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='CNBC',
        id='tvs.sbd.1000027',
        media_content={},
        is_first_party=False,
        is_enabled_for_editorial_featuring=False,
        bundle_id='com.nbcuni.cnbc.cnbcrtipad'
    ),
    CanvasNames.AMC_PLUS_MCC: Canvas(  # AMC Channel
        canvas_type=CanvasTypes.CHANNEL,
        name='AMC+',
        id='tvs.sbd.1000383',
        is_first_party=True,
        brand_equivalence_id='tvs.eqb.1000000',
        bundle_id='com.apple.TVWatchList'
    ),
    CanvasNames.AMC_PLUS_FED: Canvas(  # AMC app
        canvas_type=CanvasTypes.CHANNEL,
        name='AMC+',
        id='tvs.sbd.1000498',
        is_first_party=False,
        brand_equivalence_id='tvs.eqb.1000000',
        bundle_id='com.amcplus.amcn'
    ),
    CanvasNames.BRITBOX: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Britbox',
        id='tvs.sbd.1000294',
        is_first_party=False,
    ),
    CanvasNames.BET_PLUS_MCCORMICK: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='BET+',
        id='tvs.sbd.1000299',
        is_first_party=True,
    ),
    CanvasNames.HULU: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Hulu',
        id='tvs.sbd.10000',
        is_first_party=False,
        external_service_id='com.hulu.plus',
        bundle_id='com.hulu.plus',
    ),
    CanvasNames.HBO_GO: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='HBO Go',
        id='tvs.sbd.11000353',
        is_first_party=False,
        bundle_id='com.wbd.stream'
    ),

    # Tier 2 Federated US begins
    # https://quip-apple.com/2i2zAwpBDGBt
    CanvasNames.PARAMOUNT_PLUS_TIER2_US: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Paramount+',
        id='tvs.sbd.10120',
        is_first_party=False,
        bundle_id='com.cbsvideo.app',
        locale_info=en_US
    ),
    CanvasNames.ANIMAL_PLANET: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Animal Planet',
        id='tvs.sbd.11580',
        is_first_party=False,
        bundle_id='com.discovery.mobile.aplgo',
        locale_info=en_US
    ),
    # Tier 2 Federated US ends

    # Tier 2 Federated International begins
    CanvasNames.DISNEY_PLUS_TIER2_INTERNATIONAL_1: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Disney+',
        id='tvs.sbd.1000550',
        is_first_party=False,
        bundle_id='com.disneyplus.mea',
        locale_info=ar_SA
    ),
    CanvasNames.DISNEY_PLUS_TIER2_INTERNATIONAL_2: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Disney+',
        id='tvs.sbd.1000216',
        is_first_party=False,
        bundle_id='com.disney.disneyplus',
        locale_info=pl_PL
    ),
    CanvasNames.PARAMOUNT_PLUS_TIER2_INTERNATIONAL: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Paramount+',
        id='tvs.sbd.1000090',
        is_first_party=False,
        bundle_id='com.cbs.canada.app',
        locale_info=en_AU
    ),
    # Tier 2 Federated International ends

    # Tier 3 Federated US begins
    CanvasNames.SCIENCE_CHANNEL: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Science Channel',
        id='tvs.sbd.11582',
        is_first_party=False,
        bundle_id='com.discovery.mobile.scigo',
        locale_info=en_US
    ),
    CanvasNames.CARTOON_NETWORK: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Cartoon Network',
        id='tvs.sbd.11222',
        is_first_party=False,
        bundle_id='com.turner.cnvideoapp',
        locale_info=en_US
    ),
    # Tier 3 Federated US ends

    # Tier 3 Federated International begins
    CanvasNames.DISNEY_PLUS_TIER3_INTERNATIONAL: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Disney+',
        id='tvs.sbd.1000216',
        is_first_party=False,
        bundle_id='com.disney.disneyplus',
        locale_info=sl_SI
    ),
    CanvasNames.CRUNCHYROLL: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        name='Crunchyroll',
        id='tvs.sbd.11160',
        is_first_party=False,
        bundle_id='com.crunchyroll.iphone',
        locale_info=sl_SI
    ),
    # Tier 3 Federated International ends

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
    CanvasNames.TAHOMA_STORE: Canvas(
        canvas_type=CanvasTypes.ROOT,
        name='Tahoma Store',
        id='tahoma_store',
        collection_items={
            CollectionNames.DOOR_LOCKUP: Collection(
                collection_id='edt.col.6556a3ca-c6c9-49f7-beca-fb7b492572a0',
                context_ids={
                    DisplayTypes.DOOR_LOCKUP: Context(
                        root='tahoma_store',
                        display_type=DisplayTypes.DOOR_LOCKUP
                    ),
                    DisplayTypes.DOOR_LOCKUP_WITH_SECTIONS: Context(
                        root='tahoma_store',
                        display_type=DisplayTypes.DOOR_LOCKUP_WITH_SECTIONS
                    )
                }
            ),
        }
    ),
    CanvasNames.TAHOMA_SEARCH_LANDING: Canvas(
        canvas_type=CanvasTypes.ROOT,
        name='Tahoma Search Landing',
        id='tahoma_searchlanding'
    ),
    CanvasNames.TAHOMA_WATCH_NOW: Canvas(
        canvas_type=CanvasTypes.ROOT,
        name='Watch Now',
        id='tahoma_watchnow',
        collection_items={
            CollectionNames.EPIC_STAGE: Collection(
                collection_id='edt.col.638e4768-9f51-45c9-979c-1b8fd36eee9c',
                context_ids={
                    DisplayTypes.EPIC_STAGE: Context(
                        canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                        shelf='edt.shelf.63583fcf-bbe0-4275-9d93-0a6c77b48b72',
                        display_type=DisplayTypes.EPIC_STAGE
                    )
                }
            ),
            CollectionNames.DOOR_LOCKUP: Collection(
                collection_id='edt.col.6556a3ca-c6c9-49f7-beca-fb7b492572a0',
                context_ids={
                    DisplayTypes.DOOR_LOCKUP: Context(
                        root='tahoma_watchnow',
                        display_type=DisplayTypes.DOOR_LOCKUP
                    ),
                    DisplayTypes.DOOR_LOCKUP_WITH_SECTIONS: Context(
                        root='tahoma_watchnow',
                        display_type=DisplayTypes.DOOR_LOCKUP_WITH_SECTIONS
                    )
                }
            )
        },
        up_next_fallback={
            'up_next_fallback_collection_id': 'edt.col.6388eb62-8138-4aae-9001-01f4b4850e5d',
            'up_next_fallback_category_name': 'uts.category.tv+_free_offer_collection'
        },
    ),
    CanvasNames.TAHOMA_SPORTS: Canvas(
        canvas_type=CanvasTypes.ROOT,
        name='Sports',
        id='tahoma_sports'
    ),
    CanvasNames.TAHOMA_KIDS: Canvas(
        canvas_type=CanvasTypes.ROOT,
        name='Kids',
        id='tahoma_kids'
    ),
    CanvasNames.SEO_TEST_ROOM: Canvas(  # Test record set to verify seoTitle and seoDescription
        canvas_type=CanvasTypes.ROOM,
        name='',
        id='edt.item.5f1f15cd-61f4-4114-9b5f-7779ae8407ed',
    ),
    CanvasNames.COMING_TO_APPLE_TV_PLUS: Canvas(
        canvas_type=CanvasTypes.ROOM,
        name='Coming to Apple TV+',
        id='edt.item.62e4314e-8707-4e17-9b77-cdb29787ba94'
    ),
    CanvasNames.MLB_ROOM: Canvas(
        canvas_type=CanvasTypes.ROOM,
        id='edt.item.62327df1-6874-470e-98b2-a5bbeac509a2',
        name='Canvas without live sporting events on demand',
    ),
    CanvasNames.MARCH_MADNESS_LIVE: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.1000042',
        name='March Madness Live'
    ),
    CanvasNames.MLB_AT_BAT: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.1000075',
        is_sports_dynamic=True,
        name='MLB',
        bundle_id='com.mlb.AtBatUniversal',
        media_content={
            'mlb_at_bat_live_sporting_event': direct_access['mlb_at_bat_live_sporting_event'],
            'mlb_at_bat_upcoming_sporting_event': direct_access['mlb_at_bat_upcoming_sporting_event'],
            'mlb_at_bat_VOD_sporting_event': direct_access['mlb_at_bat_VOD_sporting_event'],
        },
    ),
    CanvasNames.GENERIC_SPORT: Canvas(
        canvas_type=CanvasTypes.SPORT,
        id='0',
        name='SPORT'
    ),
    CanvasNames.GENERIC_PERSON: Canvas(
        canvas_type=CanvasTypes.PERSON,
        id='0',
        name='PERSON'
    ),
    CanvasNames.GENERIC_GENRE: Canvas(
        canvas_type=CanvasTypes.GENRE,
        id='0',
        name='GENRE'
    ),
    CanvasNames.GENERIC_TEAM: Canvas(
        canvas_type=CanvasTypes.TEAM,
        id='0',
        name='TEAM'
    ),
    CanvasNames.TELEMUNDO: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.10642',
        name='Telemundo',
        bundle_id='com.nbcuni.telemundo.tve'
    ),
    CanvasNames.HISTORY: Canvas(
        canvas_type=CanvasTypes.CHANNEL,
        id='tvs.sbd.10260',
        name='canvas for a brand without a brand paged',
    ),
    CanvasNames.SHOWS_WITH_BOX_SET_ITEMS_ON_SHELVES: Canvas(
        canvas_type=CanvasTypes.ROOM,
        name='Canvas with box set items on shelves',
        id='edt.cvs.6515ff9c-8e2a-40b4-94af-bf25533e140b',
        media_content={
            'show_with_box_set_item': direct_access['show_with_box_set_item']
        }
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
    ),
    CanvasNames.RENT_FOR_99C_ROOM: Canvas(
        canvas_type=CanvasTypes.ROOM,
        name='Rent for 99 cents',
        id='edt.item.614a451b-9964-44b0-a6d3-69924bc5e81e'
    ),
    CanvasNames.OUTRAGEOUS_COMEDIES_ROOM: Canvas(
        canvas_type=CanvasTypes.ROOM,
        name='Rent for 99 cents',
        id='edt.item.61a6acf2-e9d5-4867-9fe8-64133a83dfb4'
    )
}
