from test_data_classes import UTSOffer
from test_data_keys import UTSOfferTypes, AccountTypes

UTS_OFFERS = {
    UTSOfferTypes.FREE_TRIAL: UTSOffer(
        offer_name='AppleTVPlus_1month_001',
        offer_intent='FreeTrial',
        eligibility_type='INTRO',
        account_types=[AccountTypes.DEFAULT_DEBUG_USER]
    ),
    UTSOfferTypes.REGULAR: UTSOffer(
        offer_name='Regular',
        offer_intent='Regular',
        eligibility_type='NONE',
        account_types=[AccountTypes.TV_PLUS_PARAMOUNT_BURNED]
    ),
    UTSOfferTypes.CHAMELEON_INTRO: UTSOffer(
        offer_name='AppleTVPlus_1month_001',
        offer_intent='IndIntroDiscountConfigOffer',
        eligibility_type='INTRO',
        account_types=[AccountTypes.TV_PLUS_PARAMOUNT_NOT_SUBSCRIBED]
    ),
    UTSOfferTypes.CHAMELEON_WINBACK: UTSOffer(
        offer_name='AppleTVPlus_1month_001',
        offer_intent='IndWinbackDiscountConfigOffer',
        eligibility_type='GENERIC_MARKETING',
        account_types=[AccountTypes.TV_PLUS_PARAMOUNT_BURNED]
    ),
    UTSOfferTypes.MLS_MONTHLY: UTSOffer(
        offer_name='MLS_Season_Pass_1month',
        offer_intent='Regular',
        eligibility_type='NONE'
    ),
    UTSOfferTypes.MLS_SEASON: UTSOffer(
        offer_name='MLS_Season_Pass_1season',
        offer_intent='Regular',
        eligibility_type='NONE'
    )
}
