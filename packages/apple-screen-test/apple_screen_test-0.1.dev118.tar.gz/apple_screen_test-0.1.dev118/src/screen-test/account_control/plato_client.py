from ampplato.client import AccountsClient

buy_params_map = {
    'mls_monthly': 'offerName=MLS_Season_Pass_1month&offrd-free-trial=false&price=19990&pg=default&appExtVrsId'
                   '=833519801&salableAdamId=1472441559&pricingParameters=STDQ&bid=com.apple.tv&productType=A'
                   '&appAdamId=1174078549',
    'mls_annually': 'offerName=MLS_Season_Pass_1season&offrd-free-trial=false&price=119990&pg=default&appExtVrsId'
                    '=833519801&salableAdamId=6445132219&pricingParameters=STDQ&bid=com.apple.tv&productType=A'
                    '&appAdamId=1174078549',
    'chapman_team_monthly': 'offerName=TexasRangers_1month&offrd-free-trial=false&price=19000&pg=default&'
                            'appExtVrsId=860384852&salableAdamId=10788601661&pricingParameters=STDQ&'
                            'bid=com.apple.tv&productType=A&appAdamId=1174078549',
    'chapman_team_season': 'offerName=TexasRangers_1season&offrd-free-trial=false&price=99000&pg=default&'
                           'appExtVrsId=860384852&salableAdamId=10788601683&pricingParameters=STDQ&'
                           'bid=com.apple.tv&productType=A&appAdamId=1174078549',
    'chapman_league_monthly': 'offerName=Chapman_1month&offrd-free-trial=false&price=39000&pg=default&'
                              'appExtVrsId=860384852&salableAdamId=10788601949&pricingParameters=STDQ&'
                              'bid=com.apple.tv&productType=A&appAdamId=1174078549',
    'chapman_league_season': 'offerName=Chapman_1season&offrd-free-trial=false&price=199000&pg=default&'
                             'appExtVrsId=860384852&salableAdamId=10788601924&pricingParameters=STDQ&'
                             'bid=com.apple.tv&productType=A&appAdamId=1174078549',
    'chapman_padres': 'offerName=SanDiegoPadres_1season&offrd-free-trial=false&price=99000&pg=default&'
                      'appExtVrsId=860384852&salableAdamId=10788601682&pricingParameters=STDQ&'
                      'bid=com.apple.tv&productType=A&appAdamId=1174078549',
    'chapman_astros': 'offerName=HoustonAstros_1season&offrd-free-trial=false&price=99000&pg=default&'
                      'appExtVrsId=860384852&salableAdamId=10788601669&pricingParameters=STDQ&'
                      'bid=com.apple.tv&productType=A&appAdamId=1174078549',
    'chapman_rangers': 'offerName=TexasRangers_1season&offrd-free-trial=false&price=99000&pg=default&'
                       'appExtVrsId=860384852&salableAdamId=10788601683&pricingParameters=STDQ&'
                       'bid=com.apple.tv&productType=A&appAdamId=1174078549',
    'chapman_oom': 'offerName=Chapman_oom_1month&offrd-free-trial=false&price=35000&pg=default&'
                   'appExtVrsId=860384852&salableAdamId=10790120869&pricingParameters=STDQ&'
                   'bid=com.apple.tv&productType=A&appAdamId=1174078549',
    'showtime': 'offerName=Showtime_1month_001&offrd-free-trial=true&price=10990&pg=default&appExtVrsId=833519801'
                '&salableAdamId=1455895207&pricingParameters=STDQ&bid=com.apple.tv&productType=A&appAdamId=1174078549',
    'evergreen': 'offerName=EvergreenIAP&offrd-free-trial=true&price=490&pg=default&appExtVrsId=833519801'
                 '&salableAdamId=2000253401&pricingParameters=STDQ&bid=com.apple.tv&productType=A&appAdamId=1174078549',
    'paramount_plus': 'offerName=AppleTVPlus_1month_001&offrd-free-trial=true&price=6990&pg=default&appExtVrsId'
                      '=2000185991&salableAdamId=1472441559&pricingParameters=STDQ&bid=com.apple.tv&productType=A'
                      '&appAdamId=1174078549',
    'epix': 'offerName=Epix_1month_001&offrd-free-trial=true&price=8990&pg=default&appExtVrsId=2000185991'
            '&salableAdamId=1455894781&pricingParameters=STDQ&bid=com.apple.tv&productType=A&appAdamId=1174078549',
}


class PlatoClient(AccountsClient):

    def buy_tv_plus_add_on_subscription(self, email, add_on_subscription, password):
        return self.buy_product_by_pricing_parameters(email, buy_params_map[add_on_subscription], password,
                                                      is_latest_ios=True)
