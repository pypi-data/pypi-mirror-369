from dataclasses import dataclass, field


@dataclass
class LocaleInfo:
    locale: str = ''
    country_alpha2_code: str = ''
    country_alpha3_code: str = ''
    store_front: int = 0
    language: str = ''
    rating_systems: list = field(default_factory=list)


en_US = LocaleInfo(
    locale='en-US',
    country_alpha2_code='US',
    country_alpha3_code='USA',
    store_front=143441,
    language='en',
    rating_systems=['US_TV', 'MPAA']
)
es_US = LocaleInfo(
    locale='es-US',
    country_alpha2_code='US',
    country_alpha3_code='USA',
    store_front=143441,
    language='es'
)
en_CA = LocaleInfo(
    locale='en-CA',
    country_alpha2_code='CA',
    country_alpha3_code='CAN',
    store_front=143455,
    language='en'
)
fr_CA = LocaleInfo(
    locale='fr-CA',
    country_alpha2_code='CA',
    country_alpha3_code='CAN',
    store_front=143455,
    language='fr'
)
en_GB = LocaleInfo(
    locale='en-GB',
    country_alpha2_code='GB',
    country_alpha3_code='GBR',
    store_front=143444,
    language='en',
    rating_systems=['UK_TV', 'BBFC']
)
fr_FR = LocaleInfo(
    locale='fr-FR',
    country_alpha2_code='FR',
    country_alpha3_code='FRA',
    store_front=143442,
    language='fr'
)
de_DE = LocaleInfo(
    locale='de-DE',
    country_alpha2_code='DE',
    country_alpha3_code='DEU',
    store_front=143443,
    language='de'
)
ja_JP = LocaleInfo(
    locale='ja-JP',
    country_alpha2_code='JP',
    store_front=143462,
    language='ja'
)
en_TR = LocaleInfo(
    locale='en-TR',
    country_alpha2_code='TR',
    store_front=143480,
    language='en'
)
en_BN = LocaleInfo(
    locale='en-BN',
    country_alpha2_code='BN',
    store_front=143560,
    language='en'
)
pt_BR = LocaleInfo(
    locale='pt-BR',
    country_alpha2_code='BR',
    store_front=143503,
    language='pt'
)
pt_PT = LocaleInfo(
    locale='pt-PT',
    country_alpha2_code='PT',
    store_front=143453,
    language='pt'
)
ko_KR = LocaleInfo(
    locale='ko-KR',
    country_alpha2_code='KR',
    store_front=143466,
    language='ko'
)
en_AU = LocaleInfo(
    locale='en-AU',
    country_alpha2_code='AU',
    store_front=143460,
    language='en'
)
es_MX = LocaleInfo(
    locale='es-MX',
    country_alpha2_code='MX',
    store_front=143468,
    language='es'
)
en_HK = LocaleInfo(
    locale='en-HK',
    country_alpha2_code='HK',
    store_front=143463,
    language='en'
)
en_SG = LocaleInfo(
    locale='en-SG',
    country_alpha2_code='SG',
    store_front=143464,
    language='en'
)
sv_SE = LocaleInfo(
    locale='sv-SE',
    country_alpha2_code='SE',
    store_front=143456,
    language='sv'
)
en_NZ = LocaleInfo(
    locale='en-AU',
    country_alpha2_code='NZ',
    store_front=143461,
    language='en'
)
en_IN = LocaleInfo(
    locale='en-GB',
    country_alpha2_code='IN',
    store_front=143467,
    language='en'
)
hi_IN = LocaleInfo(
    locale='hi-IN',
    country_alpha2_code='IN',
    store_front=143467,
    language='en'
)
es_ES = LocaleInfo(
    locale='es-ES',
    country_alpha2_code='ES',
    country_alpha3_code='ESP',
    store_front=143454,
    language='es'
)
ar_SA = LocaleInfo(
    locale='ar_SA',
    country_alpha2_code='SA',
    store_front=143479,
    language='ar'
)
nl_NL = LocaleInfo(
    locale='nl_NL',
    country_alpha2_code='NL',
    country_alpha3_code='NLD',
    store_front=143452,
    language='nl'
)
nb_NO = LocaleInfo(
    locale='nb_NO',
    country_alpha2_code='NO',
    store_front=143457,
    language='nb'
)
pl_PL = LocaleInfo(
    locale='pl_PL',
    country_alpha2_code='PL',
    store_front=143478,
    language='pl'
)
sl_SI = LocaleInfo(
    locale='sl_SI',
    country_alpha2_code='SI',
    country_alpha3_code='SVN',
    store_front=143499,
    language='sl'
)

# invalid locale for test purposes
zz_ZZ = LocaleInfo(
    locale='zz_ZZ',
    country_alpha2_code='ZZ',
    store_front=111111,
)
vi_VI = LocaleInfo(
    locale='vi_VI',
    country_alpha2_code='VN'
)
ru_RU = LocaleInfo(
    locale='ru_RU',
    country_alpha2_code='RU',
    country_alpha3_code='RU',
    store_front=143469
)

uk_UA = LocaleInfo(
    locale='uk_UA',
    country_alpha2_code='UA',
    country_alpha3_code='UA',
    store_front=143492
)

MLS_LOCALES: list[LocaleInfo] = [en_US, es_US]


def get_locale_key(locale_info: LocaleInfo, key: str):
    if not isinstance(locale_info, LocaleInfo):
        raise ValueError("Invalid locale information")
    try:
        return getattr(locale_info, key)
    except AttributeError:
        raise ValueError(f"Key '{key}' not found in LocaleInfo")


def get_locale(locale_info: LocaleInfo):
    return get_locale_key(locale_info, 'locale')


def get_language(locale_info: LocaleInfo):
    return get_locale_key(locale_info, 'language')


def get_country_alpha2_code(locale_info: LocaleInfo):
    return get_locale_key(locale_info, 'country_alpha2_code')


def get_country_alpha3_code(locale_info: LocaleInfo):
    return get_locale_key(locale_info, 'country_alpha3_code')
