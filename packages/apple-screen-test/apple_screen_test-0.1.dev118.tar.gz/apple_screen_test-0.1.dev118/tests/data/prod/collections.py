from test_data_classes import Collection, Context
from test_data_keys import CollectionNames, DisplayTypes, CanvasNames

COLLECTIONS = {
    CollectionNames.MLS_CHANNEL_UPSELL: Collection(
        collection_id='',
        context_ids={
            DisplayTypes.CHANNEL_UPSELL: Context(
                root='',
                canvas='',
                shelf='',
                display_type=DisplayTypes.CHANNEL_UPSELL
            )
        }
    ),
    CollectionNames.MLS_EPIC_STAGE: Collection(
        collection_id='edt.col.65caaf6c-efbe-4db9-a09a-a50121992a8d',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(
                canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47',
                display_type=DisplayTypes.EPIC_STAGE,
                shelf='edt.shelf.64fa239b-6bcd-466e-8cb0-5ea90d751e02'
            )
        }
    ),
    CollectionNames.SHELF_PAGINATION: Collection(
        collection_id='edt.col.64aee6c5-66b2-4cf9-ac47-fdfdac0bfd27',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                root='',
                canvas='',
                shelf='',
                display_type=DisplayTypes.LOCKUP
            )
        }
    ),
    CollectionNames.SHELF_TRAILERS_WITH_PLAYLIST: Collection(
        collection_id='edt.col.67199bf6-f3bc-4d37-a0a4-d4e5bd28e0d0'
    ),
    CollectionNames.TV_PLUS_BRAND_CHART: Collection(
        collection_id='uts.col.ChartsBlended.tvs.sbd.4000',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                root='',
                canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                shelf='edt.shelf.633f1950-a891-41c6-884d-99c73c880e2a',
                display_type=DisplayTypes.LOCKUP
            ),
            DisplayTypes.CHART: Context(
                display_type=DisplayTypes.CHART,
                root='tahoma_watchnow',
                canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                shelf='edt.shelf.633f1950-a891-41c6-884d-99c73c880e2a',
            )
        }
    ),
    CollectionNames.TV_PLUS_MOVIES_CHART: Collection(
        collection_id='uts.col.ChartsMovies.tvs.sbd.4000',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                root='',
                canvas='edt.cvs.610c550f-938a-46e7-98e3-c573fcd24208',
                shelf='edt.shelf.649e17ea-7079-4fe6-a1e2-acccee44acec',
                display_type=DisplayTypes.LOCKUP
            )
        }
    ),
    CollectionNames.TV_PLUS_GENRE_CHARTS: Collection(
        collection_id='uts.col.PersonalizedGenreCharts.tvs.sbd.4000',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                root='',
                canvas='edt.cvs.610c550f-938a-46e7-98e3-c573fcd24208',
                shelf='edt.shelf.668c5f1c-3948-434c-87ff-b99658e07ac6',
                display_type=DisplayTypes.LOCKUP
            )
        }
    ),
    CollectionNames.MCCORMICK_1_BRAND_CHART: Collection(  # Paramount
        collection_id='uts.col.ChartsBlended.tvs.sbd.1000230',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                root='',
                canvas='edt.cvs.5d0a7e9f-b85f-4ff8-bd22-964fb0c58a2f',
                shelf='edt.shelf.626974a8-5626-4c61-a41a-021fc8af9d0b',
                display_type=DisplayTypes.LOCKUP
            )
        }
    ),
    CollectionNames.MCCORMICK_2_BRAND_CHART: Collection(  # TasteMade
        collection_id='uts.col.ChartsBlended.tvs.sbd.1000211',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                root='',
                canvas='edt.cvs.5c8bdbcb-4236-4607-a42b-4582fede9535',
                shelf='edt.shelf.62697b5c-c5c3-41da-aa49-36c4e5f2aeb2',
                display_type=DisplayTypes.LOCKUP
            )
        }
    ),
    CollectionNames.FEDERATED_APPS_WATCHNOW: Collection(
        # Collection of federated apps that appears in Watch Now ('Streaming Apps')
        collection_id='edt.col.5e154796-60d6-428b-a707-e5d12c65214e',
        context_ids={
            DisplayTypes.BRICK: Context(
                root='tahoma_watchnow',
                canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                shelf='edt.shelf.5e5de493-1975-4b62-ba41-56a4d1438820',
                display_type=DisplayTypes.BRICK
            )
        }
    ),
    # Header override title collections
    CollectionNames.WATCH_NOW_EPIC_STAGE: Collection(
        collection_id='edt.col.638e4768-9f51-45c9-979c-1b8fd36eee9c',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(
                canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                display_type=DisplayTypes.EPIC_STAGE,
                root='tahoma_watchnow',
            )
        }
    ),
    CollectionNames.CHARTS_BLENDED: Collection(
        collection_id='uts.col.ChartsBlended',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                root='',
                canvas='',
                shelf='',
                display_type=DisplayTypes.CHART
            )
        }
    ),
    CollectionNames.FREE_APPLE_TVPLUS_PREMIERES: Collection(
        # Collection of TV+ premieres
        collection_id='edt.col.610c48e4-4375-4bbe-81ce-3ca096a69bf0',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                root='tahoma_watchnow',
                canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                shelf='edt.shelf.621e63bc-32b3-4593-ac96-84b158264ed4',
                display_type=DisplayTypes.LOCKUP
            )
        }
    ),
    CollectionNames.COMING_SOON_ON_APPLE_TV: Collection(
        collection_id='edt.col.612e9de1-a24c-40f8-918a-69e4fbccb955',
        context_ids={
            DisplayTypes.BRICK: Context(
                root='tahoma_watchnow',
                canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                shelf='edt.shelf.62f58f88-1238-4162-9b8e-808c8351b57d',
                display_type=DisplayTypes.BRICK
            )
        }
    ),
    CollectionNames.LOCKUP_WITH_SPORT_TEAMS: Collection(
        collection_id='uts.col.Teams.umc.csl.3c9plmy5skze52ff5ce24mo4g'
    ),
    CollectionNames.DOOR_LOCKUP: Collection(
        collection_id='edt.col.6556a3ca-c6c9-49f7-beca-fb7b492572a0',
        context_ids={
            DisplayTypes.DOOR_LOCKUP: Context(
                canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                display_type=DisplayTypes.DOOR_LOCKUP,
                root='tahoma_watchnow'
            ),
        }
    ),
    CollectionNames.EPIC_SHOWCASE_FLAVOR_F: Collection(
        collection_id='edt.col.67eeca85-aece-4d7a-af48-e380b71f774e',
        context_ids={
            DisplayTypes.EPIC_SHOWCASE_F: Context(
                canvas='edt.cvs.67d8cf6f-d790-4361-bf61-b1670132d769',
                display_type=DisplayTypes.EPIC_SHOWCASE,
                shelf='edt.shelf.67eecb18-8c18-4800-8591-7d007693859f'
            ),
        }
    ),
    CollectionNames.UP_NEXT_LOCKUP: Collection(
        collection_id='uts.col.UpNext',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                shelf='edt.shelf.633dfaf8-80e8-40d0-981a-e9942255f59c',
                display_type=DisplayTypes.LOCKUP
            )
        }
    ),
    CollectionNames.UPSELL_OFFER: Collection(
        collection_id='edt.col.5e3c958f-ba1f-4202-8a5a-91d522b09b94'
    ),
    CollectionNames.MLS_TEAMS_ROW: Collection(
        collection_id='uts.col.Teams.umc.csl.3c9plmy5skze52ff5ce24mo4g',
        context_ids={
            DisplayTypes.TEAM_LOCKUP: Context(display_type=DisplayTypes.TEAM_LOCKUP,
                                              canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47',
                                              shelf='edt.shelf.656542b0-85d2-4718-8763-881e6b47bc3e'
                                              ),
        }
    ),
    CollectionNames.MY_TV_DOOR_LOCKUP_WITH_SECTIONS: Collection(
        collection_id='uts.col.MyTv.edt.col.6556a3ca-c6c9-49f7-beca-fb7b492572a0',
        context_ids={
            DisplayTypes.DOOR_LOCKUP_WITH_SECTIONS: Context(
                canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                display_type=DisplayTypes.DOOR_LOCKUP_WITH_SECTIONS,
                root='tahoma_watchnow'
            ),
        }
    ),
    CollectionNames.EPIC_STAGE_WITH_EXTRA_SHELF: Collection(
        collection_id='edt.col.647fbd6d-0b4f-4ee7-8abb-140abfe0d056',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(
                display_type=DisplayTypes.EPIC_STAGE,
                canvas='edt.cvs.64fa29ca-e723-4b38-ac30-a95826355de4',
                shelf='',
                root=''
            )
        }
    ),
    CollectionNames.PlAY_DEMOTION_MOVIES: Collection(  # This collection has been created by using Collection Template
        collection_id='uts.col.smart-play-demotion-test-movies',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                canvas='',
                shelf='',
                display_type=DisplayTypes.LOCKUP
            )
        }
    ),
    CollectionNames.RIVER_SHELF: Collection(
        collection_id='edt.col.5e62c42d-2ccb-4cae-b708-fa5a2ba0da84',
        context_ids={
            DisplayTypes.RIVER: Context(
                canvas='',
                shelf='',
                display_type=DisplayTypes.RIVER
            )
        }
    ),
    CollectionNames.MLS_ARTWORK_AUTOMATION_SPORTS_CARD_LOCKUP_LIVE_SPORTING_EVENTS: Collection(
        collection_id='edt.col.63c997d6-da28-4b26-a2ed-3cc56985a063',
        context_ids={
            DisplayTypes.SPORTS_CARD_LOCKUP: Context(
                canvas='edt.cvs.63c99e63-1594-4138-b39c-0a3618dcec08',
                shelf='edt.shelf.63c99e63-de2b-47c6-8dc6-c01467059bfc',
                display_type=DisplayTypes.SPORTS_CARD_LOCKUP
            )
        }
    ),
    CollectionNames.MLS_ARTWORK_AUTOMATION_EPIC_STAGE_VOD_SPORTING_EVENTS: Collection(
        collection_id='edt.col.63c9968b-7ff2-4b03-914e-a066dd9542c0',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(
                canvas='edt.cvs.63c9a15e-2408-43f4-bb96-10caa85569d4',
                shelf='edt.shelf.63c9a15e-c098-49fc-92a8-4a3eccbf2429',
                display_type=DisplayTypes.EPIC_STAGE
            )
        }
    ),
    CollectionNames.MLS_ARTWORK_AUTOMATION_SPORTS_CARD_LOCKUP_VOD_SPORTING_EVENTS: Collection(
        collection_id='edt.col.63c997d6-40df-455f-af5b-5c3e9ffa043e',
        context_ids={
            DisplayTypes.SPORTS_CARD_LOCKUP: Context(
                canvas='edt.cvs.63c9a15e-2408-43f4-bb96-10caa85569d4',
                shelf='edt.shelf.63c9a15e-1c43-4263-9c9a-9463bfd152ca',
                display_type=DisplayTypes.SPORTS_CARD_LOCKUP
            )
        }
    ),
    CollectionNames.PAGINATED_GAME_SCHEDULE_LOCKUP_LEAGUE: Collection(
        collection_id='edt.col.657366fa-ced6-42a6-a5b5-b529f1212f90',
        context_ids={
            DisplayTypes.GAME_SCHEDULE_LOCKUP: Context(
                display_type=DisplayTypes.GAME_SCHEDULE_LOCKUP,
                canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47',
                shelf='edt.shelf.65bacc53-cdaa-46cd-9216-7a36a2dee56c'
            )
        }
    ),
    CollectionNames.CHART_COLLECTION_WITH_BOX_SETS: Collection(
        collection_id='uts.col.ItunesCharts.chart.tvSeasons32',
        context_ids={
            DisplayTypes.CHART: Context(display_type=DisplayTypes.CHART,
                                        canvas='edt.cvs.64fa29ca-e723-4b38-ac30-a95826355de4',
                                        shelf='umc.cmc.73b64pvznxmnytk5fqm82kv5l',
                                        root=''
                                        )
        },
    ),
    CollectionNames.MOVIE_BUNDLES_COLLECTION: Collection(
        collection_id='edt.col.620183a8-c847-4a71-8ca2-94eb7232c6f4',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                display_type=DisplayTypes.LOCKUP
            )
        }
    ),
    CollectionNames.DISPLAY_TYPE_TEST: Collection(
        collection_id='edt.col.602fe201-dfd8-4e60-a83f-e6c28d6fecb7'
    ),
    CollectionNames.WHAT_TO_WATCH_SHELF: Collection(
        collection_id='edt.col.5c6fac13-1d1e-467a-aa26-ebf632a4b64c',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                shelf='edt.shelf.63583fcf-197a-4be5-8842-c8911700ffb0',
                display_type=DisplayTypes.LOCKUP,
                root='tahoma_watchnow'
            )
        }
    ),
    CollectionNames.CHARTS_MOVIES_WEEKLY: Collection(
        collection_id='uts.col.ChartsMoviesWeekly',
        context_ids={
            DisplayTypes.CHART: Context(
                display_type=DisplayTypes.CHART
            )
        }
    ),
    CollectionNames.ENTITLED_TRENDING: Collection(
        collection_id='uts.col.EntitledTrendingUnified'
    ),
    CollectionNames.SHELF_FOR_VISION_PRO: Collection(
        collection_id='edt.col.6695a1d4-085c-48fd-af40-5a8686f68b53',
        context_ids={
            DisplayTypes.EPIC_SHOWCASE: Context(
                canvas='edt.cvs.669598e7-711c-4e7a-b371-d047df6f42fc',
                shelf='edt.shelf.669598e7-ae83-4a70-bffe-3b6b8236d96e',
                display_type=DisplayTypes.EPIC_SHOWCASE,
            )
        }
    ),
    CollectionNames.SHELF_EPIC_SHOWCASE_MIXED: Collection(
        collection_id='edt.col.61d746a9-ab0c-44b5-ba01-50f1cf06aed4',
        context_ids={
            DisplayTypes.EPIC_SHOWCASE: Context(
                canvas='edt.cvs.61d76a14-2069-4dff-9249-04bf6611eb43',
                shelf='edt.shelf.61d76a14-ed2f-491b-8b96-42abf8cacc63',
                display_type=DisplayTypes.EPIC_SHOWCASE,
            )
        }
    ),

    CollectionNames.SHELF_WITH_SPORTING_EVENTS: Collection(
        collection_id='edt.col.6754a13a-c8e1-4a44-b2ea-0f257d32b815',
        context_ids={
            DisplayTypes.GAME_SCHEDULE_LOCKUP: Context(
                canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47',
                shelf='edt.shelf.66c8ce4b-897e-48e9-b42c-9b1b9ce6caea',
                display_type=DisplayTypes.GAME_SCHEDULE_LOCKUP,
            )
        }
    ),
    CollectionNames.TRAILERS_SHELF: Collection(
        collection_id='edt.col.66b28542-d08c-4b76-8b51-dd70f8772847'
    ),
    CollectionNames.RICH_HEADER_AND_EI_WRAPPER_MLS: Collection(
        collection_id='edt.col.67914ee7-22ae-4658-8595-051e1c9eb157',
        context_ids={
            DisplayTypes.ENHANCED_LOCKUP: Context(
                canvas='edt.cvs.679184ec-196d-415c-878b-f2f53ee6808a',
                shelf='edt.shelf.679184ec-b12d-4595-8d02-3c7953314e26',
                display_type=DisplayTypes.ENHANCED_LOCKUP
            )
        }
    ),
    CollectionNames.RICH_HEADER_AND_EI_WRAPPER_MOVIES: Collection(
        collection_id='edt.col.67903889-de8b-46f8-bab0-d4043d92656c',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                canvas='edt.cvs.679184ec-196d-415c-878b-f2f53ee6808a',
                shelf='edt.shelf.679184ec-b2f2-4b66-a464-67f718c8af9e',
                display_type=DisplayTypes.LOCKUP
            )
        }
    ),
    CollectionNames.OPAL_SHELF_LOCKUP: Collection(
        collection_id='edt.col.644954a1-df68-4829-a355-8b29a0b9ac32',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                shelf='edt.shelf.644ade1d-5931-4d42-a2e9-965128378387',
                display_type=DisplayTypes.LOCKUP,
                root='tahoma_watchnow'
            )
        }
    ),
    CollectionNames.OPAL_SHELF_CHARTS: Collection(
        collection_id='uts.col.ChartsBlended.tvs.sbd.4000',
        context_ids={
            DisplayTypes.CHART: Context(
                canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                shelf='edt.shelf.633f1950-a891-41c6-884d-99c73c880e2a',
                display_type=DisplayTypes.CHART,
                root='tahoma_watchnow'
            )
        }
    ),
    CollectionNames.BONUS_ON_PRODUCT_PAGE: Collection(
        # Morning show has bonus items with AppleTV+ availability
        collection_id='uts.col.BonusContent.umc.cmc.vtoh0mn0xn7t3c643xqonfzy',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                display_type=DisplayTypes.LOCKUP,
                shelf='',
                canvas=''
            )
        }
    ),
    CollectionNames.PERSONALIZED_LIVE_SPORTS: Collection(
        collection_id='uts.col.PersonalizedLiveSports',
        context_ids={
            DisplayTypes.SPORTS_CARD_LOCKUP: Context(
                canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199id',
                shelf='edt.shelf.60b97c66-3a95-4d02-83f9-282238e92368',
                display_type=DisplayTypes.SPORTS_CARD_LOCKUP,
                root='tahoma_watchnow'
            )
        }
    ),
    CollectionNames.MLS_TODAY_SHELF: Collection(
        collection_id='uts.col.mlstoday',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47',
                shelf='uts.col.mlstoday',
                display_type=DisplayTypes.LOCKUP,
                brand='tvs.sbd.7000'
            )
        }
    ),
    CollectionNames.F1_MOVIE: Collection(
        collection_id='edt.col.68252351-3c54-429f-ad85-6eaafa283099',
    ),
    CollectionNames.F1_TRAILERS: Collection(
        collection_id='edt.col.682636c1-f285-4e6a-a6f1-750d56b92ebd',
    ),
    CollectionNames.BROWSE_ON_SEARCH_LANDING: Collection(
        collection_id='edt.col.5f722d40-9d74-4179-b4b9-15bdc0704eef',
        context_ids={
            DisplayTypes.BRICK: Context(
                canvas='edt.cvs.5f7e147a-5c8e-4124-b00a-5efc45e45ccb',
                shelf='edt.shelf.5f7e147a-1d71-4b03-aea8-c6e9c158da54',
                display_type=DisplayTypes.BRICK,
                root='tahoma_searchlanding'
            )
        }
    ),
    CollectionNames.SEARCH_BR_SHELF: Collection(
        collection_id='uts.col.search.BR'
    ),
    CollectionNames.SPORTS_EXTRAS_NOTES_LOCKUP: Collection(
        collection_id='edt.col.65a70af5-f145-41f6-884f-d3f0b996f1ad',
        context_ids={
            DisplayTypes.NOTES_LOCKUP: Context(
                canvas='edt.cvs.63c8395c-18fb-439e-8cfd-d33265690bda',
                shelf='edt.shelf.65e4a73c-3225-4d25-b3aa-57ba7535a87b',
                display_type=DisplayTypes.NOTES_LOCKUP
            ),
        }
    ),
    CollectionNames.WATCH_LIVE_AMC: Collection(
        collection_id='edt.col.5f5a7a00-a5a3-4c5e-9838-2a79f50e9553?',
        context_ids={
            DisplayTypes.LIVE_SERVICE_LOCKUP: Context(
                canvas='edt.cvs.5f45a1e4-69d9-4d84-bcb6-edb9fec1b7dd',
                shelf='edt.shelf.5f5b8ee7-0e0e-497f-a55b-32ef327dc786',
                brand='tvs.sbd.1000383',
                display_type=DisplayTypes.LIVE_SERVICE_LOCKUP
            )
        }
    ),
    CollectionNames.APPLE_ORIGINALS: Collection(
        collection_id='edt.col.61536b57-aa8c-4c4f-9ff8-b10e73842ae6',
        context_ids={
            DisplayTypes.RIVER: Context(
                display_type=DisplayTypes.RIVER
            )
        }
    ),
    CollectionNames.MLS_PAST_MATCHES: Collection(
        collection_id='edt.col.65d68d2e-f150-427e-8bf6-c2f7ae9f120f',
        context_ids={
            DisplayTypes.SPORTS_CARD_LOCKUP: Context(
                canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47',
                shelf='edt.shelf.6763510c-7baa-46f9-a51f-b4898d40ca53',
                display_type=DisplayTypes.SPORTS_CARD_LOCKUP,
                brand='tvs.sbd.7000'
            )
        }
    )
}
