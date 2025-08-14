from test_data_classes import UTSOffer
from test_data_keys import UTSOfferTypes, AccountTypes

THIRD_PTV_GENERIC_ACCOUNT_TYPES = [
    # AccountTypes.PLAYSTATION4, AccountTypes.PLAYSTATION5,
    AccountTypes.TELSTRA]

THIRD_PTV_WEB_GENERIC_ACCOUNT_TYPES = [AccountTypes.COMCAST]

UTS_OFFERS = {
    UTSOfferTypes.FREE_TRIAL: UTSOffer(
        offer_name='AppleTVPlus_1month_001',
        offer_intent='FreeTrial',
        eligibility_type='INTRO',
        account_types=[AccountTypes.DEFAULT_DEBUG_USER]  # [AccountTypes.MCC1_INTRO, AccountTypes.MCC2_INTRO]
    ),
    UTSOfferTypes.CHAMELEON_INTRO: UTSOffer(
        offer_name='AppleTVPlus_1month_001',
        offer_intent='IndIntroDiscountConfigOffer',
        eligibility_type='INTRO',
        account_types=[AccountTypes.DEFAULT_DEBUG_USER]
    ),
    UTSOfferTypes.CHAMELEON_WINBACK: UTSOffer(
        offer_name='AppleTVPlus_1month_001',
        offer_intent='IndWinbackDiscountConfigOffer',
        eligibility_type='GENERIC_MARKETING',
        account_types=[AccountTypes.TV_PLUS_BURNED]
    ),
    UTSOfferTypes.PLATO_REGULAR: UTSOffer(
        offer_name='Bundle_Regular',
        offer_intent='Regular',
        offer_type='BundleStoreKitOffer',
        subscription_bundle_id='2000061889',
        account_types=[AccountTypes.DEFAULT_DEBUG_USER]
    ),
    UTSOfferTypes.PLATO_UPGRADE: UTSOffer(
        offer_name='Bundle_Upgrade',
        offer_intent='Upgrade',
        offer_type='BundleStoreKitOffer',
        subscription_bundle_id='2000061889',
        account_types=[AccountTypes.MLS_TV_PLUS_SUBSCRIBED]
    ),
    UTSOfferTypes.HARMONY: UTSOffer(
        offer_name='harmony',
        ad_hoc_offer_id='1Party_Harmony_Winback_TV_Offer_1',
        offer_intent='Harmony2',
        device_purchased='Apple device',
        eligibility_type='HARDWARE_1',
        account_types=[AccountTypes.HARMONY, AccountTypes.HARMONY2, AccountTypes.HARMONY_WINBACK]
    ),
    UTSOfferTypes.REGULAR: UTSOffer(
        offer_name='Regular',
        offer_intent='Regular',
        eligibility_type='NONE',
        account_types=[AccountTypes.TV_PLUS_BURNED, AccountTypes.MCC1_BURNED, AccountTypes.MCC2_BURNED]
    ),
    UTSOfferTypes.ARISTOTLE_GENERIC: UTSOffer(
        offer_name='AristotleGeneric',
        offer_intent='AristotleGeneric',
        eligibility_type='HARD_BUNDLE',
        account_types=[AccountTypes.CIP_A1_PREMIER, AccountTypes.CIP_A1_FAMILY, AccountTypes.CIP_A1_INDIVIDUAL]
    ),
    UTSOfferTypes.WIRELESS_HARD_BUNDLE: UTSOffer(
        offer_name='WirelessHardBundle',
        offer_intent='WirelessHardBundle',
        eligibility_type='HARD_BUNDLE',
        carrier_name='T-Mobile USA',
        account_types=[AccountTypes.CIP_HARD_BUNDLE]
    ),
    UTSOfferTypes.WIRELESS_EXTENDED_TRIAL: UTSOffer(
        offer_name='WirelessExtendedTrial',
        offer_intent='WirelessExtendedTrial',
        eligibility_type='HARD_BUNDLE',
        account_types=[AccountTypes.CIP_EXTENDED_OFFER]
    ),
    UTSOfferTypes.WEB_GENERIC_PLAN_3PTV: UTSOffer(
        offer_name='AppleTVPlus_1month_001',
        offer_intent='WebGenericPlan3PTV',
        free_duration_period='3',
        eligibility_type='HARDWARE_1',
        ad_hoc_offer_id='3Party_Comcast_TV_Offer_1',
        account_types=THIRD_PTV_GENERIC_ACCOUNT_TYPES + THIRD_PTV_WEB_GENERIC_ACCOUNT_TYPES
    ),
    UTSOfferTypes.HARDWARE_GENERIC_PLAN_3PTV: UTSOffer(
        offer_name='AppleTVPlus_1month_001',
        offer_intent='HardwareGeneric3PTV',
        free_duration_period='3',
        eligibility_type='HARDWARE_1',
        ad_hoc_offer_id='3Party_Comcast_TV_Offer_1',
        account_types=THIRD_PTV_GENERIC_ACCOUNT_TYPES
    ),
    UTSOfferTypes.MLS_MONTHLY_WITHOUT_TV_PLUS: UTSOffer(
        offer_name='AppleTVPlus_1month_001',
        offer_intent='MLSMonthlyPlanNonTVPlus',
        eligibility_type='NONE',
        account_types=[AccountTypes.COLD_START, AccountTypes.MLS_BURNED]
    ),
    UTSOfferTypes.MVPD_GENERIC_WIRELESS_HARD_BUNDLE_STREAM_PLUS: UTSOffer(
        offer_name='MVPDGenericWirelessHardBundleStream+',
        offer_intent='MVPDGenericWirelessHardBundle',
        eligibility_type='HARD_BUNDLE',
        provider_name='Stream+',
        account_types=[AccountTypes.CIP_TELUSCA_MVPD_ATV_HB, AccountTypes.CIP_TELUSCA_MVPD_ATV_PMEO_6M]
    ),
    UTSOfferTypes.MVPD_GENERIC_WIRELESS_HARD_BUNDLE_TOTAL_PLAY: UTSOffer(
        offer_name='MVPDGenericWirelessHardBundleTotalPlay',
        offer_intent='MVPDGenericWirelessHardBundle',
        eligibility_type='HARD_BUNDLE',
        provider_name='TotalPlay',
        account_types=[AccountTypes.CIP_TOTALPLAYMX_MVPD_ATV_CPAID, AccountTypes.CIP_TOTALPLAYMX_MVPD_ATV_HB,
                       AccountTypes.CIP_TOTALPLAYMX_MVPD_ATV_PMEO_3M]
    ),
    UTSOfferTypes.MVPD_GENERIC_WIRELESS_HARD_BUNDLE_BARCLAYS: UTSOffer(
        offer_name='MVPDGenericWirelessHardBundleBarclays',
        offer_intent='MVPDGenericWirelessHardBundle',
        eligibility_type='HARD_BUNDLE',
        provider_name='Barclays',
        account_types=[AccountTypes.CIP_BARCLAYSGB_FIN_ATV_HB]
    ),
    UTSOfferTypes.MVPD_GENERIC_WIRELESS_HARD_BUNDLE_COMCAST: UTSOffer(
        offer_name='MVPDGenericWirelessHardBundleComcast',
        offer_intent='MVPDGenericAppleManagedExtOffer',
        eligibility_type='HARD_BUNDLE',
        provider_name='Comcast',
        account_types=[AccountTypes.CIP_CTUS_MVPD_ATV_CPAID, AccountTypes.CIP_CTUSXUMO_MVPD_ATV_CPAID]
    ),
    UTSOfferTypes.CTUS_MVPD_ATV_CPAID: UTSOffer(
        product_code='CTUS_MVPD_ATV_CPAID',
        adam_id='1472441559',
        offer_name='MVPDGenericAppleManagedExtOfferCtus',
        offer_intent='MVPDGenericAppleManagedExtOffer',
        eligibility_type='HARD_BUNDLE',
        provider_name='Comcast',
        account_types=[]
    ),
    UTSOfferTypes.CTUSXUMO_MVPD_ATV_CPAID: UTSOffer(
        product_code='CTUSXUMO_MVPD_ATV_CPAID',
        adam_id='1472441559',
        offer_name='MVPDGenericAppleManagedExtOfferCtusXumo',
        offer_intent='MVPDGenericAppleManagedExtOffer',
        eligibility_type='HARD_BUNDLE',
        provider_name='Comcast',
        account_types=[]
    ),
    UTSOfferTypes.BARCLAYSGB_FIN_MLS_HB: UTSOffer(
        product_code='BARCLAYSGB_FIN_MLS_HB',
        adam_id='6445132388',
        offer_name='MVPDSeasonalGenericWirelessHardBundleOfferBarclays',
        offer_intent='MVPDSeasonalGenericWirelessHardBundleOffer',
        eligibility_type='HARD_BUNDLE',
        provider_name='Barclays',
        account_types=[]
    ),
    UTSOfferTypes.CTUS_MVPD_MLS_CPAID_SEASON: UTSOffer(
        product_code='CTUS_MVPD_MLS_CPAID_SEASON',
        adam_id='6445132219',
        offer_name='MVPDGenericAppleManagedExtOfferCtusXumo',
        offer_intent='MVPDGenericAppleManagedExtOffer',
        eligibility_type='HARD_BUNDLE',
        provider_name='Comcast',
        account_types=[]
    ),
    UTSOfferTypes.CTUS_MVPD_MLS_CPAID: UTSOffer(
        product_code='CTUS_MVPD_MLS_CPAID',
        adam_id='6445132388',
        offer_name='MVPDGenericAppleManagedExtOfferCtusXumo',
        offer_intent='MVPDGenericAppleManagedExtOffer',
        eligibility_type='HARD_BUNDLE',
        provider_name='Comcast',
        account_types=[]
    ),
    UTSOfferTypes.CTUSXUMO_MVPD_MLS_CPAID: UTSOffer(
        product_code='CTUSXUMO_MVPD_MLS_CPAID',
        adam_id='6445132388',
        offer_name='MVPDGenericAppleManagedExtOfferCtusXumo',
        offer_intent='MVPDGenericAppleManagedExtOffer',
        eligibility_type='HARD_BUNDLE',
        provider_name='Comcast',
        account_types=[]
    ),
    UTSOfferTypes.CTUSXUMO_MVPD_MLS_CPAID_SEASON: UTSOffer(
        product_code='CTUSXUMO_MVPD_MLS_CPAID_SEASON',
        adam_id='6445132219',
        offer_name='MVPDGenericAppleManagedExtOfferCtusXumo',
        offer_intent='MVPDGenericAppleManagedExtOffer',
        eligibility_type='HARD_BUNDLE',
        provider_name='Comcast',
        account_types=[]
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
    ),
    UTSOfferTypes.CHAPMAN_LEAGUE_MONTHLY: UTSOffer(
        offer_name='Chapman_1month',
        offer_intent='MLBLeaguePassMonthly',
        eligibility_type='INTRO'
    ),
    UTSOfferTypes.CHAPMAN_LEAGUE_ANNUALLY: UTSOffer(
        offer_name='Chapman_1season',
        offer_intent='MLBLeaguePassSeasonal',
        eligibility_type='INTRO'
    ),
    UTSOfferTypes.CHAPMAN_LEAGUE_OOM_ANNUALLY: UTSOffer(
        offer_name='Chapman_oom_1season',
        offer_intent='MLBLeaguePassSeasonal',
        eligibility_type='INTRO'
    ),
    UTSOfferTypes.CHAPMAN_LEAGUE_OOM_MONTHLY: UTSOffer(
        offer_name='Chapman_oom_1month',
        offer_intent='MLBLeaguePassSeasonal',
        eligibility_type='INTRO'
    ),
    UTSOfferTypes.CHAPMAN_ASTROS_ANNUALLY: UTSOffer(
        offer_name='HoustonAstros_1season',
        offer_intent='MLBLeaguePassSeasonal',
        eligibility_type='INTRO'
    ),
    UTSOfferTypes.CHAPMAN_ASTROS_MONTHLY: UTSOffer(
        offer_name='HoustonAstros_1month',
        offer_intent='MLBLeaguePassSeasonal',
        eligibility_type='INTRO'
    ),
    UTSOfferTypes.CHAPMAN_RANGERS_ANNUALLY: UTSOffer(
        offer_name='TexasRangers_1season',
        offer_intent='MLBLeaguePassSeasonal',
        eligibility_type='INTRO'
    ),
    UTSOfferTypes.CHAPMAN_RANGERS_MONTHLY: UTSOffer(
        offer_name='TexasRangers_1month',
        offer_intent='MLBLeaguePassSeasonal',
        eligibility_type='INTRO'
    ),
    UTSOfferTypes.CHAPMAN_PADRES_ANNUALLY: UTSOffer(
        offer_name='SanDiegoPadres_1season',
        offer_intent='MLBLeaguePassSeasonal',
        eligibility_type='INTRO'
    ),
    UTSOfferTypes.CHAPMAN_PADRES_MONTHLY: UTSOffer(
        offer_name='SanDiegoPadres_1month',
        offer_intent='MLBLeaguePassSeasonal',
        eligibility_type='INTRO'
    )
}
