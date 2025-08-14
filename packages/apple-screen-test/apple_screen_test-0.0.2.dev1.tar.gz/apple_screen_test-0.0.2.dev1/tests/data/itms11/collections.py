from test_data_classes import Collection, Context
from test_data_keys import CollectionNames, DisplayTypes, CanvasNames

COLLECTIONS = {
    CollectionNames.PLATO_NOT_SUBSCRIBED_PEACOCK: Collection(
        collection_id='edt.col.68028918-c17c-4e14-a197-0070b897be6d',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                root='tahoma_watchnow',
                canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                shelf='edt.shelf.68028dc7-23c8-47c3-a929-dd5c7a4c68c2',
                display_type=DisplayTypes.LOCKUP

            )
        }
    ),
    CollectionNames.PLATO_SUBSCRIBED_PEACOCK: Collection(
        collection_id='edt.col.6855c69e-d571-4d44-9b89-84300adf93b4',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                root='tahoma_watchnow',
                canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                shelf='edt.shelf.6855c716-b86b-4fd5-84f3-462b872a754d',
                display_type=DisplayTypes.LOCKUP
            )
        }
    ),
    CollectionNames.SAMSUNG_CONTINUE_WATCHING: Collection(
        collection_id='uts.col.samsung-continue-watching',
        context_ids={
            DisplayTypes.CONTINUE_WATCHING: Context(
                display_type=DisplayTypes.CONTINUE_WATCHING
            )
        }
    ),
    CollectionNames.SAMSUNG_CONTINUE_WATCHING_UNSIGNED: Collection(
        collection_id='uts.col.samsung-continue-watching-unsigned',
        context_ids={
            DisplayTypes.CONTINUE_WATCHING: Context(
                display_type=DisplayTypes.CONTINUE_WATCHING
            )
        }
    ),
    CollectionNames.MLS_CHANNEL_UPSELL: Collection(
        collection_id='edt.col.6362aa98-1ad3-4718-a092-9bf6c067bc68',
        context_ids={
            DisplayTypes.CHANNEL_UPSELL: Context(
                root='',
                canvas='edt.cvs.6345cffe-daee-4c5a-93f5-cc1aae41d62d',
                shelf='edt.shelf.6362afd7-5422-46e0-a30c-b835757a28d9',
                display_type=DisplayTypes.CHANNEL_UPSELL
            )
        }
    ),
    CollectionNames.MLS_EPIC_INLINE_FLAVOR_E: Collection(
        collection_id='edt.col.6322220c-f4b0-4169-92a7-a334a8f74a46',
        context_ids={
            DisplayTypes.EPIC_INLINE: Context(
                root='',
                canvas='edt.cvs.6345cffe-daee-4c5a-93f5-cc1aae41d62d',
                shelf='edt.shelf.6362afd7-d35e-480f-a634-0738576ad08a',
                display_type=DisplayTypes.EPIC_INLINE
            )
        }
    ),
    CollectionNames.MLS_EPIC_SHOWCASE_FLAVOR_E: Collection(
        collection_id='edt.col.63222087-e8e8-406c-ace8-b50e224e7492',
        context_ids={
            DisplayTypes.EPIC_SHOWCASE: Context(
                root='',
                canvas='edt.cvs.6345cffe-daee-4c5a-93f5-cc1aae41d62d',
                shelf='edt.shelf.6362afd7-5a41-4660-b717-b3becc631cb0',
                display_type=DisplayTypes.EPIC_SHOWCASE
            )
        }
    ),
    CollectionNames.EPIC_SHOWCASE_WITH_VIDEO: Collection(
        collection_id='edt.col.61a7cbf3-84a5-4a1e-9eff-3c0c2c5a5cb9',
        context_ids={
            DisplayTypes.EPIC_SHOWCASE: Context(
                root='',
                canvas='edt.cvs.61a7cdcc-6919-41df-9b0b-ea97ab820dc6',
                shelf='edt.shelf.61a7cdcc-b048-4d1c-ba74-4b7f8a8f47bd',
                display_type=DisplayTypes.EPIC_SHOWCASE,
            )
        }
    ),
    CollectionNames.MLS_EPIC_STAGE: Collection(
        collection_id='edt.col.6358bfb7-d658-4c88-83f6-03eeb14dba99',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(
                root='',
                canvas='edt.cvs.6345cffe-daee-4c5a-93f5-cc1aae41d62d',
                shelf='edt.shelf.6345cffe-230d-4483-a649-bbbc9d6bcbb0',
                display_type=DisplayTypes.EPIC_STAGE
            )
        }
    ),
    CollectionNames.EPIC_STAGE_EXPLAINABILITY_LINE: Collection(
        collection_id='edt.col.681b8ac9-ae8c-4e19-a633-e553886351b0',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(
                root='',
                canvas='edt.cvs.65de5d76-22e2-4260-93bd-6300d9321a60',
                shelf='edt.shelf.681b92eb-4620-4be5-87eb-2da336c6d2f0',
                display_type=DisplayTypes.EPIC_STAGE
            )
        }
    ),

    CollectionNames.MLS_SPOTLIGHT: Collection(
        collection_id='edt.col.63221eaa-4360-469b-b476-a307f91ae762',
        context_ids={
            DisplayTypes.SPOTLIGHT: Context(
                root='',
                canvas='edt.cvs.6345cffe-daee-4c5a-93f5-cc1aae41d62d',
                shelf='edt.shelf.6362afd7-5bff-4c8a-8b52-458774aab627',
                display_type=DisplayTypes.SPOTLIGHT
            )
        }
    ),
    CollectionNames.CIP_MVPD_CHANNEL_UPSELL: Collection(
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
    CollectionNames.CIP_MVPD_SPOTLIGHT: Collection(
        collection_id='edt.col.6489f934-c9db-44a0-b572-4840e1658228',
        context_ids={
            DisplayTypes.SPOTLIGHT: Context(
                root='',
                canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                shelf='edt.shelf.6489f977-da30-450d-83c9-94d63efc5223',
                display_type=DisplayTypes.SPOTLIGHT
            )
        }
    ),
    CollectionNames.CIP_MVPD_EPIC_INLINE_FLAVOR_E: Collection(
        collection_id='edt.col.5ef27581-7923-4d69-80ed-dcb351c1acf6',
        context_ids={
            DisplayTypes.EPIC_INLINE: Context(
                root='',
                canvas='edt.cvs.5d44d57c-3a1a-481c-8911-853f7615bbc4',
                shelf='edt.shelf.5ef27997-1543-4466-9c5e-28097b4f0eaa',
                display_type=DisplayTypes.EPIC_INLINE
            )
        }
    ),
    CollectionNames.CIP_MVPD_EPIC_STAGE: Collection(
        collection_id='edt.col.62292489-5e93-4292-b04f-af0dcefbd039',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(
                root='',
                canvas='edt.cvs.5d44d57c-3a1a-481c-8911-853f7615bbc4',
                shelf='edt.shelf.6270780c-7b56-4228-bada-e5178c488893',
                display_type=DisplayTypes.EPIC_STAGE
            )
        }
    ),
    CollectionNames.SHELF_PAGINATION: Collection(
        collection_id='edt.col.64078739-95f1-402f-ad6b-152e86e1deb3',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                root="",
                canvas="",
                shelf="",
                display_type=DisplayTypes.LOCKUP
            )
        }
    ),
    CollectionNames.SPORTS_EXTRAS_HAND_PICKED: Collection(
        collection_id='edt.col.63e532dc-dcc1-422c-9c1f-4754c2811644'
    ),
    CollectionNames.SPORTS_EXTRAS_QUERY_ONE: Collection(
        collection_id='edt.col.63e530a8-b9ff-449c-87d0-bc2a7bdfb08a'
    ),
    CollectionNames.SPORTS_EXTRAS_QUERY_TWO: Collection(
        collection_id='edt.col.63e531f9-2187-4407-a7a3-0636405bebcb'
    ),
    CollectionNames.SPORTS_EXTRAS_NOTES_LOCKUP: Collection(
        collection_id='edt.col.66058591-3690-4252-80b9-e4579a4d60e0',
        context_ids={
            DisplayTypes.NOTES_LOCKUP: Context(
                canvas='edt.cvs.66063223-61a5-4305-9e5e-e22bcc7efd7c',
                shelf='edt.col.66058591-3690-4252-80b9-e4579a4d60e0',
                display_type=DisplayTypes.NOTES_LOCKUP
            ),
        }
    ),
    CollectionNames.SPORTS_EXTRAS_LOCKUP: Collection(
        collection_id='edt.col.639923a9-0e66-4bdb-8996-f93d92d9ee04',
        context_ids={
            DisplayTypes.SPORTS_EXTRAS_LOCKUP: Context(
                canvas='edt.cvs.631bd6a1-9074-409e-a3f7-35620da139c8',
                shelf='edt.shelf.644ff1af-8caa-47ca-a08d-fe6ecccb752a',
                display_type=DisplayTypes.SPORTS_EXTRAS_LOCKUP
            ),
        }
    ),
    CollectionNames.SPORTS_EXTRAS_EPIC_INLINE_A: Collection(
        collection_id='edt.col.66024186-6f18-4ddd-899a-36f9d170c168',
        context_ids={
            DisplayTypes.EPIC_INLINE_A: Context(
                canvas='edt.cvs.66063223-61a5-4305-9e5e-e22bcc7efd7c',
                shelf='edt.col.66024186-6f18-4ddd-899a-36f9d170c168',
                display_type=DisplayTypes.EPIC_INLINE_A
            ),
        }
    ),
    CollectionNames.SPORTS_EXTRAS_EPIC_INLINE_B: Collection(
        collection_id='edt.col.6602c6cf-9045-4df7-ad5c-2687aad367bb',
        context_ids={
            DisplayTypes.EPIC_INLINE_B: Context(
                canvas='edt.cvs.66063223-61a5-4305-9e5e-e22bcc7efd7c',
                shelf='edt.col.6602c6cf-9045-4df7-ad5c-2687aad367bb',
                display_type=DisplayTypes.EPIC_INLINE_B
            ),
        }
    ),
    CollectionNames.SPORTS_EXTRAS_EPIC_INLINE_C: Collection(
        collection_id='edt.col.6602c701-3211-4e8a-b348-79f4b5b2e95e',
        context_ids={
            DisplayTypes.EPIC_INLINE_C: Context(
                canvas='edt.cvs.66063223-61a5-4305-9e5e-e22bcc7efd7c',
                shelf='edt.col.6602c701-3211-4e8a-b348-79f4b5b2e95e',
                display_type=DisplayTypes.EPIC_INLINE_C
            ),
        }
    ),
    CollectionNames.SPORTS_EXTRAS_EPIC_INLINE_D: Collection(
        collection_id='edt.col.6602c714-b610-4c82-b4df-868c8f113827',
        context_ids={
            DisplayTypes.EPIC_INLINE_D: Context(
                canvas='edt.cvs.66063223-61a5-4305-9e5e-e22bcc7efd7c',
                shelf='edt.col.6602c714-b610-4c82-b4df-868c8f113827',
                display_type=DisplayTypes.EPIC_INLINE_D
            ),
        }
    ),
    CollectionNames.SPORTS_EXTRAS_EPIC_INLINE_E: Collection(
        collection_id='edt.col.6602c6e6-38c2-4a11-a36a-14f6b8e6ad2c',
        context_ids={
            DisplayTypes.EPIC_INLINE_E: Context(
                canvas='edt.cvs.66063223-61a5-4305-9e5e-e22bcc7efd7c',
                shelf='edt.col.6602c6e6-38c2-4a11-a36a-14f6b8e6ad2c',
                display_type=DisplayTypes.EPIC_INLINE_E
            ),
        }
    ),
    CollectionNames.MLS_ARTWORK_AUTOMATION_EPIC_STAGE_UPCOMING_SPORTING_EVENTS: Collection(
        collection_id='edt.col.63c99653-9689-4f26-b592-de8b9d1c3f3e',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(
                canvas='edt.cvs.63c71574-9402-44b2-b8c3-7ab72025e8da',
                shelf='edt.shelf.63c71574-8cef-4dd6-9815-9923864d09b6',
                display_type=DisplayTypes.EPIC_STAGE
            )
        }
    ),
    CollectionNames.MLS_ARTWORK_AUTOMATION_SPORTS_CARD_LOCKUP_UPCOMING_SPORTING_EVENTS: Collection(
        collection_id='edt.col.63c997d6-513e-4d98-bb52-20c5f4213bf1',
        context_ids={
            DisplayTypes.SPORTS_CARD_LOCKUP: Context(
                canvas='edt.cvs.63c71574-9402-44b2-b8c3-7ab72025e8da',
                shelf='edt.shelf.63c71574-754f-4747-a87f-81f5be70ac94',
                display_type=DisplayTypes.SPORTS_CARD_LOCKUP
            ),
        }
    ),
    CollectionNames.MLS_ARTWORK_AUTOMATION_EPIC_STAGE_LIVE_SPORTING_EVENTS: Collection(
        collection_id='edt.col.63c9966c-9e83-4187-a4e0-777c2539e37d',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(
                canvas='edt.cvs.63c99e63-1594-4138-b39c-0a3618dcec08',
                shelf='edt.shelf.63c99e63-24a0-4ca8-a2c8-5a602511007a',
                display_type=DisplayTypes.EPIC_STAGE
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
        collection_id='edt.col.649b5538-0331-4cae-9a27-285533573bf9',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(
                canvas='edt.cvs.5c3e5498-c234-47fa-830c-5569cee560d8',
                shelf='edt.shelf.635b02ee-acc8-4f32-be68-32a26e879394',
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
    CollectionNames.EPIC_STAGE: Collection(
        collection_id='edt.col.62292489-5e93-4292-b04f-af0dcefbd039',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(
                canvas='edt.cvs.5d44d57c-3a1a-481c-8911-853f7615bbc4',
                shelf='edt.shelf.6270780c-7b56-4228-bada-e5178c488893',
                display_type=DisplayTypes.EPIC_STAGE
            ),
            DisplayTypes.EPIC_STAGE_WITH_UPSELL: Context(
                canvas='edt.cvs.5d44d57c-3a1a-481c-8911-853f7615bbc4',
                shelf='edt.shelf.6270780c-7b56-4228-bada-e5178c488893',
                display_type=DisplayTypes.EPIC_STAGE_WITH_UPSELL
            )

        }
    ),
    CollectionNames.CAPABILITY_FLAG_SHELF_ITEM_SUPPORT: Collection(
        collection_id='edt.col.67a2b1f7-6b25-4862-91dd-7b2cf5c8c10f',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(
                canvas='edt.cvs.67a2b615-e959-425f-9ef5-c02a90664852',
                shelf='edt.col.67a2b1f7-6b25-4862-91dd-7b2cf5c8c10f',
                display_type=DisplayTypes.EPIC_STAGE
            )
        },
        items=['umc.cmc.4w3bwphe4llkud3itjiaipfis']  # capability flag programmed on shelf item
    ),
    CollectionNames.CAPABILITY_FLAG_SHELF_ITEM_ART_SUPPORT: Collection(
        collection_id='edt.col.67a2b647-98e8-4d19-87f6-742ff4b5d732',
        context_ids={
            DisplayTypes.BRICK: Context(
                canvas='edt.cvs.67a2b615-e959-425f-9ef5-c02a90664852',
                shelf='edt.col.67a2b647-98e8-4d19-87f6-742ff4b5d732',
                display_type=DisplayTypes.BRICK
            )
        },
        items=['edt.item.67a2b528-b086-4387-ab63-2d79f1a73f46']  # capability flag programmed on shelf item art
    ),
    CollectionNames.EPIC_STAGE_WITH_NO_BRAND_ASSOCIATION: Collection(
        collection_id='edt.col.62fd7c31-89ec-4263-9002-7744b2edfdad',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(
                canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                shelf='edt.shelf.62fe8e5c-b3cf-4125-b5d9-d3989dc2e54b',
                display_type=DisplayTypes.EPIC_STAGE
            )
        }
    ),
    CollectionNames.EPIC_STAGE_WITH_NEW_ENTITIES: Collection(
        collection_id='edt.col.64dfdcff-5bec-4e4f-b19f-48b490fe0aeb',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(
                canvas='edt.cvs.64de62b9-4b8a-4fc3-b92f-dce104c09328',
                shelf='edt.shelf.64de62b9-ffd5-4e1d-8ecb-3ad0a27a9fc1',
                display_type=DisplayTypes.EPIC_STAGE
            )
        }
    ),
    CollectionNames.LOCKUP: Collection(
        collection_id='edt.col.641b3d6d-08b8-4659-9c24-b2166ae4e09a',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                root='',
                canvas='edt.cvs.64149657-6098-45ca-965e-b5f7ac3e0424',
                shelf='edt.shelf.64149657-76e4-4dad-b961-28665da8dd5c',
                display_type=DisplayTypes.LOCKUP
            )
        }
    ),
    CollectionNames.GRID_LOCKUP: Collection(
        collection_id='edt.col.641b75ac-74d7-42b2-8e00-5f5e7ada060b',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                root='',
                canvas='edt.cvs.64149657-6098-45ca-965e-b5f7ac3e0424',
                shelf='edt.shelf.641b761d-3375-4d6e-b0e1-bb8665ff61e6',
                display_type=DisplayTypes.LOCKUP
            )
        }
    ),
    CollectionNames.EPISODE_LOCKUP: Collection(
        collection_id='edt.col.641cb3f4-5bbe-4d88-93e8-4da9eb516e0d',
        context_ids={
            DisplayTypes.EPISODE_LOCKUP: Context(
                root='',
                canvas='edt.cvs.64149657-6098-45ca-965e-b5f7ac3e0424',
                shelf='edt.shelf.641cb5ac-9547-46a1-a8e1-d8aa835f4edc',
                display_type=DisplayTypes.EPISODE_LOCKUP
            )
        }
    ),
    CollectionNames.SEASON_LOCKUP: Collection(
        collection_id='edt.col.641cb411-6d4c-430a-a050-43ffbe2d1d39',
        context_ids={
            DisplayTypes.SEASON_LOCKUP: Context(
                root='',
                canvas='edt.cvs.64149657-6098-45ca-965e-b5f7ac3e0424',
                shelf='edt.shelf.641cb5ac-29a3-40c3-a315-0013a00cd25f',
                display_type=DisplayTypes.SEASON_LOCKUP
            )
        }
    ),
    CollectionNames.SPORTS_LOCKUP: Collection(
        collection_id='edt.col.641cb465-bcfa-4be1-8d0b-53367f7c4abf',
        context_ids={
            DisplayTypes.SPORTS_LOCKUP: Context(
                root='',
                canvas='edt.cvs.64149657-6098-45ca-965e-b5f7ac3e0424',
                shelf='edt.shelf.641cb5ac-8c29-42bb-95f6-664d97fb27dc',
                display_type=DisplayTypes.SPORTS_CARD_LOCKUP
            )
        }
    ),
    CollectionNames.SPORTS_MASTER_LOCKUP: Collection(
        collection_id='edt.col.641cb489-88a2-45a2-875e-b0f450e761dd',
        context_ids={
            DisplayTypes.SPORTS_MASTER_LOCKUP: Context(
                root='',
                canvas='edt.cvs.64149657-6098-45ca-965e-b5f7ac3e0424',
                shelf='edt.shelf.641cb5ac-f0c7-4e16-ba9c-ffaffb94335d',
                display_type=DisplayTypes.SPORTS_MASTER_LOCKUP
            )
        }
    ),
    CollectionNames.SPORTS_CARD_LOCKUP: Collection(
        collection_id='uts.col.PersonalizedLiveSports'
    ),
    CollectionNames.NOTES_LOCKUP: Collection(
        collection_id='edt.col.641cc9f1-f987-4836-8708-fccc733afe03',
        context_ids={
            DisplayTypes.NOTES_LOCKUP: Context(
                root='',
                canvas='edt.cvs.64149657-6098-45ca-965e-b5f7ac3e0424',
                shelf='edt.shelf.641cff80-ca0e-41f0-94b9-1abb4dc0b8bd',
                display_type=DisplayTypes.NOTES_LOCKUP
            )
        }
    ),
    CollectionNames.PERSON_LOCKUP: Collection(
        collection_id='edt.col.641cccea-fe5b-479e-925d-97c8ff142d7c',
        context_ids={
            DisplayTypes.PERSON_LOCKUP: Context(
                root='',
                canvas='edt.cvs.64149657-6098-45ca-965e-b5f7ac3e0424',
                shelf='edt.shelf.641cff80-fab1-4a0e-aec5-fbd0a1c17f60',
                display_type=DisplayTypes.PERSON_LOCKUP
            )
        }
    ),
    CollectionNames.BRICK: Collection(
        collection_id='edt.col.641de54b-0360-43ec-88d2-b321d736c28f',
        context_ids={
            DisplayTypes.BRICK: Context(
                root='tahoma_watchnow',
                canvas='edt.cvs.64149657-6098-45ca-965e-b5f7ac3e0424',
                shelf='edt.shelf.641df271-705a-482f-aefc-ef5f259e476b',
                display_type=DisplayTypes.BRICK
            )
        }
    ),
    CollectionNames.CHANNEL_LOCKUP: Collection(
        collection_id='edt.col.641ccf1f-25ea-4dea-9297-e6effcc9908c',
        context_ids={
            DisplayTypes.CHANNEL_LOCKUP: Context(
                root='',
                canvas='edt.cvs.64149657-6098-45ca-965e-b5f7ac3e0424',
                shelf='edt.shelf.641cff80-2a27-430c-8111-ee0b97b97354',
                display_type=DisplayTypes.CHANNEL_LOCKUP
            )
        }
    ),
    CollectionNames.BRAND_LOCKUP: Collection(
        collection_id='edt.col.641d029f-7bb0-4503-8730-e359f93352ac',
        context_ids={
            DisplayTypes.BRAND_LOCKUP: Context(
                root='',
                canvas='edt.cvs.64149657-6098-45ca-965e-b5f7ac3e0424',
                shelf='edt.shelf.641d02f8-ee23-4b24-af55-8eec82cdf81f',
                display_type=DisplayTypes.BRAND_LOCKUP
            )
        }
    ),
    CollectionNames.NAV_BRICK: Collection(
        collection_id='edt.col.5ef2354d-1e8b-46dd-8562-d0af0f9915eb'
    ),
    CollectionNames.NAV_BRICK_ART_ONLY: Collection(
        collection_id='edt.col.6421e6ca-d4a1-4559-bec8-e76a5522c058',
        context_ids={
            DisplayTypes.NAV_BRICK_ART: Context(
                root='',
                canvas='edt.cvs.64149657-6098-45ca-965e-b5f7ac3e0424',
                shelf='edt.shelf.6421f7f9-20f6-45a3-b850-1b6e99a39e48',
                display_type=DisplayTypes.NAV_BRICK_ART
            )
        }
    ),
    CollectionNames.NAV_BRICK_ART_AND_TEXT: Collection(
        collection_id='edt.col.6421e6d4-13bb-4d85-b52e-da8e82ca9c8d',
        context_ids={
            DisplayTypes.NAV_BRICK_ART_TEXT: Context(
                root='',
                canvas='edt.cvs.64149657-6098-45ca-965e-b5f7ac3e0424',
                shelf='edt.shelf.6421f7f9-2659-44e9-bdcf-e67641bde700',
                display_type=DisplayTypes.NAV_BRICK_ART_TEXT
            )
        }
    ),
    CollectionNames.CATEGORY_BRICK: Collection(
        collection_id='edt.col.6424bf61-0a24-4944-93dc-5ce7b440270a',
        context_ids={
            DisplayTypes.CATEGORY_BRICK: Context(
                root='',
                canvas='edt.cvs.64149657-6098-45ca-965e-b5f7ac3e0424',
                shelf='edt.shelf.6424caaf-a36f-43e0-a21a-0140cee8931e',
                display_type=DisplayTypes.CATEGORY_BRICK
            )
        }

    ),
    CollectionNames.SPOTLIGHT: Collection(
        collection_id='edt.col.6425bf43-0ab8-4600-a6a2-26b9d5f332ba',
        context_ids={
            DisplayTypes.SPOTLIGHT: Context(
                root='',
                canvas='edt.cvs.64149657-6098-45ca-965e-b5f7ac3e0424',
                shelf='edt.shelf.6425c43d-db0e-4f58-b528-9cf26984941b',
                display_type=DisplayTypes.SPOTLIGHT
            )
        }
    ),
    CollectionNames.CHANNEL_UPSELL: Collection(
        collection_id='edt.col.6425c284-2a8d-4d9b-9494-21831b89af98',
        context_ids={
            DisplayTypes.CHANNEL_UPSELL: Context(
                root='',
                canvas='edt.cvs.6345cffe-daee-4c5a-93f5-cc1aae41d62d',
                shelf='edt.shelf.6425c43d-9b67-4252-9ed3-3f62270dfda4',
                display_type=DisplayTypes.CHANNEL_UPSELL
            )
        }
    ),
    CollectionNames.EPIC_INLINE_FLAVOR_A: Collection(
        collection_id='edt.col.664d9854-2324-4ce5-9d60-1a26250a978d',
        context_ids={
            DisplayTypes.EPIC_INLINE_A: Context(
                root='',
                canvas='edt.cvs.664c9364-5a9f-4efa-b85f-a67e2f8806de',
                shelf='edt.shelf.6425fb13-8e32-4051-96c7-0110035a7722',
                display_type=DisplayTypes.EPIC_INLINE_A
            )
        }
    ),
    CollectionNames.EPIC_INLINE_FLAVOR_B: Collection(
        collection_id='edt.col.6425cf7f-889d-41df-8b01-de86cc6220c0',
        context_ids={
            DisplayTypes.EPIC_INLINE_B: Context(
                root='',
                canvas='edt.cvs.64149657-6098-45ca-965e-b5f7ac3e0424',
                shelf='edt.shelf.6425fb13-46b9-4b6a-baa9-7a59c65b1faa',
                display_type=DisplayTypes.EPIC_INLINE_B
            )
        }
    ),
    CollectionNames.EPIC_INLINE_FLAVOR_C: Collection(
        collection_id='edt.col.6425e473-cc0f-4c51-80b9-2c2a9264abb9',
        context_ids={
            DisplayTypes.EPIC_INLINE_C: Context(
                root='',
                canvas='edt.cvs.64149657-6098-45ca-965e-b5f7ac3e0424',
                shelf='edt.shelf.6425fb13-7e44-46ae-b9a7-20912d9236a4',
                display_type=DisplayTypes.EPIC_INLINE_C
            )
        }
    ),
    CollectionNames.EPIC_INLINE_FLAVOR_D: Collection(
        collection_id='edt.col.6425e7e3-196f-412c-b8b5-56bd5e5ef867',
        context_ids={
            DisplayTypes.EPIC_INLINE_D: Context(
                root='',
                canvas='edt.cvs.64149657-6098-45ca-965e-b5f7ac3e0424',
                shelf='edt.shelf.6425fb13-df72-4392-81c7-cdaac3d443fd',
                display_type=DisplayTypes.EPIC_INLINE_D
            )
        }
    ),
    CollectionNames.EPIC_INLINE_FLAVOR_E: Collection(
        collection_id='edt.col.6425fa27-bb9a-4367-a5e5-16f380ed98ae',
        context_ids={
            DisplayTypes.EPIC_INLINE_E: Context(
                root='',
                canvas='edt.cvs.64149657-6098-45ca-965e-b5f7ac3e0424',
                shelf='edt.shelf.6425fb13-adf8-49f5-b2f9-4003c3951075',
                display_type=DisplayTypes.EPIC_INLINE_E
            )
        }
    ),
    CollectionNames.EPIC_SHOWCASE_FLAVOR_A: Collection(
        collection_id='edt.col.67b394d5-0abe-40fb-868d-bf1b7e7662e9',
        context_ids={
            DisplayTypes.EPIC_SHOWCASE_A: Context(
                root='',
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67b3962f-220b-48d8-8dfc-a1198adbf810',
                display_type=DisplayTypes.EPIC_SHOWCASE_A
            )
        }
    ),

    CollectionNames.EPIC_SHOWCASE_FLAVOR_B: Collection(
        collection_id='edt.col.67b3969c-1f89-47f6-a769-ecb89bb25aaf',
        context_ids={
            DisplayTypes.EPIC_SHOWCASE_B: Context(
                root='',
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67b39d51-25b5-4a1a-868b-c3954aa7a850',
                display_type=DisplayTypes.EPIC_SHOWCASE_B
            )
        }
    ),
    CollectionNames.EPIC_SHOWCASE_FLAVOR_C: Collection(
        collection_id='edt.col.67b39973-6cf6-40d1-b36d-60ec2f4cfd58',
        context_ids={
            DisplayTypes.EPIC_SHOWCASE_C: Context(
                root='',
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67b39d51-a9f0-4760-9f9b-2889c9e8f79b',
                display_type=DisplayTypes.EPIC_SHOWCASE_C
            )
        }
    ),
    CollectionNames.EPIC_SHOWCASE_FLAVOR_D: Collection(
        collection_id='edt.col.67b39991-4ff7-41f9-a80c-b87b4b417394',
        context_ids={
            DisplayTypes.EPIC_SHOWCASE_D: Context(
                root='',
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67b39d51-42a6-4097-8484-b3e2e26ad1a9',
                display_type=DisplayTypes.EPIC_SHOWCASE_D
            )
        }
    ),
    CollectionNames.EPIC_SHOWCASE_FLAVOR_E: Collection(
        collection_id='edt.col.67bf7447-f140-497d-bb78-20b229a9aaff',
        context_ids={
            DisplayTypes.EPIC_SHOWCASE_E: Context(
                root='',
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67bf74b3-89a5-43a8-af0c-9f70fae56f11',
                display_type=DisplayTypes.EPIC_SHOWCASE_E
            )
        }
    ),
    CollectionNames.EPIC_SHOWCASE_SPORTS_FLAVOR_F: Collection(
        collection_id='edt.col.67dcaa36-31c8-4ed9-ac13-5dbd9d16552d',
        context_ids={
            DisplayTypes.EPIC_SHOWCASE_F: Context(
                root='',
                canvas='edt.cvs.67f5fb9f-f459-47c6-a9f2-b693c7b29d5a',
                shelf='edt.shelf.67dcad89-c7d4-4e35-b830-221776c5c409',
                display_type=DisplayTypes.EPIC_SHOWCASE_F,
            )
        }
    ),
    CollectionNames.EPIC_SHOWCASE_FLAVOR_F: Collection(
        collection_id='edt.col.67dcaa36-31c8-4ed9-ac13-5dbd9d16552d',
        context_ids={
            DisplayTypes.EPIC_SHOWCASE_F: Context(
                root='',
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67dcad89-c7d4-4e35-b830-221776c5c409',
                display_type=DisplayTypes.EPIC_SHOWCASE_F,
            )
        }
    ),
    # Notes Lockup > Epic Showcase F in v90 if shelf has movies and shows only
    CollectionNames.NOTES_LOCKUP_TO_EPIC_SHOWCASE_FLAVOR_F: Collection(
        collection_id='edt.col.67db4c4c-a3d9-4f84-91de-157651df92ca',
        context_ids={
            DisplayTypes.EPIC_SHOWCASE_F: Context(
                root='',
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67dcad89-ab96-46b6-ae7f-b790c9cd8d94',
                display_type=DisplayTypes.EPIC_SHOWCASE_F,
            )
        }
    ),
    # Notes Lockup should  transfer to Epic Showcase F in v90 if shelf has movies and shows only
    CollectionNames.NOTES_LOCKUP_TO_EPIC_SHOWCASE_FLAVOR_F_NOTESLOCKUP_DT: Collection(
        collection_id='edt.col.67db4c4c-a3d9-4f84-91de-157651df92ca',
        context_ids={
            DisplayTypes.NOTES_LOCKUP: Context(
                root='',
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67dcad89-ab96-46b6-ae7f-b790c9cd8d94',
                display_type=DisplayTypes.NOTES_LOCKUP,
            )
        }
    ),
    CollectionNames.TV_PLUS_EPIC_SHOWCASE: Collection(
        collection_id='edt.col.62bcf1fb-05ad-485d-a754-d1773f607fb5',
        context_ids={
            DisplayTypes.EPIC_SHOWCASE: Context(
                canvas='edt.cvs.5d44d57c-3a1a-481c-8911-853f7615bbc4',
                shelf='edt.shelf.62c47517-f179-4192-ab58-748458f5f23d',
                display_type=DisplayTypes.EPIC_SHOWCASE
            )
        }
    ),
    CollectionNames.TV_PLUS_LOCKUP: Collection(
        collection_id='edt.col.62c472d2-d033-4e71-b501-74a0936ed29f',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                canvas='edt.cvs.5d44d57c-3a1a-481c-8911-853f7615bbc4',
                shelf='edt.shelf.62c47517-5c63-4ac9-bec3-9017583ccd73',
                display_type=DisplayTypes.LOCKUP
            )
        }
    ),
    CollectionNames.TV_PLUS_SPORTS_CARD_LOCKUP: Collection(
        collection_id='edt.col.62c472d2-d033-4e71-b501-74a0936ed29f',
        context_ids={
            DisplayTypes.SPORTS_CARD_LOCKUP: Context(
                canvas='edt.cvs.5d44d57c-3a1a-481c-8911-853f7615bbc4',
                shelf='edt.shelf.62c47517-5c63-4ac9-bec3-9017583ccd73',
                display_type=DisplayTypes.SPORTS_CARD_LOCKUP
            )
        }

    ),
    CollectionNames.TV_PLUS_MASTER_LOCKUP: Collection(
        collection_id='edt.col.63447875-9e11-4d31-85de-1e3bf0063397',
        context_ids={
            DisplayTypes.SPORTS_MASTER_LOCKUP: Context(
                canvas='edt.cvs.6345cffe-daee-4c5a-93f5-cc1aae41d62d',
                shelf='edt.shelf.6345cffe-a63d-42a8-86bc-2e062554db2a',
                display_type=DisplayTypes.SPORTS_MASTER_LOCKUP
            )
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
    CollectionNames.TV_PLUS_EPIC_INLINE: Collection(
        collection_id='edt.col.6322213c-9f82-4334-8d54-f5800d7b13c3',
        context_ids={
            DisplayTypes.EPIC_INLINE: Context(
                canvas='edt.cvs.6322223f-45fe-421a-a126-0cd43ff478a6',
                shelf='edt.shelf.6322223f-98ed-4207-8f8d-e17c74f2ecff',
                display_type=DisplayTypes.EPIC_INLINE
            )
        }
    ),
    CollectionNames.FREE_APPLE_TVPLUS_PREMIERES: Collection(
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
    CollectionNames.LOCKUP_WITH_SPORT_TEAMS: Collection(
        collection_id='edt.col.63d85967-6397-465c-ba25-de5fe688f782'
    ),
    CollectionNames.UPSELL_OFFER: Collection(
        collection_id='edt.col.5e3c958f-ba1f-4202-8a5a-91d522b09b94'
    ),
    CollectionNames.RECOMMENDED: Collection(
        collection_id='uts.col.GroupForYou.bb94fb27-bf17-46eb-a2ff-9b68c4beb122'
    ),
    CollectionNames.DOOR_LOCKUP: Collection(
        collection_id='edt.col.64cafb3f-3267-4df2-b55c-2f79e111a1f5',
        context_ids={
            DisplayTypes.DOOR_LOCKUP: Context(
                canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                shelf='edt.shelf.6452b3eb-1397-4e5d-92d5-54caeb3ab731',
                display_type=DisplayTypes.DOOR_LOCKUP,
                root='tahoma_watchnow'
            ),
        },
        items=[  # Canvases.TV_PLUS, MISSING_IMAGE
            CanvasNames.MLS,
            CanvasNames.PRIME_VIDEO,
            CanvasNames.HULU,
            CanvasNames.BRITBOX,
            CanvasNames.STARZ_MCCORMICK,
            CanvasNames.EPIX_MCCORMICK,
            CanvasNames.NOGGIN,
            CanvasNames.SHOWTIME_MCCORMICK,
            CanvasNames.EVERGREEN_MCCORMICK,
            CanvasNames.DISNEY_PLUS,
            CanvasNames.DISCOVERY_PLUS,
            CanvasNames.PARAMOUNT_PLUS_MCCORMICK,
            CanvasNames.FEDERATED_APP_WITHOUT_CANVAS,
            CanvasNames.CHANNEL_CONTAINING_BPP_SHELVES,
            # Canvases.CBS_ALL_ACCESS, MISSING_IMAGE
            CanvasNames.FEDERATED_APP_WITHOUT_EDITORIALFEATURING_FLAGS,
            CanvasNames.MCCORMICK_CHANNEL_WITHOUT_EDITORIALFEATURING_FLAGS,
            CanvasNames.AMC_PLUS_MCC,
            # Canvases.AMC Should be dropped because it's considered a duplicate of AMC+
        ]
    ),
    CollectionNames.MY_TV_DOOR_LOCKUP_WITH_SECTIONS: Collection(
        collection_id='uts.col.MyTv.edt.col.64d55f9c-224a-4ab0-a0bf-bc2661e3e575',
        context_ids={
            DisplayTypes.DOOR_LOCKUP_WITH_SECTIONS: Context(
                canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                shelf='edt.shelf.64d56733-464f-4f07-a931-66de967bee14',
                display_type=DisplayTypes.DOOR_LOCKUP,
                root='tahoma_watchnow'
            ),
        }
    ),
    CollectionNames.LOCKUP_WITH_MOVIES_ONE: Collection(
        collection_id='edt.col.5f4d6194-f8c7-4f7d-bc9b-dc551f6c8bab'
    ),
    CollectionNames.LOCKUP_WITH_MOVIES_TWO: Collection(
        collection_id='edt.col.5e433916-0798-47bb-87ef-6da688aa71f9'
    ),
    CollectionNames.ROOM_BRICK_TAKEOVER: Collection(
        collection_id='edt.col.645d5e5a-1672-4d63-97e9-764c104f6a0f',
        context_ids={
            DisplayTypes.BRICK: Context(
                display_type=DisplayTypes.BRICK
            )
        }
    ),
    CollectionNames.ROOM_BRICK: Collection(
        collection_id='edt.col.644c238b-a0ca-4598-95c4-05e65a61db10',
        context_ids={
            DisplayTypes.BRICK: Context(display_type=DisplayTypes.BRICK,
                                        canvas='edt.cvs.644c24a1-14fa-4a66-9568-5eb08eaf260a',
                                        shelf='edt.shelf.644c24a1-bf0d-495a-9be9-10d9bbe37a4f',
                                        root='tahoma_watchnow'
                                        )
        }
    ),
    CollectionNames.CONTENT_BRICK: Collection(
        collection_id='edt.col.644c3aee-ef5d-429e-81e7-bde2b4f24c65',
        context_ids={
            DisplayTypes.BRICK: Context(display_type=DisplayTypes.BRICK,
                                        canvas='edt.cvs.644c24a1-14fa-4a66-9568-5eb08eaf260a',
                                        shelf='edt.shelf.644c4984-ce38-4536-bbc1-c45ffc8d9149',
                                        root='tahoma_watchnow'
                                        )
        }
    ),
    CollectionNames.EXTERNAL_LINK_BRICK: Collection(
        collection_id='edt.col.644c48e4-a9e5-44c3-aac3-4fd59cf2bed3',
        context_ids={
            DisplayTypes.BRICK: Context(display_type=DisplayTypes.BRICK,
                                        canvas='edt.cvs.644c24a1-14fa-4a66-9568-5eb08eaf260a',
                                        shelf='edt.shelf.644c4984-7095-4cd0-ac11-69bf75055128',
                                        root='tahoma_watchnow'
                                        )
        }
    ),
    CollectionNames.ROOM_SPOTLIGHT: Collection(
        collection_id='edt.col.644c4bb9-a73f-403b-9ccc-212ad77f9a52',
        context_ids={
            DisplayTypes.SPOTLIGHT: Context(display_type=DisplayTypes.SPOTLIGHT,
                                            canvas='edt.cvs.644c24a1-14fa-4a66-9568-5eb08eaf260a',
                                            shelf='edt.shelf.644c4c66-91ae-4a7a-b558-5f80f2a68163',
                                            root='tahoma_watchnow'
                                            )
        }
    ),
    CollectionNames.CONTENT_SPOTLIGHT: Collection(
        collection_id='edt.col.644c4c28-f0bb-4387-be3f-a6d5bfbf3921',
        context_ids={
            DisplayTypes.SPOTLIGHT: Context(display_type=DisplayTypes.SPOTLIGHT,
                                            canvas='edt.cvs.644c24a1-14fa-4a66-9568-5eb08eaf260a',
                                            shelf='edt.shelf.644c4c66-db0f-4a0c-a248-46921a373bb7',
                                            root='tahoma_watchnow'
                                            )
        }
    ),
    CollectionNames.EDITORIAL_VIDEO_CLIP_SHELF: Collection(
        collection_id='edt.col.64b81e2f-6238-4acc-8bea-1bbc06ab01ab',
        context_ids={
            DisplayTypes.BRICK: Context(display_type=DisplayTypes.BRICK,
                                        canvas='edt.cvs.64b81e84-b8ef-4c66-8cf0-59f3309b42c0',
                                        shelf='edt.shelf.64b81e84-d1f7-4604-9c69-74e209750e25',
                                        root='tahoma_watchnow'
                                        )
        }
    ),
    CollectionNames.EPIC_STAGE_MAX_ITEM_VALUE_SET_20: Collection(
        collection_id='edt.col.64dbce48-5a9e-43cb-8a3e-6f6cb5cf36f1',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(display_type=DisplayTypes.EPIC_STAGE,
                                             canvas='edt.cvs.64dbced0-2b21-4ee4-92c5-e47593645038',
                                             shelf='',
                                             root=''
                                             )
        }
    ),
    CollectionNames.EPIC_STAGE_MAX_ITEM_VALUE_SET_30: Collection(
        collection_id='edt.col.64dbd199-85b5-443f-b73c-6cb2d653887f',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(display_type=DisplayTypes.EPIC_STAGE,
                                             canvas='edt.cvs.64dbced0-2b21-4ee4-92c5-e47593645038',
                                             shelf='',
                                             root=''
                                             )
        }
    ),
    CollectionNames.EPIC_STAGE_MAX_ITEM_VALUE_NOT_SET_30: Collection(
        collection_id='edt.col.64dbd1d2-1f1f-4f6a-b350-2d5e9be7df3d',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(display_type=DisplayTypes.EPIC_STAGE,
                                             canvas='edt.cvs.64dbced0-2b21-4ee4-92c5-e47593645038',
                                             shelf='',
                                             root=''
                                             )
        }
    ),
    CollectionNames.EPIC_STAGE_MAX_ITEM_VALUE_NOT_SET_10: Collection(
        collection_id='edt.col.64dbcfce-c29f-4b48-924a-7dafdbb6b91c',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(display_type=DisplayTypes.EPIC_STAGE,
                                             canvas='edt.cvs.64dbced0-2b21-4ee4-92c5-e47593645038',
                                             shelf='',
                                             root=''
                                             )
        }
    ),
    CollectionNames.EPIC_STAGE_HIDE_HERO_DESCRIPTION_FLAG_ON: Collection(
        collection_id='edt.col.64dfdcff-5bec-4e4f-b19f-48b490fe0aeb',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(display_type=DisplayTypes.EPIC_STAGE,
                                             canvas='edt.cvs.64de62b9-4b8a-4fc3-b92f-dce104c09328',
                                             shelf='',
                                             root=''
                                             )
        }
    ),
    CollectionNames.EPIC_STAGE_HIDE_HERO_DESCRIPTION_FLAG_OFF: Collection(
        collection_id='',  # TODO: add collection after setup is ready - rdar://114281578
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(display_type=DisplayTypes.EPIC_STAGE,
                                             canvas='edt.cvs.64de62b9-4b8a-4fc3-b92f-dce104c09328',
                                             shelf='',
                                             root=''
                                             )
        }
    ),
    CollectionNames.EPIC_STAGE_WITH_EXTRA_SHELF: Collection(
        collection_id='edt.col.647fbd6d-0b4f-4ee7-8abb-140abfe0d056',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(display_type=DisplayTypes.EPIC_STAGE,
                                             canvas='edt.cvs.64fa29ca-e723-4b38-ac30-a95826355de4',
                                             shelf='',
                                             root=''
                                             )
        }
    ),
    CollectionNames.MLS_NOTABLE_MOMENTS: Collection(
        collection_id='edt.col.654eafe1-a746-4660-b7fd-ed583b8b8d15',
        context_ids={
            DisplayTypes.SPORTS_EXTRAS_LOCKUP: Context(
                display_type=DisplayTypes.SPORTS_EXTRAS_LOCKUP,
                shelf='edt.shelf.654eb0c6-dcb7-4fac-a052-eb344eda47f2',
                canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47'
            )
        }
    ),
    CollectionNames.MLS_INTERVIEWS: Collection(
        collection_id='edt.col.654ea7d8-bc7b-4cbb-b961-39b83277ab40',
        context_ids={
            DisplayTypes.SPORTS_EXTRAS_LOCKUP: Context(
                display_type=DisplayTypes.SPORTS_EXTRAS_LOCKUP,
                shelf='edt.shelf.654ea844-4487-4bc3-93b3-8df73563e2e5',
                canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47'
            )
        }
    ),
    CollectionNames.MLS_KEY_PLAYS: Collection(
        collection_id='edt.col.654eaf15-605e-4014-8c8a-646ecb939cb1',
        context_ids={
            DisplayTypes.SPORTS_EXTRAS_LOCKUP: Context(
                display_type=DisplayTypes.SPORTS_EXTRAS_LOCKUP,
                shelf='edt.shelf.654eb0c6-d1ed-4ea9-93a5-edcb624e7727',
                canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47'
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
    CollectionNames.BONUS_AND_TRAILERS_ENHANCED_LOCKUP: Collection(
        collection_id='edt.col.6573601d-b386-4b0f-aa82-0c9b2312791f',
        context_ids={
            DisplayTypes.ENHANCED_LOCKUP: Context(
                display_type=DisplayTypes.ENHANCED_LOCKUP,
                canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47',
                shelf='edt.shelf.657360ec-c9e7-4711-9424-1f029288a10f',
            )
        }
    ),
    "large_sports_extras": Collection(
        collection_id='edt.col.654eb37a-4ad7-4039-97d0-36c8b4c61944',
        context_ids={
            DisplayTypes.SPORTS_EXTRAS_LOCKUP: Context(display_type=DisplayTypes.SPORTS_EXTRAS_LOCKUP,
                                                       canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47',
                                                       shelf='edt.shelf.654eb3e6-3711-44d4-a0b4-602041fb3f31',
                                                       )
        }
    ),
    "extras_and_non_extras_team": Collection(
        collection_id='edt.col.63a24b87-4815-4595-ab4b-0298787f9a52',
        context_ids={
            DisplayTypes.EPIC_INLINE: Context(display_type=DisplayTypes.EPIC_INLINE_A,
                                              canvas='edt.cvs.63c83c05-6fc5-4a62-8294-317bba3398f8',
                                              shelf='edt.shelf.63c83c05-66f0-4734-a429-3787fed6ba62',
                                              ),
            DisplayTypes.LOCKUP: Context(display_type=DisplayTypes.LOCKUP,
                                         canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f4',
                                         shelf='edt.shelf.65735ad9-7aca-4b83-b786-e0b08fcd2c9e',
                                         )
        }
    ),
    "distributed_extras": Collection(
        collection_id='edt.col.65735bee-28d3-42be-aa37-62969e598918',
        context_ids={
            DisplayTypes.LOCKUP: Context(display_type=DisplayTypes.LOCKUP,
                                         canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47',
                                         shelf='edt.shelf.65735c8b-f021-481c-ad71-c0d8d2694fd1',
                                         )
        }
    ),
    "trailers_and_paid_bonus": Collection(
        collection_id='edt.col.6573601d-b386-4b0f-aa82-0c9b2312791f',
        context_ids={
            DisplayTypes.LOCKUP: Context(display_type=DisplayTypes.LOCKUP,
                                         canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47',
                                         shelf='edt.shelf.657360ec-c9e7-4711-9424-1f029288a10f',
                                         )
        }
    ),
    "promotional_extras": Collection(
        collection_id='edt.col.65736e02-5c21-4a0c-8fda-4d92156d626b',
        context_ids={
            DisplayTypes.EPIC_INLINE: Context(display_type=DisplayTypes.EPIC_INLINE,
                                              canvas='edt.cvs.65736fae-162a-40e4-b2e2-22383d228205',
                                              shelf='edt.shelf.65736fae-ee33-4aae-85af-f019b92fb9c3',
                                              flavor='Flavor_A'
                                              ),
            DisplayTypes.EPIC_INLINE_A: Context(display_type=DisplayTypes.EPIC_INLINE_A,
                                                canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47',
                                                )
        }
    ),
    CollectionNames.LOCKUP_COLLECTION_WITH_BOX_SETS: Collection(
        collection_id='edt.col.6509e795-3fc9-47ce-9c7d-c3d048c41253',
        context_ids={
            DisplayTypes.LOCKUP: Context(display_type=DisplayTypes.LOCKUP,
                                         canvas='edt.cvs.6515ff9c-8e2a-40b4-94af-bf25533e140b',
                                         shelf='umc.cmr.its.se.2nek13h1ypet447u76iyilnok',
                                         root=''
                                         )
        },
    ),
    CollectionNames.OPAL_TRAILERS_LOCKUP: Collection(
        collection_id='edt.col.67bcf31a-9047-4814-b847-b50c9bceb500',
        context_ids={
            DisplayTypes.TRAILER_LOCKUP: Context(display_type=DisplayTypes.TRAILER_LOCKUP,
                                                 canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                                                 shelf='edt.shelf.67bcf422-c75e-4593-94e7-1034e366dab2',
                                                 root=''
                                                 )
        },
    ),
    CollectionNames.BRICK_COLLECTION_WITH_BOX_SETS: Collection(
        collection_id='edt.col.651c9b72-e3ad-4a6e-81f0-cb8de05f2e00',
        context_ids={
            DisplayTypes.BRICK: Context(display_type=DisplayTypes.BRICK,
                                        canvas='edt.cvs.6515ff9c-8e2a-40b4-94af-bf25533e140b',
                                        shelf='umc.cmr.its.se.5x2d313ejy3l9mp79ikeqdm8x',
                                        root=''
                                        )
        },
    ),
    CollectionNames.GRID_COLLECTION_WITH_BOX_SETS: Collection(
        collection_id='edt.col.651c9d20-09c8-481e-b83f-0ef97e2c09fd',
        context_ids={
            DisplayTypes.GRID_LOCKUP: Context(display_type=DisplayTypes.GRID_LOCKUP,
                                              canvas='edt.cvs.6515ff9c-8e2a-40b4-94af-bf25533e140b',
                                              shelf='umc.cmr.its.se.5tnwptz10xfimdrkuj44f3b2g',
                                              root=''
                                              )
        },
    ),
    CollectionNames.NOTES_LOCKUP_COLLECTION_WITH_BOX_SETS: Collection(
        collection_id='edt.col.651cd8e1-a483-465a-bde9-41a2bf7ee265',
        context_ids={
            DisplayTypes.NOTES_LOCKUP: Context(display_type=DisplayTypes.NOTES_LOCKUP,
                                               canvas='edt.cvs.6515ff9c-8e2a-40b4-94af-bf25533e140b',
                                               shelf='umc.cmr.its.se.5yzmphgz3h413490d22un0bz9',
                                               root=''
                                               )
        },
    ),
    CollectionNames.EPIC_SHOWCASE_A_COLLECTION_WITH_BOX_SETS: Collection(
        collection_id='edt.col.651ce216-fbc1-436f-984e-f6e05b5f9708',
        context_ids={
            DisplayTypes.EPIC_SHOWCASE_A: Context(display_type=DisplayTypes.EPIC_SHOWCASE_A,
                                                  canvas='edt.cvs.6515ff9c-8e2a-40b4-94af-bf25533e140b',
                                                  shelf='umc.cmc.455js879szmdywutf3qjewagm',
                                                  root=''
                                                  )
        },
    ),
    CollectionNames.EPIC_SHOWCASE_B_COLLECTION_WITH_BOX_SETS: Collection(
        collection_id='edt.col.651ce3ef-f8a5-4cd1-9d1a-f14e0e72d5c9',
        context_ids={
            DisplayTypes.EPIC_SHOWCASE_B: Context(display_type=DisplayTypes.EPIC_SHOWCASE_B,
                                                  canvas='edt.cvs.6515ff9c-8e2a-40b4-94af-bf25533e140b',
                                                  shelf='umc.cmr.its.se.2fzqe5mmabsof5yf5ypcs6gwi',
                                                  root=''
                                                  )
        },
    ),
    CollectionNames.EPIC_SHOWCASE_C_COLLECTION_WITH_BOX_SETS: Collection(
        collection_id='edt.col.651ce3b8-d7cd-4820-990d-acc60fcc6604',
        context_ids={
            DisplayTypes.EPIC_SHOWCASE_C: Context(display_type=DisplayTypes.EPIC_SHOWCASE_C,
                                                  canvas='edt.cvs.6515ff9c-8e2a-40b4-94af-bf25533e140b',
                                                  shelf='umc.cmr.its.se.ca5d9sqwh1prwz9xevxztlru',
                                                  root=''
                                                  )
        },
    ),
    CollectionNames.EPIC_SHOWCASE_D_COLLECTION_WITH_BOX_SETS: Collection(
        collection_id='edt.col.651ce520-2de1-40bf-942d-4292645b1848',
        context_ids={
            DisplayTypes.EPIC_SHOWCASE_D: Context(display_type=DisplayTypes.EPIC_SHOWCASE_D,
                                                  canvas='edt.cvs.6515ff9c-8e2a-40b4-94af-bf25533e140b',
                                                  shelf='umc.cmr.its.se.4mbxmxplll4ffepzsxp7avbn3',
                                                  root=''
                                                  )
        },
    ),
    CollectionNames.EPIC_INLINE_A_COLLECTION_WITH_BOX_SETS: Collection(
        collection_id='edt.col.651cdacd-b472-448e-901d-dd6aea530f61',
        context_ids={
            DisplayTypes.EPIC_INLINE_A: Context(display_type=DisplayTypes.EPIC_INLINE_A,
                                                canvas='edt.cvs.6515ff9c-8e2a-40b4-94af-bf25533e140b',
                                                shelf='umc.cmr.its.se.4mbxmxplll4ffepzsxp7avbn3',
                                                root=''
                                                )
        },
    ),
    CollectionNames.EPIC_INLINE_B_COLLECTION_WITH_BOX_SETS: Collection(
        collection_id='edt.col.651cdf93-6fc8-4cdf-822f-0ac90e2f34c2',
        context_ids={
            DisplayTypes.EPIC_INLINE_B: Context(display_type=DisplayTypes.EPIC_INLINE_B,
                                                canvas='edt.cvs.6515ff9c-8e2a-40b4-94af-bf25533e140b',
                                                shelf='',
                                                root='umc.cmr.its.se.3z00584pbhbhs3jdjkb189rcp'
                                                )
        },
    ),
    CollectionNames.EPIC_INLINE_C_COLLECTION_WITH_BOX_SETS: Collection(
        collection_id='edt.col.651cdff1-5a6b-4796-b32a-7527dd5acb84',
        context_ids={
            DisplayTypes.EPIC_INLINE_C: Context(display_type=DisplayTypes.EPIC_INLINE_C,
                                                canvas='edt.cvs.6515ff9c-8e2a-40b4-94af-bf25533e140b',
                                                shelf='umc.cmr.its.se.4cf590tp3hr41d6gx6z41x8km',
                                                root=''
                                                )
        },
    ),
    CollectionNames.EPIC_INLINE_D_COLLECTION_WITH_BOX_SETS: Collection(
        collection_id='edt.col.651ce094-4b7e-4234-a301-e58cf317d05e',
        context_ids={
            DisplayTypes.EPIC_INLINE_D: Context(display_type=DisplayTypes.EPIC_INLINE_D,
                                                canvas='edt.cvs.6515ff9c-8e2a-40b4-94af-bf25533e140b',
                                                shelf='umc.cmr.its.se.5avp85v23bvbu02vbffd9qwl6',
                                                root=''
                                                )
        },
    ),
    CollectionNames.EPIC_STAGE_COLLECTION_WITH_BOX_SETS: Collection(
        collection_id='edt.col.651c9cbb-92d6-476b-b35a-70e36ac92562',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(display_type=DisplayTypes.EPIC_STAGE,
                                             canvas='edt.cvs.6515ff9c-8e2a-40b4-94af-bf25533e140b',
                                             shelf='umc.cmr.its.se.2fzqe5mmabsof5yf5ypcs6gwi',
                                             root=''
                                             )
        },
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
    CollectionNames.PAGINATED_GAME_SCHEDULE_LOCKUP_TEAM: Collection(
        collection_id='edt.col.65691904-6b2d-43bf-8b30-68cafc8ff674',
        context_ids={
            DisplayTypes.GAME_SCHEDULE_LOCKUP: Context(display_type=DisplayTypes.GAME_SCHEDULE_LOCKUP,
                                                       canvas='edt.cvs.63c8355c-bc09-45fa-8dad-620f3c221ab3',
                                                       shelf='edt.shelf.63c8355c-cddf-4c60-8019-db64079dab84'
                                                       )
        }
    ),
    CollectionNames.GAME_SCHEDULE_LOCKUP_PINNING: Collection(
        collection_id='edt.col.65e8d6e7-9f9f-49ba-bfab-0e0dede48c5f',
        context_ids={
            DisplayTypes.GAME_SCHEDULE_LOCKUP: Context(display_type=DisplayTypes.GAME_SCHEDULE_LOCKUP,
                                                       canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47',
                                                       shelf='edt.shelf.65e8e053-8485-4cd2-bf5b-242712059e01'
                                                       )
        }
    ),
    CollectionNames.LEAGUE_STANDINGS_SHELF_WITH_CONTEXT: Collection(
        collection_id='uts.col.LeagueStandings.umc.csl.3c9plmy5skze52ff5ce24mo4g',
        context_ids={
            DisplayTypes.LEAGUE_STANDINGS: Context(display_type=DisplayTypes.LEAGUE_STANDINGS,
                                                   canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47',
                                                   shelf='edt.shelf.660468a6-b56f-405b-b201-43c8921b9b50',
                                                   root='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47'
                                                   )
        }
    ),
    CollectionNames.CONDUCTOR_TED_LASSO: Collection(
        collection_id='edt.col.6595fc9a-e5fc-4166-874f-07d6b8d57928',
        conductor_published_id='800444603555163'
    ),
    CollectionNames.CHRONOS_POSTPLAY: Collection(
        collection_id='',
        items=[
            'umc.cmc.40qrv09i2yfh8iilyi4s8vfi',  # Palmer movie
            'umc.cmc.7bztxfm8c2y0g5888tox6ed3u',  # LOTR movie
            'umc.cmc.2sp4pbfnp4sai5qen74ub8skc',  # Ted Lasso s1e1
            'umc.cmc.69sq804vqp3dy39oxiajnr3ux',  # Harry Potter movie
            'umc.cmc.39q9ehc6lpx0r70oe8iwwmt39'  # Elephant movie
        ]
    ),
    CollectionNames.CHRONOS_POSTPLAY_2: Collection(
        collection_id='',
        items=[
            'umc.cmc.3s4mgg2y7h95fks9gnc4pw13m',  # SEE show
            'umc.cmc.3vq452bru4dywi1y0fzildivg',  # The 100 show
            'umc.cmc.7htjb4sh74ynzxavta5boxuzq',  # GoT show
            'umc.cmc.dhahximux30cp6mferbl2wf4',  # Never Seen Again show
        ]
    ),
    CollectionNames.CHRONOS_POSTPLAY_3: Collection(
        collection_id='',
        items=[
            'umc.cmc.5983fipzqbicvrve6jdfep4x3',  # Foundation show
            'umc.cmc.5tuytm6lzyp9zn3ji1x27u63b',  # For All Mankind show
            'umc.cmc.70b7z97fv7azfzn5baqnj88p6',  # Invasion show
            'umc.cmc.260bmp43ucaq656rs0tw6aioj',  # Mad Men show
            'umc.cmc.b24vsa2aaua8e5l465xek14s'  # Outlander show
        ]
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

    CollectionNames.PLAY_DEMOTION_SHOWS_CHRONOS_SCORE_MODIFIER_TARGET: Collection(
        collection_id='edt.col.6569433a-119c-48d2-a0b5-7b7c574bc0ac',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                root='tahoma_watchnow',
                canvas='edt.cvs.67072dee-d7b6-4518-8261-30282d16254a',
                shelf='edt.shelf.67072dee-6f72-43e8-aacc-243c39b94ff5',
                display_type=DisplayTypes.LOCKUP
            )
        }
    ),

    CollectionNames.PLAY_DEMOTION_SHOWS: Collection(
        collection_id='edt.col.6569433a-119c-48d2-a0b5-7b7c574bc0ac',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                root='tahoma_watchnow',
                canvas='edt.cvs.669f12d0-d038-4b5a-af6f-ff6cbacd17ae',
                shelf='edt.shelf.669f12d0-c55e-4e4a-aae5-44b105a5a4bd',
                display_type=DisplayTypes.LOCKUP
            )
        }
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

    CollectionNames.SHELF_WITH_PLAYLIST: Collection(
        collection_id='edt.col.66a040a2-9987-46ad-9907-efbca9e36d31'
    ),

    CollectionNames.MLB_UPCOMING_SCHEDULE: Collection(
        collection_id='uts.col.mlb-league-page-upcoming-schedule',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                canvas='uts.tcvs.mlb-league-page-canvas',
                shelf='uts.shelf.upcoming-games',
                display_type=DisplayTypes.LOCKUP
            )
        }
    ),

    CollectionNames.MLB_LIVE_SCHEDULE: Collection(
        collection_id='uts.col.mlb-league-page-live-schedule',
        context_ids={
            DisplayTypes.SPORTS_CARD_LOCKUP: Context(
                canvas='uts.tcvs.mlb-league-page-canvas',
                shelf='uts.shelf.live-games',
                display_type=DisplayTypes.SPORTS_CARD_LOCKUP
            )
        }
    ),

    CollectionNames.MLB_VOD_SCHEDULE: Collection(
        collection_id='uts.col.mlb-league-page-past-schedule',
        context_ids={
            DisplayTypes.GAME_SCHEDULE_LOCKUP: Context(
                canvas='uts.tcvs.mlb-league-page-canvas',
                shelf='uts.shelf.past-games',
                display_type=DisplayTypes.GAME_SCHEDULE_LOCKUP
            )
        }
    ),

    CollectionNames.MLS_LIVE_AND_UPCOMING_SCHEDULE: Collection(
        collection_id='edt.col.654ea8ac-6ef1-426c-ac36-756294f3d827',
        context_ids={
            DisplayTypes.SPORTS_CARD_LOCKUP: Context(
                canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47',
                shelf='edt.shelf.654ea96c-6b99-4d5a-8e13-0f0f21c3028f',
                display_type=DisplayTypes.SPORTS_CARD_LOCKUP
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

    CollectionNames.MLB_LEAGUE_SHELF: Collection(
        collection_id='uts.col.mlb-league-epic-stage',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(
                canvas='uts.tcvs.mlb-league-page-canvas',
                shelf='uts.shelf.epic-stage',
                display_type=DisplayTypes.EPIC_STAGE,
                brand='tvs.sbd.8000'
            ),
            DisplayTypes.EPIC_STAGE_WITH_UPSELL: Context(
                canvas='uts.tcvs.mlb-league-page-canvas',
                display_type=DisplayTypes.EPIC_STAGE_WITH_UPSELL,
                brand='tvs.sbd.8000'
            ),
            DisplayTypes.EPIC_SHOWCASE: Context(
                canvas='uts.tcvs.mlb-league-page-canvas',
                display_type=DisplayTypes.EPIC_SHOWCASE,
                brand='tvs.sbd.8000'
            ),
            DisplayTypes.EPIC_INLINE: Context(
                canvas='uts.tcvs.mlb-league-page-canvas',
                display_type=DisplayTypes.EPIC_INLINE,
                brand='tvs.sbd.8000'
            ),
            DisplayTypes.BRICK: Context(
                canvas='uts.tcvs.mlb-league-page-canvas',
                display_type=DisplayTypes.BRICK,
                brand='tvs.sbd.8000'
            ),
            DisplayTypes.SPORTS_CARD_LOCKUP: Context(
                canvas='uts.tcvs.mlb-league-page-canvas',
                display_type=DisplayTypes.SPORTS_CARD_LOCKUP,
                brand='tvs.sbd.8000'
            ),
            DisplayTypes.GRID_LOCKUP: Context(
                canvas='uts.tcvs.mlb-league-page-canvas',
                display_type=DisplayTypes.GRID_LOCKUP,
                brand='tvs.sbd.8000'
            ),
            DisplayTypes.GAME_SCHEDULE_LOCKUP: Context(
                canvas='uts.tcvs.mlb-league-page-canvas',
                display_type=DisplayTypes.GAME_SCHEDULE_LOCKUP,
                brand='tvs.sbd.8000'
            ),
            DisplayTypes.UP_NEXT_LOCKUP: Context(
                canvas='uts.tcvs.mlb-league-page-canvas',
                display_type=DisplayTypes.UP_NEXT_LOCKUP,
                brand='tvs.sbd.8000'
            )
        }
    ),

    # Header override title collections
    CollectionNames.WATCH_NOW_EPIC_STAGE: Collection(
        collection_id='edt.col.638e4768-9f51-45c9-979c-1b8fd36eee9c',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(
                canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                display_type=DisplayTypes.EPIC_STAGE
            )
        }
    ),

    CollectionNames.TV_PLUS_EPIC_STAGE_WITH_UPSELL: Collection(
        collection_id='edt.col.629e7e8d-14dd-4cc4-ae4a-c9dfddc1844b',
        context_ids={
            DisplayTypes.EPIC_STAGE_WITH_UPSELL: Context(
                canvas='edt.cvs.610c550f-938a-46e7-98e3-c573fcd24208',
                display_type=DisplayTypes.EPIC_STAGE
            )
        }
    ),

    CollectionNames.STORE_EPIC_STAGE: Collection(
        collection_id='edt.col.647fbd6d-0b4f-4ee7-8abb-140abfe0d056',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(
                canvas='edt.cvs.64fa29ca-e723-4b38-ac30-a95826355de4',
                display_type=DisplayTypes.EPIC_STAGE
            )
        }
    ),

    CollectionNames.MLS_EPIC_STAGE_WITH_UPSELL: Collection(
        collection_id='edt.col.63b50945-b5c1-42a5-9d15-6500817d78ef',
        context_ids={
            DisplayTypes.EPIC_STAGE_WITH_UPSELL: Context(
                canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47',
                display_type=DisplayTypes.EPIC_STAGE
            )
        }
    ),

    CollectionNames.TV_PLUS_EPIC_STAGE_MULTI_QUERY_V1: Collection(
        collection_id='uts.col.tv-plus-epic-stage-multi-query-v1',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(
                display_type=DisplayTypes.EPIC_STAGE
            )
        }
    ),

    CollectionNames.TV_PLUS_EPIC_STAGE_MULTI_QUERY_V2: Collection(
        collection_id='uts.col.tv-plus-epic-stage-multi-query-v2',
        context_ids={
            DisplayTypes.EPIC_STAGE: Context(
                display_type=DisplayTypes.EPIC_STAGE
            )
        }
    ),

    CollectionNames.MLS_TV_PLUS_EPIC_STAGE_SPORTS_RANKER: Collection(
        collection_id='',
        items=[
            'umc.cse.3c1lrij4je4lzd7x7qnk3h63i',  # Live game
            'umc.cse.279bg3pkdgtuat1pl185c9xfp',  # Upcoming game
        ]
    ),
    CollectionNames.OPAL_SHELF_LOCKUP: Collection(
        collection_id='edt.col.67a3db41-852d-4961-9dec-fad5e3cb1e10',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.65e00bc1-fad6-4da1-8018-0b697c0cf63c',
                display_type=DisplayTypes.LOCKUP,
                root='tahoma_watchnow'
            )
        }
    ),
    CollectionNames.OPAL_SHELF_SPORTS_EXTRAS_LOCKUP: Collection(
        collection_id='edt.col.67a538df-b3c7-47e3-a582-e546c0f1d1f9',
        context_ids={
            DisplayTypes.SPORTS_EXTRAS_LOCKUP: Context(
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67a53b57-180e-45aa-9810-29d0978217b3',
                display_type=DisplayTypes.LOCKUP,
                root='tahoma_watchnow'
            )
        }
    ),
    CollectionNames.OPAL_SHELF_TRAILER_LOCKUP: Collection(
        collection_id='edt.col.67bcf31a-9047-4814-b847-b50c9bceb500',
        context_ids={
            DisplayTypes.TRAILER_LOCKUP: Context(
                canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                shelf='edt.shelf.67bcf422-c75e-4593-94e7-1034e366dab2',
                display_type=DisplayTypes.TRAILER_LOCKUP,
                root='tahoma_watchnow'
            )
        }
    ),
    CollectionNames.OPAL_SHELF_EPIC_INLINE_FLAVOR_A: Collection(
        collection_id='edt.col.67b394ec-8fbe-41fc-a872-828b97166b81',
        context_ids={
            DisplayTypes.EPIC_INLINE_A: Context(
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67b3962f-4cb4-48c3-b610-e47fb2ee8347',
                display_type=DisplayTypes.EPIC_INLINE_A,
                root='tahoma_watchnow'
            )
        }
    ),
    CollectionNames.OPAL_SHELF_EPIC_INLINE_FLAVOR_B: Collection(
        collection_id='edt.col.67b396aa-cd6b-4e6d-9904-89511e2d012c',
        context_ids={
            DisplayTypes.EPIC_INLINE_B: Context(
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67b39d51-146a-424f-8253-23a37d22486b',
                display_type=DisplayTypes.EPIC_INLINE_B,
                root='tahoma_watchnow'
            )
        }
    ),
    CollectionNames.OPAL_SHELF_EPIC_INLINE_FLAVOR_C: Collection(
        collection_id='edt.col.67b39980-83b6-4f7e-80f6-d3b71556c30b',
        context_ids={
            DisplayTypes.EPIC_INLINE_C: Context(
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67b39d51-b942-4829-b37d-fc2aec622cd6',
                display_type=DisplayTypes.EPIC_INLINE_C,
                root='tahoma_watchnow'
            )
        }
    ),
    CollectionNames.OPAL_SHELF_EPIC_INLINE_FLAVOR_D: Collection(
        collection_id='edt.col.67b399a1-74f0-4b23-a2f0-513eb56659c1',
        context_ids={
            DisplayTypes.EPIC_INLINE_D: Context(
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67b39d51-eb05-4ebc-aa35-19741509099c',
                display_type=DisplayTypes.EPIC_INLINE_D,
                root='tahoma_watchnow'
            )
        }
    ),
    CollectionNames.OPAL_SHELF_EPIC_INLINE_FLAVOR_E: Collection(
        collection_id='edt.col.67bcfa64-1199-4819-b343-edcec7c80ee0',
        context_ids={
            DisplayTypes.EPIC_INLINE_E: Context(
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67bcfcc1-e89a-4537-8c88-f26162cefa48',
                display_type=DisplayTypes.EPIC_INLINE_E,
                root='tahoma_watchnow'
            )
        }
    ),
    CollectionNames.OPAL_SHELF_EPIC_SHOWCASE_FLAVOR_A: Collection(
        collection_id='edt.col.67b394d5-0abe-40fb-868d-bf1b7e7662e9',
        context_ids={
            DisplayTypes.EPIC_SHOWCASE_A: Context(
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67b3962f-220b-48d8-8dfc-a1198adbf810',
                display_type=DisplayTypes.EPIC_SHOWCASE_A,
                root='tahoma_watchnow'
            )
        }
    ),
    CollectionNames.OPAL_SHELF_EPIC_SHOWCASE_FLAVOR_B: Collection(
        collection_id='edt.col.67b3969c-1f89-47f6-a769-ecb89bb25aaf',
        context_ids={
            DisplayTypes.EPIC_SHOWCASE_B: Context(
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67b39d51-25b5-4a1a-868b-c3954aa7a850',
                display_type=DisplayTypes.EPIC_SHOWCASE_B,
                root='tahoma_watchnow'
            )
        }
    ),
    CollectionNames.OPAL_SHELF_EPIC_SHOWCASE_FLAVOR_C: Collection(
        collection_id='edt.col.67b39973-6cf6-40d1-b36d-60ec2f4cfd58',
        context_ids={
            DisplayTypes.EPIC_SHOWCASE_C: Context(
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67b39d51-a9f0-4760-9f9b-2889c9e8f79b',
                display_type=DisplayTypes.EPIC_SHOWCASE_C,
                root='tahoma_watchnow'
            )
        }
    ),
    CollectionNames.OPAL_SHELF_EPIC_SHOWCASE_FLAVOR_D: Collection(
        collection_id='edt.col.67b39991-4ff7-41f9-a80c-b87b4b417394',
        context_ids={
            DisplayTypes.EPIC_SHOWCASE_D: Context(
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67b39d51-42a6-4097-8484-b3e2e26ad1a9',
                display_type=DisplayTypes.EPIC_SHOWCASE_D,
                root='tahoma_watchnow'
            )
        }
    ),
    CollectionNames.OPAL_SHELF_EPIC_SHOWCASE_FLAVOR_E: Collection(
        collection_id='edt.col.67bf7447-f140-497d-bb78-20b229a9aaff',
        context_ids={
            DisplayTypes.EPIC_SHOWCASE_E: Context(
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67bf74b3-89a5-43a8-af0c-9f70fae56f11',
                display_type=DisplayTypes.EPIC_SHOWCASE_E,
                root='tahoma_watchnow'
            )
        }
    ),
    CollectionNames.OPAL_SHELF_EPIC_SHOWCASE_FLAVOR_F: Collection(
        collection_id='edt.col.67dcaa36-31c8-4ed9-ac13-5dbd9d16552d',
        context_ids={
            DisplayTypes.EPIC_SHOWCASE_F: Context(
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67dcad89-c7d4-4e35-b830-221776c5c409',
                display_type=DisplayTypes.EPIC_SHOWCASE_F,
                root='tahoma_watchnow'
            )
        }
    ),
    CollectionNames.OPAL_SHELF_BRICK: Collection(
        collection_id='edt.col.67e71e46-b8c1-4ded-a4dc-443a3454bc3b',
        context_ids={
            DisplayTypes.BRICK: Context(
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67e72388-46c2-4181-8ead-680bf1e6984a',
                display_type=DisplayTypes.BRICK,
                root='tahoma_watchnow'
            )
        }
    ),
    CollectionNames.OPAL_SHELF_CATEGORY_BRICK: Collection(
        collection_id='edt.col.67b39354-0b4f-4199-b18b-23d0e79714c4',
        context_ids={
            DisplayTypes.BRICK: Context(
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67b3962f-ec7a-4417-af66-6b4a9d9dd171',
                display_type=DisplayTypes.BRICK,
                root='tahoma_watchnow'
            )
        }
    ),
    CollectionNames.OPAL_SHELF_CHARTS: Collection(
        collection_id='uts.col.ChartsBlended.tvs.sbd.4000',
        context_ids={
            DisplayTypes.CHART: Context(
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67bf7a1e-b910-46bc-9cfb-3f5365b84a62',
                display_type=DisplayTypes.CHART,
                root='tahoma_watchnow'
            )
        }
    ),
    CollectionNames.OPAL_SHELF_BRICK_FULLBLEED: Collection(
        collection_id='edt.col.67e72338-4003-4354-997b-1b166a962724',
        context_ids={
            DisplayTypes.BRICK: Context(
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67e72388-c1a4-4111-a262-c46c05c22a1d ',
                display_type=DisplayTypes.BRICK,
                root='tahoma_watchnow'
            )
        }
    ),
    CollectionNames.OPAL_SHELF_BRICK_HEADING_1: Collection(
        collection_id='edt.col.67e722b9-3939-4b38-b2cc-d18995fef529',
        context_ids={
            DisplayTypes.BRICK: Context(
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67e72388-0d5e-4158-bb31-3bdef1fcd12f',
                display_type=DisplayTypes.BRICK,
                root='tahoma_watchnow'
            )
        }
    ),
    CollectionNames.OPAL_SHELF_BRICK_HEADING_2: Collection(
        collection_id='edt.col.67e7232e-b3df-4e80-8e20-1dd6968855e6',
        context_ids={
            DisplayTypes.BRICK: Context(
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67e72388-aff9-427d-9f3d-40391ff9eec8',
                display_type=DisplayTypes.BRICK,
                root='tahoma_watchnow'
            )
        }
    ),
    CollectionNames.OPAL_SHELF_SPORTS_CARD_LOCKUP: Collection(
        collection_id='edt.col.67afc65c-83c7-4155-badd-b9abba9f369d',
        context_ids={
            DisplayTypes.SPORTS_CARD_LOCKUP: Context(
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67afce89-353a-41e7-9d0d-1a219201331c',
                display_type=DisplayTypes.SPORTS_CARD_LOCKUP,
                root='tahoma_watchnow'
            )
        }
    ),
    CollectionNames.OPAL_MARKER_SHELF: Collection(
        collection_id='uts.col.PersonalizedLiveSports',
        context_ids={
            DisplayTypes.SPORTS_CARD_LOCKUP: Context(
                root='',
                canvas='edt.cvs.5c3786c3-3593-465b-83ba-ae6a4d33b199',
                shelf='edt.shelf.60b97c66-3a95-4d02-83f9-282238e92368',
                display_type=DisplayTypes.SPORTS_CARD_LOCKUP
            )
        }
    ),
    CollectionNames.OPAL_SHELF_EPIC_INLINE: Collection(
        collection_id='edt.col.6602c6e6-38c2-4a11-a36a-14f6b8e6ad2c',
        context_ids={
            DisplayTypes.EPIC_INLINE_A: Context(
                canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47',
                shelf='edt.shelf.66185efb-3d12-48a4-969a-c64fd0c25f4b',
                display_type=DisplayTypes.EPIC_INLINE_A,
                brand='tvs.sbd.7000'
            ),
            DisplayTypes.EPIC_INLINE_B: Context(
                canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47',
                shelf='edt.shelf.66185efb-3d12-48a4-969a-c64fd0c25f4b',
                display_type=DisplayTypes.EPIC_INLINE_B,
                brand='tvs.sbd.7000'
            ),
            DisplayTypes.EPIC_INLINE_C: Context(
                canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47',
                shelf='edt.shelf.66185efb-3d12-48a4-969a-c64fd0c25f4b',
                display_type=DisplayTypes.EPIC_INLINE_C,
                brand='tvs.sbd.7000'
            ),
            DisplayTypes.EPIC_INLINE_D: Context(
                canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47',
                shelf='edt.shelf.66185efb-3d12-48a4-969a-c64fd0c25f4b',
                display_type=DisplayTypes.EPIC_INLINE_D,
                brand='tvs.sbd.7000'
            ),
            DisplayTypes.EPIC_INLINE_E: Context(
                canvas='edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47',
                shelf='edt.shelf.66185efb-3d12-48a4-969a-c64fd0c25f4b',
                display_type=DisplayTypes.EPIC_INLINE_E,
                brand='tvs.sbd.7000'
            )
        }
    ),
    CollectionNames.OPAL_SHELF_NOTES_LOCKUP_MIXED: Collection(
        collection_id='edt.col.67b92222-28a6-44a3-adbd-bd8eed7b5249',
        context_ids={
            DisplayTypes.NOTES_LOCKUP: Context(
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67bf5fb5-32f8-49e8-8280-193a1a24f79a',
                display_type=DisplayTypes.NOTES_LOCKUP,
            )
        }
    ),
    CollectionNames.OPAL_SHELF_NOTES_LOCKUP_NO_DIRECT_PLAYBACK_ONLY: Collection(
        collection_id='edt.col.67db4c4c-a3d9-4f84-91de-157651df92ca',
        context_ids={
            DisplayTypes.NOTES_LOCKUP: Context(
                canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                shelf='edt.shelf.67dcad89-ab96-46b6-ae7f-b790c9cd8d94',
                display_type=DisplayTypes.NOTES_LOCKUP,
            )
        }
    ),
    CollectionNames.OPAL_EPISODE_LOCKUP: Collection(
        collection_id='edt.col.67a3dbe5-840d-4848-9698-2238007fb647',
        context_ids={
            DisplayTypes.EPISODE_LOCKUP: Context(display_type=DisplayTypes.EPISODE_LOCKUP,
                                                 canvas='edt.cvs.65c56188-2042-4bce-8645-866eb69e4cc1',
                                                 shelf='edt.shelf.65e00bc1-c3bd-47f5-9c9b-29c603834e68',
                                                 root=''
                                                 )
        },
    ),
    CollectionNames.GROUP_FOR_YOU: Collection(
        collection_id='uts.col.group-for-you-recommendations',
        context_ids={
            DisplayTypes.LOCKUP: Context(
                display_type=DisplayTypes.LOCKUP,
            )
        }
    )
}
