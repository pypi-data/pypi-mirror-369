from test_data_classes import Account
from test_data_keys import AccountTypes
####################################################################################################
# UPSELL OFFER ACCOUNTS
# Accounts with UP_NEXT PRIVILEGES: https://quip-apple.com/54lfAXCviks4
####################################################################################################
ACCOUNTS = {
    # Not signed in offer eligible accounts
    # test_data.ACCOUNTS[AccountTypes.COLD_START].dsid
    AccountTypes.COLD_START: Account(
        dsid='',
        cid='',
    ),
    AccountTypes.DEFAULT_DEBUG_USER: Account(
        dsid='20898464899',
        cid='40ede524456043a592b539a37cd838a6050',
    ),
    AccountTypes.TV_PLUS_PARAMOUNT_NOT_SUBSCRIBED: Account(
        dsid='21759168540',
        cid='5568f4868427480db961d711d038439f053',
    ),
    AccountTypes.MLS_NOT_SUBSCRIBED: Account(
        dsid='21759168540',
        cid='5568f4868427480db961d711d038439f053',
    ),
    AccountTypes.MLS_BURNED: Account(
        dsid='21772512925',
        cid='f9c51736ea784e859c00cc80af1c5e76007',
    ),
    # TODO: account need to be activated
    AccountTypes.TV_PLUS_BURNED: Account(
        dsid='18783600076',
        cid='0e04c3d15ead4adb8fd84ffaeb872d8a032',
    ),
    AccountTypes.TV_PLUS_PARAMOUNT_SUBSCRIBED: Account(
        dsid='21756388232',
        cid='c6ca5ba3d55749dc8a8fc5942c719fa9047',
    ),
    AccountTypes.TV_PLUS_SUBSCRIBED_MLS_NOT_SUBSCRIBED: Account(
        dsid='21756388232',
        cid='c6ca5ba3d55749dc8a8fc5942c719fa9047',
    ),
    AccountTypes.TV_PLUS_PARAMOUNT_BURNED: Account(
        dsid='21772512925',
        cid='f9c51736ea784e859c00cc80af1c5e76007',
    ),
    AccountTypes.MLS_SEASON_SUBSCRIBED: Account(
        dsid='21758990622',
        cid='6c11390249d7443dae694e2c6d1e2485023',
    ),

    # Harmony offer eligible accounts
    AccountTypes.HARMONY: Account(
        dsid='20898464899',
        cid='40ede524456043a592b539a37cd838a6050',
    ),
    # TODO: account need to be activated
    AccountTypes.HARMONY2: Account(
        dsid='20993083884',
        cid='5c2e0a799c384dcea2d5c190d0389289049',
    ),
    # TODO: account need to be activated
    AccountTypes.HARMONY_WINBACK: Account(
        dsid='18306947231',
        cid='e4417a73998c43f9ace3c566b48d096b049',
    ),
    # McCormick offer eligible accounts
    AccountTypes.MCC1_INTRO: Account(
        dsid='20898464899',
        cid='40ede524456043a592b539a37cd838a6050',
    ),
    AccountTypes.MCC1_BURNED: Account(
        dsid='18168650454',
        cid='d5c28cd1de6742e3b35ae90555222a5d042',
    ),
    AccountTypes.MCC2_INTRO: Account(
        dsid='20898464899',
        cid='40ede524456043a592b539a37cd838a6050',
    ),
    AccountTypes.MCC2_BURNED: Account(
        dsid='18168650454',
        cid='d5c28cd1de6742e3b35ae90555222a5d042',
    ),
    # CIP offer eligible accounts
    # TODO: account need to be activated
    AccountTypes.CIP_A1_PREMIER: Account(
        dsid='18297594663',
        cid='6183cf26254e4a49968d5b36508a4425031',
    ),
    # TODO: account need to be activated
    AccountTypes.CIP_A1_FAMILY: Account(
        dsid='0ad61d601886451a97ff8d1607c8aa1a041',
        cid='18339113462',
    ),
    AccountTypes.CIP_A1_INDIVIDUAL: Account(
        dsid='20798613490',
        cid='2297b38347f044cfbcdecca31f29e180007',
    ),
    # TODO: account need to be activated
    AccountTypes.CIP_HARD_BUNDLE: Account(
        dsid='18307018290',
        cid='a4a0d807001347e782a56a75bdb1bf2e034',
    ),
    # TODO: account need to be activated
    AccountTypes.CIP_EXTENDED_OFFER: Account(
        dsid='18306398590',
        cid='423f0366ee1944359e2971f6937452e3010',
    ),
    AccountTypes.CIP_BARCLAYSGB_FIN_ATV_HB: Account(
        dsid='',
        cid='',
    ),
    AccountTypes.CIP_TELUSCA_MVPD_ATV_HB: Account(
        dsid='',
        cid='',
    ),
    AccountTypes.CIP_TELUSCA_MVPD_ATV_PMEO_6M: Account(
        dsid='',
        cid='',
    ),
    AccountTypes.CIP_TOTALPLAYMX_MVPD_ATV_CPAID: Account(
        dsid='',
        cid='',
    ),
    AccountTypes.CIP_TOTALPLAYMX_MVPD_ATV_HB: Account(
        dsid='',
        cid='',
    ),
    AccountTypes.CIP_TOTALPLAYMX_MVPD_ATV_PMEO_3M: Account(
        dsid='',
        cid='',
    ),
    # 3PTV offer eligible accounts
    AccountTypes.PLAYSTATION4: Account(
        dsid='',
        cid='',
    ),
    AccountTypes.PLAYSTATION5: Account(
        dsid='',
        cid='',
        email='',
    ),
    AccountTypes.LG: Account(
        dsid='',
        cid='',
        email='',
    ),
    AccountTypes.VIZIO: Account(
        dsid='',
        cid='',
        email='',
    ),
    AccountTypes.TELSTRA: Account(
        dsid='',
        cid='',
        email='',
    ),
    AccountTypes.WITH_ITEMS_IN_UP_NEXT: Account(
        dsid='18277018136',
        cid='1b1ef44065c448c8a192f7387baf3000031',
        email='miche.b456dkx.paid@icloud.com',  # Password: Blackberry0938*, Remote Secret: 123456
        protected=True
    ),
    AccountTypes.RECO_WITH_PLAY_ACTIVITY: Account(
        dsid='50652535',
        cid='b9a5f273507b4d2bb2c3e926e13ff8ba010',
        protected=True
    ),
    # Same as CIP_A1_INDIVIDUAL, reproduced to identify better in test cases.
    # Allow-listed account with mock entitlements, see here:
    #     https://uts-api-tests.itunes.apple.com/uts-api/mock-files/mock-entitlement-dataset%2F
    # Play history cover all sidebar smart filter cases (see test), events are added dynamically before the test
    # using the API to POST to /uts/v3/internal/debug/playActivity and removed after test is finished
    AccountTypes.SMART_FILTERING_PLAY_HISTORY_CASES_MCC: Account(
        dsid='20798613490',
        cid='2297b38347f044cfbcdecca31f29e180007'
    ),
    # Account with real entitlements (older than 1 year).
    # Uses mock last-play data to cover all sidebar smart filter cases (account is not allow-listed so old play events
    # can't be added), see here:
    #     https://uts-api-tests.itunes.apple.com/uts-api/mock-files/user-storage%2Fdefault%2Fbrand-info%2F
    AccountTypes.SMART_FILTERING_PLAY_HISTORY_CASES_FED: Account(
        dsid='20086826675',
        cid='mock:default:6fe78b6a60fc4d6da987a41b869020bc022'
    ),

    AccountTypes.WITH_SPORT_FAVORITES: Account(
        dsid='18431325058',
        cid='9ed6f1b7abca413c9f8e11e9908d32ac012',
        protected=True
    ),
    # Events are added on a session-level fixture called 'account_with_sporting_events_in_up_next'.
    # It is cleaned up after use.
    AccountTypes.WITH_SPORTING_EVENTS_IN_UP_NEXT: Account(
        dsid='995000000421456069',
        cid='09a4bb86c915459ca68c49399e8259b4048'
    ),
    # valid accounts, available to use
    AccountTypes.UNUSED_ACCOUNT_A: Account(
        dsid='18308834348',
        cid='a8a5e70ac0234f538ca886442728d36c059'
    ),
    AccountTypes.UNUSED_ACCOUNT_B: Account(
        dsid='20898464899',
        cid='40ede524456043a592b539a37cd838a6050',
    ),
    AccountTypes.PERSONALIZATION_OPTED_OUT: Account(
        dsid='20200722870',
        cid='4b74964ca79f4cf1a135a34f1ad915fc002'
    ),
    # dummy account for unit test
    AccountTypes.DUMMY_PROTECTED_ACCOUNT: Account(
        dsid='12345',
        cid='1234567890',
        protected=True
    ),
    AccountTypes.U13_ACCOUNT: Account(
        dsid='16550638301',
        cid='819de888a9554c8788bda5bd54973a0c038',
    ),
    AccountTypes.UP_NEXT_TESTS: Account(
        dsid='20982814414',
        cid='6bd251fa23c045ebb5b382c5c2d5133b036',
    ),
    AccountTypes.FAVORITES_TESTS: Account(
        dsid='20937381576',
        cid='aceba56cc79946bea1754f47915b9b9c032',
    ),
    AccountTypes.USER_SETTINGS_TESTS: Account(
        dsid='20933186034',
        cid='435a9f0ebb574e2f85d549c5a87a74c6034',
    ),
    # this is an empty account created but never used

    # feel free to rename and use it
    # AccountTypes.UNLABELED: Account(
    #    dsid='18424518715',
    #    cid='b3852ae54a0b466690e2bb7c7a0f4009001',
    #    email='garry.p24g38b.9i4g@icloud.com',
    #    encrypted_password=b'Q2hlcnJ5OTUyNCY='  # Cherry9524&
    #

    # This account should not be used unless a
    # user with prototype features is needed
    AccountTypes.SAI_DEBUGGER_USER: Account(
        dsid='290713331',
        cid='7c22eeaa86744b51aa66d25791e2c649053',
        protected=True
    ),
}
