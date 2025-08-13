from test_data_classes import Account
from test_data_keys import AccountTypes

####################################################################################################
# UPSELL OFFER ACCOUNTS
####################################################################################################
ACCOUNTS = {
    # Not signed in offer eligible accounts
    # test_data.ACCOUNTS[AccountTypes.COLD_START].dsid
    AccountTypes.COLD_START: Account(
        dsid='', cid='',
    ),
    AccountTypes.DEFAULT_DEBUG_USER: Account(
        dsid='995000000629498143',
        cid='4f1c0d2dbd49400483b5da476390cdc1002',
        email='amp-uts-api+vkmydo@apple.com',
        encrypted_password=b'SHhqaWp0anI3',
    ),
    AccountTypes.PURPLE_ALLOW_LISTED: Account(
        email='utsqatv+subs@apple.com',
        dsid='998000005312751854',
        cid='6d64cd64d85c47f3ac2fde28c6ad5090001',
        encrypted_password=b'UEBzc3cwcmQhMzc5'
    ),
    AccountTypes.MLS_TV_PLUS_SUBSCRIBED: Account(
        dsid='995000000719441544',
        cid='99ffdffbc5d942b091950a7d2954f159001',
        email='mcarreira+freetrial@apple.com',
    ),
    AccountTypes.MLS_BURNED: Account(
        dsid='995000000731319358',
        cid='c06baa84570c4074ae50068af3539ca0001',
    ),
    AccountTypes.TV_PLUS_BURNED: Account(
        dsid='995000000774080714',
        cid='753a37f7e16e4b9e90e71c1ddc5900a5001',
        email='amp-uts-api+eexwgn@apple.com',
    ),
    # Harmony offer eligible accounts
    AccountTypes.HARMONY: Account(
        dsid='995000000719439242',
        cid='6a2da79c65f5420681974cd50f2e4eb4002',
    ),
    AccountTypes.HARMONY2: Account(
        dsid='995000000468666355',
        cid='3baba5c0d52544919ee2eccfd611a6b5002',
    ),
    AccountTypes.HARMONY_WINBACK: Account(
        dsid='995000000725176615',
        cid='9c0fd1bdcc564ad4a05a12b64e24f988001',
    ),
    # McCormick offer eligible accounts
    AccountTypes.MCC1_INTRO: Account(  # showtime
        dsid='995000000629498143',
        cid='4f1c0d2dbd49400483b5da476390cdc1002',
        email='amp-uts-api+vkmydo@apple.com',
        encrypted_password=b'SHhqaWp0anI3',
    ),
    AccountTypes.MCC1_BURNED: Account(  # showtime
        dsid='995000000728329978',
        cid='0a303a7bff0149258483aaa18db15126002',
    ),
    AccountTypes.MCC2_INTRO: Account(  # evergreen
        dsid='995000000629498143',
        cid='4f1c0d2dbd49400483b5da476390cdc1002',
        email='amp-uts-api+vkmydo@apple.com',
        encrypted_password=b'SHhqaWp0anI3',
    ),
    AccountTypes.MCC2_BURNED: Account(  # evergreen
        dsid='995000000729088892',
        cid='54d1652ef9ef4099a9a35d9ad80faea0002',
    ),
    # CIP offer eligible accounts
    AccountTypes.CIP_A1_PREMIER: Account(
        dsid='995000000703531408',
        cid='866241a50d104dd0aeba28e80852b20b002',

    ),
    AccountTypes.CIP_A1_FAMILY: Account(
        dsid='995000000703569667',
        cid='1023f34a673544afb22aa95248ed2da4002',
    ),
    AccountTypes.CIP_A1_INDIVIDUAL: Account(
        dsid='995000000452796527',
        cid='82f6a61447d248fb8fbf4e181dcd8394002',
    ),
    AccountTypes.CIP_HARD_BUNDLE: Account(
        dsid='995000000732342722',
        cid='d896b90a24174810a21c497cc0d74442002',
    ),
    AccountTypes.CIP_EXTENDED_OFFER: Account(
        dsid='995000000732342561',
        cid='a1ac83a1daa1419995374669e7b8a1de002',
    ),
    AccountTypes.CIP_BARCLAYSGB_FIN_ATV_HB: Account(
        dsid='995000000532350544',
        cid='09b87a997e684713838f0e29d1b37a38001',

    ),
    AccountTypes.CIP_TELUSCA_MVPD_ATV_HB: Account(
        dsid='995000000532352236',
        cid='38c1ce935dca45e482b2a0304f11b0b5001',
    ),
    AccountTypes.CIP_TELUSCA_MVPD_ATV_PMEO_6M: Account(
        dsid='995000000798381190',
        cid='3b976610e793459aae5c965b6a7e08e8002',
    ),
    AccountTypes.CIP_TOTALPLAYMX_MVPD_ATV_CPAID: Account(
        dsid='995000000530726343',
        cid='54e9ef373ba6453086bc85b646671dab001',
    ),
    AccountTypes.CIP_TOTALPLAYMX_MVPD_ATV_HB: Account(
        dsid='995000000798373944',
        cid='80ab78753d77442990b03a5527916841002',
    ),
    AccountTypes.CIP_TOTALPLAYMX_MVPD_ATV_PMEO_3M: Account(
        dsid='995000000798377492',
        cid='d24db8b1548a4a54970c10e070456b4f002',
    ),
    AccountTypes.CIP_CTUS_MVPD_ATV_CPAID: Account(
        dsid='998000005387961855',
        cid='83d929e391ff458e831961d3ee6ff963002',
    ),
    AccountTypes.CIP_CTUSXUMO_MVPD_ATV_CPAID: Account(
        dsid='998000005365121871',
        cid='94042b466d834b2eaaeb74018b95c80c002',
    ),

    AccountTypes.WITH_SPORT_FAVORITES: Account(
        dsid='995000000587751031',
        cid='d5e938cc6b9f41a1a278087a56c782c0002',
        protected=True
    ),
    ####################################################################################################################
    #                          Following 6 accounts are currently expired and not in use                               #
    ####################################################################################################################
    # 3PTV offer eligible accounts
    AccountTypes.PLAYSTATION4: Account(
        dsid='995000000466617864',
        cid='2ffb7d5445924a129be9cde9bed6db0d002',
        email='egyuzelyan+itms11+USA+2022-08-24-T-120736Z@apple.com',
    ),
    AccountTypes.PLAYSTATION5: Account(
        dsid='995000000717395253',
        cid='11da18c630ae4711b15a8bff69f2f3ca002',
        email='egyuzelyan+itms11+USA+2022-08-24-T-120830Z@apple.com',
    ),
    AccountTypes.VIZIO: Account(
        dsid='995000000798270351',
        cid='5ea25dbc3dd44e5a88774977ee9c61ae002',
        email='ekalimeris+itms11879722513@apple.com',
    ),
    ####################################################################################################################
    ####################################################################################################################
    ####################################################################################################################
    AccountTypes.LG: Account(
        dsid='995000000476766377',
        cid='b56a458a23d04e929c2710356b49bc4d002',
        email='egyuzelyan+itms11+USA+2022-09-22-T-174740Z@apple.com',
    ),
    AccountTypes.TELSTRA: Account(
        dsid='995000000727550084',
        cid='f28dfec922d54a2daa0d3bd028c2b7f7001',
        email='egyuzelyan+itms11+usa+2022-09-22-t-175557z@apple.com',
    ),
    AccountTypes.COMCAST: Account(
        dsid='995000000756344878',
        cid='5f36023e84e24d91856cff912a1b141d001',
    ),

    AccountTypes.ITUNES_CONTENT_ENTITLED: Account(
        dsid='995000000803451322',
        cid='3bc9a2f27eab4a06933ac1e8db1bfdb6002',
        email='amp-uts-api+qpqxtt@apple.com'
    ),
    AccountTypes.USER_SETTINGS_TESTS: Account(
        dsid='995000000651385999',
        cid='26e3a24f1d5c40e38978ac68525aa4f0001',
        email='ase-uts-api@apple.com'
    ),
    AccountTypes.SHOW_CAUGHT_UP_CLEAN_SUBSCRIBED: Account(
        dsid='995000000754230835',
        cid='a9e5900235d84d20b664e6c1db5a1bc0001',
        email='uts-api-graves-user-abcde@apple.com',
        protected=True
    ),
    AccountTypes.SHOW_NEVER_WATCHED_SUBSCRIBED: Account(
        dsid='995000000488137196',
        cid='e365c0d2a2c24f1887f3a1d1a428cd02002',
        email='uts-api-graves-user-12345@apple.com',
        protected=True
    ),
    AccountTypes.SHOW_2_CAUGHT_UP_CLEAN_SUBSCRIBED: Account(
        dsid='995000000535541373',
        cid='c9c77d10988e41308affe8229cb1957f002',
        email='uts-api-morning-user-1234@apple.com',
        protected=True
    ),
    AccountTypes.SHOW_CAUGHT_UP_DIRTY_OLD_SUBSCRIBED: Account(
        #  User who caught up, but decided to go back to S1 longer than freshness threshold
        dsid='995000000754231938',
        cid='105d7ad834804a289165cb6d8c06f846002',
        email='uts-api-graves-user-qwerty@apple.com',
        protected=True
    ),
    AccountTypes.SHOW_CAUGHT_UP_DIRTY_NEW_SUBSCRIBED: Account(
        #  User who caught up, but decided to go back to S1 within freshness threshold
        dsid='995000000754232310',
        cid='be8bcec85e2f47b5ad5932e004f69c66002',
        email='uts-api-graves-user-asdf@apple.com',
        protected=True
    ),
    AccountTypes.SHOW_NOT_IN_COHORT_WATCHED_WITHIN_24HR_SUBSCRIBED: Account(
        #  User who didn't watch but decided to watch it within the freshness threshold
        dsid='995000000754234285',
        cid='0a9bb915196c439cb2e493496bc9c172002',
        email='uts-api-graves-user-zxcv@apple.com',
        protected=True
    ),
    AccountTypes.SHOW_NOT_IN_COHORT_WATCHED_LESS_THAN_15MIN_SUBSCRIBED: Account(
        #  User who watched less than 15 minutes of the show
        dsid='995000000488141221',
        cid='97da66ffbde04eeeb982744af7cdd04c002',
        email='uts-api-graves-user-0987@apple.com',
        protected=True
    ),
    AccountTypes.RECO_WITH_PLAY_ACTIVITY: Account(
        dsid='995000000326125353',
        cid='79f394ba6bf847658bac9b10c9c864fe001',
        protected=True
    ),
    AccountTypes.IN_ALL_COHORT_RULES: Account(
        dsid='995000000724813250',
        cid='6f3e746b5be1499ea36b7a9447160754002'
    ),
    AccountTypes.WITH_ITEMS_IN_UP_NEXT: Account(
        dsid='995000000493503275',
        cid='168ebc3ef7d144d6af7a2726c69a6fa8002',
        protected=True
    ),
    AccountTypes.WITH_BOX_SET_PURCHASE: Account(
        dsid='995000000754230835',
        cid='a9e5900235d84d20b664e6c1db5a1bc0001',
        email='uts-api-graves-user-abcde@apple.com',
        protected=True
    ),
    AccountTypes.SPORTS_TASTE_PROFILE: Account(
        dsid='998000005368230397',
        cid='4b74964ca79f4cf1a135a34f1ad915fc002'
    ),
    # dummy account for unit test
    AccountTypes.DUMMY_PROTECTED_ACCOUNT: Account(
        dsid='12345',
        cid='1234567890',
        protected=True
    ),
    AccountTypes.UP_NEXT_TESTS: Account(
        dsid='995000000653926845',
        cid='fde4489e233b42a68f43d9d9e50ae901002',
        email='amp-uts-api+hwqugk@apple.com',
        encrypted_password=b'WGx4anJscGsx'
    ),
    AccountTypes.CONTINUE_WATCHING_TESTS: Account(
        dsid='998000005396488165',
        cid='9da0cd0936fe4bb4accb576af8e01d04002',
        protected=False,
        email='ase-uts-api+dnwida@apple.com',
        encrypted_password=b'TmZxbXdja2U2'
    ),

    AccountTypes.CONTINUE_WATCHING_TESTS_PRESET: Account(
        dsid='995000000630525409',
        cid='dc96cacaa98a4aa399393216c7693036001',
        protected=True
    ),

    AccountTypes.ADULT_SIMPLE_PROFILE: Account(
        dsid='2211000001530174',
        cid='626a3adf20ad45beb4f60bd447152026002',
        protected=False
    ),

    AccountTypes.CHILD_SIMPLE_PROFILE: Account(
        dsid='2211000001530567',
        cid='b95b636a3f784ea384a14000df7c7aee002',
        protected=False
    ),

    AccountTypes.SPONSOR_ACCOUNT_WITH_SIMPLE_PROFILES: Account(
        dsid='998000005426468592',
        cid='9557262f410e4d4987cdce1dfbfb6b04001',
        protected=False
    )
}
