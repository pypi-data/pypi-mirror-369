'''
This Config outlines the structure for various fetches from different tables including the mandatory parameters,
the primary key and the data that will be returned from the fetch. The use of this config can be found in the
database_fetches.py file
'''
from enum import Enum
from typing import Any, Type, List, Dict

from test_data_classes import Account, Collection, Canvas, Context, UTSOffer, Content, UMCContent, Episode, BoxSet, \
    SportingEvent, Sport, League, Person, Campaign, UMCContentType, MOVIE, TV_SHOW, EPISODE, SEASON, MOVIE_BUNDLE, \
    LIVE_SPORTING_EVENT, UPCOMING_SPORTING_EVENT, PAST_SPORTING_EVENT, STATIC_SPORTING_EVENT, EXTRA, BOX_SET, \
    LIVE_SERVICE
from test_data_keys import AccountTypes, CollectionNames, CanvasNames, DisplayTypes, UTSOfferTypes, SportNames, \
    LeagueNames, PersonNames, CampaignNames, CompetitorNames, CanvasTypes, ContentTypes

from database_manager import logger

"""
Config for structured fetches from DB
Style:
    table or style name: {
        table_name: the name of the table in the db
        schema: the database name ("screentest")
        object_class: the dataclass object to build (found in test_data_classes.py)
        enum_class: the enum type (found in test_data_keys.py)
        enum_key_column: the name where the enum type can be found in the table (as a string)
        object_constructor_mapping: the structure to map information from the database to the desired object
        any custom normalizers labelled as a factory because they normalize information in a
        custom built way (i.e. collection_items_normalizer_factory)
    }
"""


def normalize_db_string_field_or_None(value_from_db) -> str | None:
    """Converts DB value (None, '', '""') to default string value"""
    if value_from_db is None:
        return None
    if isinstance(value_from_db, str) and value_from_db == '""':
        return None
    return str(value_from_db)

def normalize_db_string_field_or_Empty(value_from_db) -> str:
    """Converts DB value (None, '', '""') to default string value"""
    if value_from_db is None:
        return ""
    if isinstance(value_from_db, str) and value_from_db == '""':
        return ""
    return str(value_from_db)


def normalize_db_string_field_to_umc_content_type(value_from_db) -> None | UMCContentType | ContentTypes:
    """Converts DB value for UMC Content Type to valid UMCContentType"""

    UMC_CONTENT_TYPE_MAP: Dict[str, UMCContentType] = {
        MOVIE.name: MOVIE,
        TV_SHOW.name: TV_SHOW,
        EPISODE.name: EPISODE,
        SEASON.name: SEASON,
        MOVIE_BUNDLE.name: MOVIE_BUNDLE,
        LIVE_SPORTING_EVENT.name: LIVE_SPORTING_EVENT,
        UPCOMING_SPORTING_EVENT.name: UPCOMING_SPORTING_EVENT,
        PAST_SPORTING_EVENT.name: PAST_SPORTING_EVENT,
        STATIC_SPORTING_EVENT.name: STATIC_SPORTING_EVENT,
        EXTRA.name: EXTRA,
        BOX_SET.name: BOX_SET,
        LIVE_SERVICE.name: LIVE_SERVICE,
    }
    if value_from_db in UMC_CONTENT_TYPE_MAP:
        return UMC_CONTENT_TYPE_MAP[value_from_db]
    return None

def normalize_db_string_field_to_uts_content_type(value_from_db)-> ContentTypes| None:
    if value_from_db is None or value_from_db =="":
        return None
    return ContentTypes(value_from_db)

def normalize_db_string_field_to_canvas_type(value_from_db) -> CanvasTypes | None:
    """Converts DB value for UMC Content Type to valid UMCContentType"""

    if value_from_db is None:
        return None
    if isinstance(value_from_db, str) and value_from_db == '""':
        return None
    return CanvasTypes[value_from_db]

def normalize_db_string_field_to_canvas_names(value_from_db) -> CanvasNames | None:
    """Converts DB value for UMC Content Type to valid UMCContentType"""

    if value_from_db is None:
        return None
    if isinstance(value_from_db, str) and value_from_db == '""':
        return None
    return CanvasNames[value_from_db]

def normalize_db_bytes_field(value_from_db) -> bytes:
    """Converts DB BYTEA value (None or bytes) to default bytes value """
    if value_from_db is None:
        return b''  # DB NULL -> empty bytes
    return bytes(value_from_db)


def normalize_db_boolean_field(value_from_db) -> bool:
    return bool(value_from_db)


def normalize_db_enum_field(value: Any, enum_class: Type[Enum]) -> Any:
    """
    Normalizer specifically for enum fields.
    It takes the raw value and the target Enum class.
    """
    if value is None:
        return None
    try:
        return enum_class[str(value)]
    except Exception as e:
        logger.error(f"Error converting '{value}' to enum {enum_class.__name__}: {e}")
        return None


def normalize_db_jsonb_list_of_enums(value: Any or None, enum_class: Type[Enum]) -> List[Enum]:
    if value is None:
        return []
    if not isinstance(value, list):
        logger.error(f"Expected a list for JSONB list of enums, but got {type(value)}: {value}")
        return []

    result_list = []
    for item in value:
        enum_member = normalize_db_enum_field(item, enum_class)
        if enum_member is not None:
            result_list.append(enum_member)
    return result_list


def normalize_db_jsonb_dict_of_strings(value: Any) -> Dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        logger.error(f"Expected a dictionary for JSONB dict of strings, but got {type(value)}: {value}")
        return {}
    return {str(k): str(v) for k, v in value.items() if k is not None and v is not None}


def normalize_db_jsonb_list_of_strings(value: Any) -> List[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        logger.error(f"Expected a list for JSONB list of strings, but got {type(value)}: {value}")
        return []
    return [str(item) for item in value if item is not None]


DB_TABLE_CONFIG = {
    "account": {
        "table_name": "account",
        "schema": "screentest",
        "object_class": Account,
        "enum_class": AccountTypes,
        "enum_key_column": "account_type",
        "primary_key": "account_uuid",
        "object_constructor_mapping": {
            "dsid": {"db_column": "dsid", "normalizer": normalize_db_string_field_or_Empty},
            "cid": {"db_column": "cid", "normalizer": normalize_db_string_field_or_Empty},
            "email": {"db_column": "email", "normalizer": normalize_db_string_field_or_Empty},
            "encrypted_password": {"db_column": "encrypted_password", "normalizer": normalize_db_bytes_field},
            "protected": {"db_column": "protected", "normalizer": normalize_db_boolean_field}
        }
    },
    "display": {
        "table_name": "display",
        "schema": "screentest",
        "primary_key": "display_uuid",
        "object_class": Context,
        "enum_class": DisplayTypes,
        "enum_key_column": "display_type",
        "object_constructor_mapping": {
            "root": {"db_column": "root", "normalizer": normalize_db_string_field_or_Empty},
            "shelf": {"db_column": "shelf", "normalizer": normalize_db_string_field_or_Empty},
            "canvas": {"db_column": "canvas", "normalizer": normalize_db_string_field_or_Empty},
            "flavor": {"db_column": "flavor","normalizer": normalize_db_string_field_or_Empty},
            "brand": {"db_column": "brand"}

        }
    },

    "display_by_uuid": {
        "table_name": "display",
        "schema": "screentest",
        "primary_key": "display_uuid",
        "object_class": Context,
        "key_column": "display_uuid",
        "object_constructor_mapping": {
            "root": {"db_column": "root", "normalizer": normalize_db_string_field_or_Empty},
            "shelf": {"db_column": "shelf", "normalizer": normalize_db_string_field_or_Empty},
            "canvas": {"db_column": "canvas", "normalizer": normalize_db_string_field_or_Empty},
            "display_type": {"db_column": "display_type", "normalizer": lambda val: normalize_db_enum_field(value=val, enum_class=DisplayTypes)},
            "flavor": {"db_column": "flavor", "normalizer": normalize_db_string_field_or_Empty},
            "brand": {"db_column": "brand", "normalizer": normalize_db_string_field_or_Empty}
        }
    },

    "collection": {
        "table_name": "collection",
        "schema": "screentest",
        "primary_key": "collection_uuid",
        "object_class": Collection,
        "enum_class": CollectionNames,
        "enum_key_column": "collection_name",
        "object_constructor_mapping": {
            "collection_id": {"db_column": "collection_id", "normalizer": normalize_db_string_field_or_Empty},
            "category_name": {"db_column": "category_name", "normalizer": normalize_db_string_field_or_Empty},
            "items": {"db_column": "items", "normalizer": normalize_db_jsonb_list_of_strings},
            "conductor_published_id": {"db_column": "conductor_published_id",
                                       "normalizer": normalize_db_string_field_or_Empty},
            "context_ids": {"db_column": "context_ids", "normalizer": "context_ids_normalizer_factory"}
        }
    },
    "collection_by_id": {
        "table_name": "collection",
        "schema": "screentest",
        "primary_key": "collection_id",
        "object_class": Collection,
        "key_column": "collection_id",
        "object_constructor_mapping": {
            "collection_id": {"db_column": "collection_id", "normalizer": normalize_db_string_field_or_Empty},
            "category_name": {"db_column": "title", "normalizer": normalize_db_string_field_or_Empty},
            "items": {"db_column": "category", "normalizer": normalize_db_jsonb_list_of_strings},
            "conductor_published_id": {"db_column": "conductor_published_id",
                                       "normalizer": normalize_db_string_field_or_Empty},
            "context_ids": {"db_column": "context_ids", "normalizer": "context_ids_normalizer_factory"}
        }
    },
    "canvas": {
        "table_name": "canvas",
        "schema": "screentest",
        "primary_key": "canvas_uuid",
        "object_class": Canvas,
        "enum_class": CanvasNames,
        "enum_key_column": "canvas_name",
        "object_constructor_mapping": {
            "id": {"db_column": "id", "normalizer": normalize_db_string_field_or_Empty},
            "child_ids": {"db_column": "child_ids", "normalizer": normalize_db_jsonb_list_of_strings},
            "is_first_party": {"db_column": "is_first_party", "normalizer": normalize_db_boolean_field},
            "name": {"db_column": "name", "normalizer": normalize_db_string_field_or_Empty},
            "bundle_id": {"db_column": "bundle_id", "normalizer": normalize_db_string_field_or_None},
            "vod_service": {"db_column": "vod_service", "normalizer": normalize_db_string_field_or_Empty},
            "external_service_id": {"db_column": "external_service_id", "normalizer": normalize_db_string_field_or_Empty},
            "salable_adam_id": {"db_column": "salable_adam_id", "normalizer": normalize_db_string_field_or_Empty},
            "up_next_fallback": {"db_column": "up_next_fallback", "normalizer": normalize_db_jsonb_dict_of_strings},
            "parent_id": {"db_column": "parent_id", "normalizer": normalize_db_string_field_or_None},
            "canvas_type": {"db_column": "canvas_type", "normalizer": normalize_db_string_field_to_canvas_type},
            "salable_adam_id_out_market": {"db_column": "salable_adam_id_out_market",
                                           "normalizer": normalize_db_string_field_or_Empty},
            "salable_adam_id_in_market": {"db_column": "salable_adam_id_in_market",
                                          "normalizer": normalize_db_string_field_or_Empty},
            "external_id": {"db_column": "external_id", "normalizer": normalize_db_string_field_or_Empty},
            "media_content": {"db_column": "media_content", "normalizer": "media_content_normalizer_factory"},
            "shelves_under_test": {"db_column": "shelves_under_test", "normalizer": normalize_db_jsonb_dict_of_strings},
            "is_sports_dynamic": {"db_column": "is_sports_dynamic", "normalizer": normalize_db_boolean_field},
            "locale_info": {"db_column": "locale_info", "normalizer": normalize_db_jsonb_dict_of_strings},
            "brand_equivalence_id": {"db_column": "brand_equivalence_id", "normalizer": normalize_db_string_field_or_Empty},
            "is_enabled_for_editorial_featuring": {"db_column": "is_enabled_for_editorial_featuring",
                                                   "normalizer": normalize_db_boolean_field},
            "expected_shelf_displayType_pairs": {"db_column": "expected_shelf_display_type_pairs",
                                                 "normalizer": normalize_db_jsonb_dict_of_strings},
            "collection_items": {"db_column": "collection_items", "normalizer": "collection_items_normalizer_factory"}
        }
    },
    "uts_offer": {
        "table_name": "uts_offer",
        "schema": "screentest",
        "object_class": UTSOffer,
        "enum_class": UTSOfferTypes,
        "enum_key_column": "uts_offer_name",
        "primary_key": "uts_offer_uuid",
        "object_constructor_mapping": {
            "ad_hoc_offer_id": {"db_column": "ad_hoc_offer_id", "normalizer": normalize_db_string_field_or_Empty},
            "free_duration_period": {"db_column": "free_duration_period", "normalizer": normalize_db_string_field_or_Empty},
            "offer_intent": {"db_column": "offer_intent", "normalizer": normalize_db_string_field_or_Empty},
            "device_purchased": {"db_column": "device_purchased", "normalizer": normalize_db_string_field_or_Empty},
            "provider_name": {"db_column": "provider_name", "normalizer": normalize_db_string_field_or_Empty},
            "eligibility_type": {"db_column": "eligibility_type", "normalizer": normalize_db_string_field_or_Empty},
            "carrier_name": {"db_column": "carrier_name", "normalizer": normalize_db_string_field_or_Empty},
            "product_code": {"db_column": "product_code", "normalizer": normalize_db_string_field_or_Empty},
            "adam_id": {"db_column": "adam_id", "normalizer": normalize_db_string_field_or_None},
            "subscription_bundle_id": {"db_column": "subscription_bundle_id", "normalizer": normalize_db_string_field_or_Empty},
            "offer_type": {"db_column": "general_offer_type", "normalizer": normalize_db_string_field_or_Empty},
            "offer_name": {"db_column": "offer_name", "normalizer": normalize_db_string_field_or_Empty},
            "account_types": {
                "db_column": "account_types",
                "normalizer": lambda value: normalize_db_jsonb_list_of_enums(value, AccountTypes)
            }
        }
    },
    "movie": {
        "table_name": "movie",
        "schema": "screentest",
        "primary_key": "movie_uuid",
        "object_class": UMCContent,
        "key_class": str,
        "key_column": "movie_element_name",
        "object_constructor_mapping": {
            "id": {"db_column": "id", "normalizer": normalize_db_string_field_or_Empty},
            "name": {"db_column": "name", "normalizer": normalize_db_string_field_or_Empty},
            "type": {"db_column": "umc_content_type", "normalizer": normalize_db_string_field_to_umc_content_type},
            "required_entitlement": {"db_column": "required_entitlement",
                                     "normalizer":  lambda value: normalize_db_jsonb_list_of_enums(value, CanvasNames)},
            "adam_id": {"db_column": "adam_id", "normalizer": normalize_db_string_field_or_None},
            "description": {"db_column": "description", "normalizer": normalize_db_string_field_or_None},
            "related_content": {"db_column": "related_content", "normalizer": normalize_db_jsonb_dict_of_strings},
        }
    },

    "tv_show": {
        "table_name": "tv_show",
        "schema": "screentest",
        "primary_key": "tv_show_uuid",
        "object_class": UMCContent,
        "key_class": str,
        "key_column": "tv_show_element_name",
        "object_constructor_mapping": {
            "id": {"db_column": "id", "normalizer": normalize_db_string_field_or_Empty},
            "name": {"db_column": "name", "normalizer": normalize_db_string_field_or_Empty},
            "type": {"db_column": "umc_content_type", "normalizer": normalize_db_string_field_to_umc_content_type},
            "required_entitlement": {"db_column": "required_entitlement",
                                     "normalizer": lambda value: normalize_db_jsonb_list_of_enums(value, CanvasNames)},
            "adam_id": {"db_column": "adam_id", "normalizer": normalize_db_string_field_or_None},
            "description": {"db_column": "description", "normalizer": normalize_db_string_field_or_None},
            "related_content": {"db_column": "related_content", "normalizer": normalize_db_jsonb_dict_of_strings},
        }
    },

    "season": {
        "table_name": "season",
        "schema": "screentest",
        "primary_key": "season_uuid",
        "object_class": UMCContent,
        "key_class": str,
        "key_column": "season_element_name",
        "object_constructor_mapping": {
            "id": {"db_column": "id", "normalizer": normalize_db_string_field_or_Empty},
            "name": {"db_column": "name", "normalizer": normalize_db_string_field_or_Empty},
            "type": {"db_column": "umc_content_type", "normalizer": normalize_db_string_field_to_umc_content_type},
            "adam_id": {"db_column": "adam_id", "normalizer": normalize_db_string_field_or_None},
            "description": {"db_column": "description", "normalizer": normalize_db_string_field_or_None},
        }
    },
    "episode": {
        "table_name": "episode",
        "schema": "screentest",
        "primary_key": "episode_uuid",
        "object_class": Episode,
        "key_class": str,
        "key_column": "content_name",
        "object_constructor_mapping": {
            "id": {"db_column": "id", "normalizer": normalize_db_string_field_or_Empty},
            "name": {"db_column": "name", "normalizer": normalize_db_string_field_or_Empty},
            "type": {"db_column": "umc_content_type", "normalizer": normalize_db_string_field_to_umc_content_type},
            "show_id": {"db_column": "show_id", "normalizer": normalize_db_string_field_or_Empty},
            "adam_id":{"db_column": "adam_id", "normalizer": normalize_db_string_field_or_Empty},
            "required_entitlement": {"db_column": "required_entitlement",
                                     "normalizer": lambda value: normalize_db_jsonb_list_of_enums(value, CanvasNames)},
        }
    },

    "other": {
        "table_name": "other",
        "schema": "screentest",
        "primary_key": "other_uuid",
        "key_class": str,
        "key_column": "other_element_name",
        "class_mappings": {  # Maps values from 'content_type' to their respective class and constructor mapping
            "DEFAULT": {
                "object_class": UMCContent,
                "constructor_mapping": {
                    "id": {"db_column": "id", "normalizer": normalize_db_string_field_or_Empty},
                    "name": {"db_column": "name", "normalizer": normalize_db_string_field_or_Empty},
                    "type": {"db_column": "content_type", "normalizer": normalize_db_string_field_to_umc_content_type},
                    "required_entitlement": {"db_column": "required_entitlement",
                                             "normalizer": lambda value: normalize_db_jsonb_list_of_enums(value, CanvasNames)},

                    "adam_id": {"db_column": "adam_id", "normalizer": normalize_db_string_field_or_None},
                    "secondary_id": {"db_column": "secondary_id", "normalizer": normalize_db_string_field_or_None},

                }
            },
            "BOX_SET": {
                "object_class": BoxSet,
                "constructor_mapping": {
                    "id": {"db_column": "id", "normalizer": normalize_db_string_field_or_Empty},
                    "name": {"db_column": "name", "normalizer": normalize_db_string_field_or_Empty},
                    "type": {"db_column": "content_type", "normalizer": normalize_db_string_field_to_umc_content_type},
                    "adam_id": {"db_column": "adam_id", "normalizer": normalize_db_string_field_or_None},
                    "secondary_id": {"db_column": "secondary_id", "normalizer": normalize_db_string_field_or_None},
                    "show_id": {"db_column": "show_id", "normalizer": normalize_db_string_field_or_Empty},
                    "required_entitlement": {"db_column": "required_entitlement",
                                             "normalizer": lambda value: normalize_db_jsonb_list_of_enums(value, CanvasNames)},
                }
            },
        }
    },
    "sporting_event": {
        "table_name": "sporting_event",
        "schema": "screentest",
        "primary_key": "sporting_event_uuid",
        "object_class": SportingEvent,
        "key_class": str,
        "key_column": "event_name",
        "object_constructor_mapping": {
            "id": {"db_column": "id", "normalizer": normalize_db_string_field_or_Empty},
            "name": {"db_column": "name", "normalizer": normalize_db_string_field_or_Empty},
            "type": {"db_column": "umc_content_type", "normalizer": normalize_db_string_field_to_umc_content_type},
            "league_name": {"db_column": "league_name", "normalizer": normalize_db_string_field_or_Empty},
            "required_entitlement": {"db_column": "required_entitlement",
                                     "normalizer": lambda value: normalize_db_jsonb_list_of_enums(value, CanvasNames)},
        }
    },
    "sports_teams": {
        "table_name": "sports_teams",
        "schema": "screentest",
        "primary_key": "sports_team_uuid",
        "object_class": UMCContent,
        "key_class": str,
        "key_column": "event_name",
        "object_constructor_mapping": {
            "id": {"db_column": "id", "normalizer": normalize_db_string_field_or_Empty},
            "name": {"db_column": "name", "normalizer": normalize_db_string_field_or_Empty},
            "type": {"db_column": "type", "normalizer": normalize_db_string_field_to_uts_content_type},
            "required_entitlement": {"db_column": "required_entitlement",
                                     "normalizer": lambda value: normalize_db_jsonb_list_of_enums(value, CanvasNames)},
            "adam_id_monthly": {"db_column":"adam_monthly_id", "normalizer": normalize_db_string_field_or_Empty},
            "adam_id_seasonal": {"db_column":"adam_seasonal_id", "normalizer": normalize_db_string_field_or_Empty},
        }
    },
    "live_events": {
        "table_name": "live_events",
        "schema": "screentest",
        "primary_key": "live_event_uuid",
        "object_class": UMCContent,
        "key_class": str,
        "key_column": "event_name",
        "object_constructor_mapping": {
            "id": {"db_column": "id", "normalizer": normalize_db_string_field_or_Empty},
            "name": {"db_column": "name", "normalizer": normalize_db_string_field_or_Empty},
            "type": {"db_column": "type", "normalizer": normalize_db_string_field_to_uts_content_type},
            "required_entitlement": {"db_column": "required_entitlement",
                                     "normalizer": lambda value: normalize_db_jsonb_list_of_enums(value, CanvasNames)},
        }
    },
    "sports": {
        "table_name": "sports",
        "schema": "screentest",
        "primary_key": "sport_uuid",
        "object_class": Sport,
        "key_class": SportNames,
        "key_column": "sport_type",
        "object_constructor_mapping": {
            "id": {"db_column": "umc_id", "normalizer": normalize_db_string_field_or_Empty},
            "name": {"db_column": "name", "normalizer": normalize_db_string_field_or_Empty},
            "umc_tag": {"db_column": "umc_tag", "normalizer": normalize_db_string_field_or_Empty},
        }
    },

    "leagues": {
        "table_name": "leagues",
        "schema": "screentest",
        "primary_key": "league_uuid",
        "object_class": League,
        "key_class": LeagueNames,
        "key_column": "league_initials",
        "object_constructor_mapping": {
            "id": {"db_column": "umc_id", "normalizer": normalize_db_string_field_or_Empty},
            "name": {"db_column": "league_full_name", "normalizer": normalize_db_string_field_or_Empty},
            "competitors": {
                "db_column": "competitors",
                "normalizer": "competitor_normalizer_factory",
            },
            "related_content": {"db_column": "related_content", "normalizer": normalize_db_jsonb_dict_of_strings},
        }
    },
    "persons": {
        "table_name": "persons",
        "schema": "screentest",
        "primary_key": "name",
        "object_class": Person,
        "key_class": PersonNames,
        "key_column": "name",
        "object_constructor_mapping": {
            "id": {"db_column": "umc_id", "normalizer": normalize_db_string_field_or_Empty},
            "name": {"db_column": "full_name", "normalizer": normalize_db_string_field_or_Empty},
        }
    },
    "campaigns": {
        "table_name": "campaigns",
        "schema": "screentest",
        "primary_key": "campaign_type",
        "object_class": Campaign,
        "key_class": CampaignNames,
        "key_column": "campaign_type",
        "object_constructor_mapping": {
            "id": {"db_column": "uts_id", "normalizer": normalize_db_string_field_or_Empty},
            "user_id": {"db_column": "user_id", "normalizer": normalize_db_string_field_or_Empty},
        }
    },

    "competitors": {
        "table_name": "competitors",
        "schema": "screentest",
        "primary_key": "competitor_uuid",
        "object_class": UMCContent,
        "key_class": CompetitorNames,
        "key_column": "competitor_team",
        "object_constructor_mapping": {
            "id": {"db_column": "umc_id", "normalizer": normalize_db_string_field_or_Empty},
            "name": {"db_column": "competitor_team_name", "normalizer": normalize_db_string_field_or_Empty},
            "type": {"db_column": "content_data_type", "normalizer": normalize_db_string_field_or_Empty},
            "related_content": {"db_column": "related_content", "normalizer": normalize_db_jsonb_dict_of_strings},
        }
    },

}
