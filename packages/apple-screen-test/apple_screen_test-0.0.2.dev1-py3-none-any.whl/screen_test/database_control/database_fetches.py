import logging
from enum import Enum
from typing import Dict, Any, Type, List

import psycopg2
from data_structures.test_data_classes import Account, Data, Collection, Canvas, UMCContent
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from test_data_classes import UTSOffer, Offer
from test_data_keys import AccountTypes, UTSOfferTypes, DisplayTypes, CollectionNames, CanvasNames, ContentDatas, \
    CompetitorNames

from database_fetch_config import DB_TABLE_CONFIG
from database_manager import DatabaseManager

# GLOBAL VARIABLES
logger = logging.getLogger(__name__)

'''
Recreating these data models
itms11_data_model = Data(
    ACCOUNTS=ACCOUNTS,
    CANVASES=CANVASES,
    COLLECTIONS=COLLECTIONS,
    CONTENT_DATAS=CONTENT_DATAS,
    DIRECT_ACCESS=direct_access,
    OFFERS=OFFERS,
    UTS_OFFERS=UTS_OFFERS,
)

prod_data_model = Data(
    ACCOUNTS=ACCOUNTS,
    CANVASES=CANVASES,
    COLLECTIONS=COLLECTIONS,
    CONTENT_DATAS=CONTENT_DATAS,
    DIRECT_ACCESS=direct_access,
    OFFERS={},
    UTS_OFFERS=UTS_OFFERS,
)

'''


def fetch_raw_table_data(db: DatabaseManager, style_name: str, environment: str) -> List[Dict] | None:
    """
    Fetches all raw rows for a given table and environment directly from the database.
    Returns a list of dictionaries, where each dictionary represents a row.
    """
    try:
        table_config = DB_TABLE_CONFIG[style_name]
        db_table_name = table_config["table_name"]
        db_schema = table_config.get("schema")

        with db.connection.cursor(cursor_factory=RealDictCursor) as cur:
            query = sql.SQL(
                """SELECT * FROM {schema}.{table} WHERE environment = %s;"""
            ).format(
                schema=sql.Identifier(db_schema),
                table=sql.Identifier(db_table_name)
            )
            results = execute_db_fetch(cur, query, (environment,), f"table {db_table_name}")
            return results
    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Database error while fetching raw data for table '{style_name}': {e}")
        raise
    except Exception as e:
        logger.error(f"[screen-test] - An unexpected error occurred in fetch_raw_table_data for '{style_name}': {e}")
        raise


def fetch_table(db: DatabaseManager, style_name: str, environment: str,
                extra_normalizer_context: Dict[str, Any] | None = None) -> Dict[Enum, Any] | None:
    """
    Fetches all rows for a given table, parses them into objects,
    and returns them in a dictionary keyed by an enum member.
    Also runs data through any normalizers for relational columns
    """
    try:
        raw_results = fetch_raw_table_data(db, style_name, environment)
        if not raw_results:
            return None

        table_config = DB_TABLE_CONFIG[style_name]
        enum_class = table_config["enum_class"]
        enum_key_column = table_config["enum_key_column"]

        new_collection = {}
        for row in raw_results:
            enum_key_value = row.get(enum_key_column)
            enum_member = enum_class[enum_key_value]
            new_collection[enum_member] = parse_single_db_row_to_object(
                row,
                table_config["object_class"],
                table_config["object_constructor_mapping"],
                style_name,
                extra_normalizer_context
            )
        return new_collection
    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Database error while fetching parsed data for table '{style_name}': {e}")
        raise
    except Exception as e:
        logger.error(f"[screen-test] - An unexpected error occurred in fetch_table for '{style_name}': {e}")
        raise


def fetch_direct_access_table(db: DatabaseManager, style_name: str, environment: str,
                              extra_normalizer_context: Dict[str, Any] | None = None) -> Dict[str, Any] | None:
    """
    Fetches all rows for a given table, parses them into objects,
    and returns them in a dictionary keyed by a str describing the content i.e. ted-lasso-s1-e1.
    Object value is built using specific object constructor mapping parameters
    """
    try:
        raw_results = fetch_raw_table_data(db, style_name, environment)
        if not raw_results:
            return None

        table_config = DB_TABLE_CONFIG[style_name]
        key_column = table_config["key_column"]

        new_collection = {}
        for row in raw_results:
            new_collection[row.get(key_column)] = parse_single_db_row_to_object(
                row,
                table_config["object_class"],
                table_config["object_constructor_mapping"],
                style_name,
                extra_normalizer_context
            )
        return new_collection
    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Database error while fetching parsed data for table '{style_name}': {e}")
        raise
    except Exception as e:
        logger.error(f"[screen-test] - An unexpected error occurred in fetch_table for '{style_name}': {e}")
        raise


def fetch_mixed_direct_access_table(db: DatabaseManager, style_name: str, environment: str,
                                    extra_normalizer_context: Dict[str, Any] | None = None) -> Dict[Enum, Any] | None:
    """
    Fetches all rows for a given table, parses them into objects,
    and returns them in a dictionary keyed by a str describing the content i.e. ted-lasso-s1-e1.
    Object value may be structured as BoxSet, but Default is for Object as UMCContent.
    """
    try:
        raw_results = fetch_raw_table_data(db, style_name, environment)
        if not raw_results:
            return None

        table_config = DB_TABLE_CONFIG[style_name]
        key_column = table_config["key_column"]  # Key value for completed dictionary
        object_style_mappings = table_config.get("class_mappings")  # style of object BoxSet or UMCContent

        new_collection = {}
        for row in raw_results:
            # content_type col value determines if the Object should be a BoxSet or Default
            content_type_value = row.get("content_type")
            if content_type_value == "BOX_SET":
                selected_class_info = object_style_mappings.get("BOX_SET")
            else:
                selected_class_info = object_style_mappings.get("DEFAULT")
            # Build the object based on the content_type
            actual_object_class = selected_class_info.get("object_class")
            actual_constructor_mapping = selected_class_info.get("constructor_mapping")
            new_collection[row.get(key_column)] = parse_single_db_row_to_object(
                row,
                actual_object_class,  # Pass the specific class (UMCContent or BoxSet)
                actual_constructor_mapping,  # Pass its corresponding constructor mapping
                style_name,
                extra_normalizer_context
            )
        return new_collection
    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Database error while fetching parsed data for table '{style_name}': {e}")
        raise
    except Exception as e:
        logger.error(f"[screen-test] - An unexpected error occurred in fetch_table for '{style_name}': {e}")
        raise


def fetch_content_data_table(db: DatabaseManager, style_name: str, environment: str,
                             extra_normalizer_context: Dict[str, Any] | None = None) -> Dict[str, Any] | None:
    """
    Fetches all rows for a given table, parses them into objects,
    and returns them in a dictionary keyed by a str describing the content i.e. ted-lasso-s1-e1.
    Object value is built using specific object constructor mapping parameters
    """
    try:
        raw_results = fetch_raw_table_data(db, style_name, environment)
        if not raw_results:
            return None

        table_config = DB_TABLE_CONFIG[style_name]
        key_column = table_config["key_column"]

        new_collection = {}
        for row in raw_results:
            new_collection[row.get(key_column)] = parse_single_db_row_to_object(
                row,
                table_config["object_class"],
                table_config["object_constructor_mapping"],
                style_name,
                extra_normalizer_context
            )
        return new_collection
    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Database error while fetching parsed data for table '{style_name}': {e}")
        raise
    except Exception as e:
        logger.error(f"[screen-test] - An unexpected error occurred in fetch_table for '{style_name}': {e}")
        raise


def fetch_table_by_uuid(db: DatabaseManager, style_name: str, environment: str,
                        extra_normalizer_context: Dict[str, Any] | None = None) -> dict or None:
    """
        Fetches all rows for a given table, parses them into objects
        and returns them in a dictionary keyed by the row's uuid.
        Used in relational parsing
        """
    if not db.connection:
        logger.error("[screen-test] - Database not connected. Call connect_to_database() first.")
        return None

    if style_name not in DB_TABLE_CONFIG:
        logger.error(f"[screen-test] - Configuration for table '{style_name}' not found in DB_TABLE_CONFIG.")
        return None
    table_config = DB_TABLE_CONFIG[style_name]
    db_table_name = table_config["table_name"]
    db_schema = table_config.get("schema")
    key_column = table_config.get("key_column")
    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cur:
            query = sql.SQL(
                """SELECT * FROM {schema}.{table}
                   WHERE environment = %s;"""
            ).format(
                schema=sql.Identifier(db_schema),
                table=sql.Identifier(db_table_name)
            )
            results = execute_db_fetch(cur, query, (environment,), f"table {db_table_name}")
            new_collection = {}
            for row in results:
                new_collection[row.get(key_column)] = parse_single_db_row_to_object(
                    row,
                    table_config["object_class"],
                    table_config["object_constructor_mapping"],
                    style_name,
                    extra_normalizer_context
                )
            return new_collection
    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Error while fetching raw data for table {db_table_name}: {e}")
        raise


def fetch_table_by_id(db: DatabaseManager, style_name: str, environment: str,
                      extra_normalizer_context: Dict[str, Any] | None = None) -> dict or None:
    """
        Fetches all rows for a given table, parses them into objects
        and returns them in a dictionary keyed by the row's uuid.
        Used in relational parsing
        """
    if not db.connection:
        logger.error("[screen-test] - Database not connected. Call connect_to_database() first.")
        return None

    if style_name not in DB_TABLE_CONFIG:
        logger.error(f"[screen-test] - Configuration for table '{style_name}' not found in DB_TABLE_CONFIG.")
        return None
    table_config = DB_TABLE_CONFIG[style_name]
    db_table_name = table_config["table_name"]
    db_schema = table_config.get("schema")
    key_column = table_config.get("key_column")
    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cur:
            query = sql.SQL(
                """SELECT * FROM {schema}.{table}
                   WHERE environment = %s;"""
            ).format(
                schema=sql.Identifier(db_schema),
                table=sql.Identifier(db_table_name)
            )
            results = execute_db_fetch(cur, query, (environment,), f"table {db_table_name}")
            new_collection = {}
            for row in results:
                new_collection[row.get(key_column)] = parse_single_db_row_to_object(
                    row,
                    table_config["object_class"],
                    table_config["object_constructor_mapping"],
                    style_name,
                    extra_normalizer_context
                )
            return new_collection
    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Error while fetching raw data for table {db_table_name}: {e}")
        raise


def fetch_collections_with_displays(db: DatabaseManager, environment: str) -> Dict[CollectionNames, Collection] | None:
    """
    Fetches all Collection objects and nests their associated Display objects.
    Returns collections in CollectionNames Enum keyed dictionary.
    """
    logger.info(f"[screen-test] - Starting fetch for Collections in environment: {environment}")

    # Fetch Display Tables by uuid to connect to context_id column in collections
    displays_by_uuid = fetch_table_by_uuid(db, "display_by_uuid", environment)
    if not displays_by_uuid:
        logger.warning(f"[screen-test] - No display data found for environment: {environment}.")
        displays_by_uuid = {}

    # Info needed from display table
    normalizer_context = {
        "displays_by_id": displays_by_uuid,
        "display_types_enum": DisplayTypes
    }

    # fetch collections keyed with enum name
    collections_by_enum_name = fetch_table(
        db,
        "collection",
        environment,
        extra_normalizer_context=normalizer_context  # will connect display table values to collections
    )

    if not collections_by_enum_name:
        logger.warning(
            f"[screen-test] - No collection data found for environment: {environment}. Returning empty dictionary.")
        return {}

    logger.info(
        f"[screen-test] - Finished fetching and nesting displays into {len(collections_by_enum_name)} Collections.")
    return collections_by_enum_name


def fetch_collections_by_id_with_displays(db: DatabaseManager, environment: str) -> Dict[str, Collection] | None:
    """
    Fetches all Collection objects and nests their associated Display objects.
    Returns collections in a UUID-keyed dictionary, without the Collection object
    itself needing a UUID attribute.
    """
    logger.info(f"[screen-test] - Starting fetch for Collections (UUID-keyed) in environment: {environment}")

    # Fetch Display Tables by uuid to connect to context_id column in collections
    displays_by_uuid = fetch_table_by_uuid(db, "display_by_uuid", environment)
    if not displays_by_uuid:
        logger.warning(f"[screen-test] - No display data found for environment: {environment}.")
        displays_by_uuid = {}

    # Info needed from display table
    normalizer_context = {
        "displays_by_id": displays_by_uuid,
        "display_types_enum": DisplayTypes
    }

    # Create collections dictionary keyed by ids from table + containing properly parsed display table relations
    collections_by_uuid = fetch_table_by_uuid(
        db,
        "collection_by_id",
        environment,
        extra_normalizer_context=normalizer_context  # will connect display table values to collections
    )

    if not collections_by_uuid:
        logger.warning(
            f"[screen-test] - No collection data found for environment: {environment}. Returning empty dictionary.")
        return {}

    logger.info(f"[screen-test] - Finished fetching and nesting displays into {len(collections_by_uuid)} Collections.")
    return collections_by_uuid


def fetch_canvases_with_collections_and_displays(db: DatabaseManager, environment: str) -> dict[
    Enum, Any]:
    """
    Fetches all Canvas objects and nests their associated Collection objects,
    which in turn will have their Display objects already nested.
    Returns canvases in an Enum-keyed dictionary.
    """
    logger.info(f"[screen-test] - Starting fetch for Canvas in environment: {environment}")

    # Fetch all collections keyed by collection_id and with displays nested
    collections_with_ids_and_displays: Dict[str, Collection] = fetch_collections_by_id_with_displays(db,
                                                                                                     environment)
    if collections_with_ids_and_displays is None:
        logger.warning(f"No collections found for environment: {environment}. Canvas collections will be empty.")
        collections_with_ids_and_displays = {}

    direct_access_table = fetch_direct_access(db, environment)
    # Info from collections table to use within the Canvas Objects already nested with Displays
    normalizer_context = {
        "collections_by_id": collections_with_ids_and_displays,
        "collection_types_enum": CollectionNames,
        "direct_access_media": direct_access_table
    }

    # Fetch canvases and parse in collection objects to collection_items attribute as needed
    canvases_by_enum_name = fetch_table(
        db,
        "canvas",
        environment,
        extra_normalizer_context=normalizer_context
    )

    if not canvases_by_enum_name:
        logger.warning(
            f"[screen-test] - No canvas data found for environment: {environment}. Returning empty dictionary.")
        return {}

    logger.info(
        f"[screen-test] - Finished fetching and nesting collections into {len(canvases_by_enum_name)} Canvases.")
    return canvases_by_enum_name


def fetch_content_data(db: DatabaseManager, environment: str) -> dict:
    """
       Fetches all relevant info from the Content Data tables (Leagues, Sports, Persons) in screentest and builds the
       Content_Data dictionary for the data model
       :param db: (DatabaseManager) an instance forming the connection to the screentest database
       :param environment: the data environment ("prod" or "itms11")
       :return: dict of Content Data Objects and their associated "Content Data" Enum Type

       Types of Content Data:
       class ContentDatas(Enum):
            LEAGUES = auto()
            SPORTS = auto()
            AB_TESTING = auto() --- Currently unused/ no specific table in DB - skipping during fetch
            PERSONS = auto()
            CAMPAIGNS = auto()
    """
    extra_context_for_normalizers = {}
    content_data = {}
    try:
        #In Leagues - Competitors are needed for stitching
        logger.info("[screen-test] - Fetching Competitors data...")
        competitors_by_enum_key = fetch_content_data_table(db, "competitors", environment)

        extra_context_for_normalizers["competitors_by_enum"] = competitors_by_enum_key

        for content_type_enum in ContentDatas:
            # Skip AB_TESTING as per original logic
            if content_type_enum == ContentDatas.AB_TESTING:
                continue

            style_name = content_type_enum.name.lower()

            # Pass the context ONLY when fetching LEAGUES
            current_extra_context = None
            if content_type_enum == ContentDatas.LEAGUES:
                current_extra_context = extra_context_for_normalizers

            logger.info(f"[screen-test] - Fetching {style_name.capitalize()} data...")
            content_data[content_type_enum] = fetch_content_data_table(
                db,
                style_name,
                environment,
                current_extra_context  # Pass the context down
            )

    except Exception as e:
        logger.error(f"[screen-test] - Error in fetch_content_data: {e}")
        raise

    return content_data


def fetch_direct_access(db: DatabaseManager, environment: str) -> dict:
    """
       Fetches all relevant info from the Direct Access table in screentest and builds the Direct_Access dictionary
       for the data model
       :param db: (DatabaseManager) an instance forming the connection to the screentest database
       :param environment: the data environment ("prod" or "itms11")
       :return: dict of UMC Objects (Sports, Episodes, Movies) and their associated "UMC Content" Enum Type

       Types of Direct Access:
       direct_access_locations = [
            direct_access_episodes,
            direct_access_mlb,
            direct_access_mls,
            direct_access_movies,
            direct_access_others,
            direct_access_seasons,
            direct_access_sports,
            direct_access_tv_shows
        ]


    """
    direct_access_locations = [
        "episode", "sporting_event", "movie", "season", "tv_show", "sports_teams", "live_events"
    ]
    tables = {}
    for location in direct_access_locations:
        tables.update(fetch_direct_access_table(db, location, environment))
        if location == "sports_teams":
            print(fetch_direct_access_table(db, "sports_teams", "itms11"))

    tables.update(fetch_mixed_direct_access_table(db, "other", environment))
    return tables


# HELPERS
def execute_db_fetch(db: DatabaseManager, query: sql.Composed, params: tuple, log_entity_name: str,
                     generated_uuid: str = None) -> dict or None:
    """Helper to execute a database fetch with common error handling and logging."""
    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()

            if results:
                logger.info(
                    f"[screen-test] - Successfully fetched {log_entity_name} with ID: {generated_uuid or 'N/A'}.")
                return results
            else:
                logger.info("[screen-test] - No records found.")
                return None
    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Error while fetching {log_entity_name}: {e}")
        raise


def parse_single_db_row_to_object(
        raw_row: Dict,
        object_class: Type[Any],
        object_constructor_mapping: Dict[str, Dict[str, Any]],
        table_style_name: str,
        extra_normalizer_context: Dict[str, Any] = None
) -> Any:
    """
    Parses a single raw database row (dictionary) into a Python object based on params outlined in
    the config include object structure, types and anything normalizers to connect tables.

    Returns:
        An object in the type indicated in the params, or None if parsing/construction fails.
    """
    instance_kwargs = {}  # gathers all attributes into dictionary structure for object build
    extra_normalizer_context = extra_normalizer_context or {}

    for obj_attr, mapping_info in object_constructor_mapping.items():
        db_column = mapping_info.get("db_column")
        normalizer_id = mapping_info.get("normalizer")
        raw_value = raw_row.get(db_column)

        normalized_value = raw_value  # Default to raw value of data from database

        # normalize context_ids (DisplayType: display_uuid)
        if normalizer_id == 'context_ids_normalizer_factory':
            normalizer_func = create_context_ids_normalizer(
                extra_normalizer_context.get("displays_by_id"),
                extra_normalizer_context.get("display_types_enum")
            )
            normalized_value = normalizer_func(raw_value)

        # normalize collection_items (CollectionNames: collection_id)
        elif normalizer_id == 'collection_items_normalizer_factory':
            normalizer_func = create_collection_items_normalizer(
                extra_normalizer_context.get("collections_by_id"),
                extra_normalizer_context.get("collection_types_enum")
            )
            normalized_value = normalizer_func(raw_value)
        elif normalizer_id == 'competitor_normalizer_factory':
            normalizer_func = create_competitors_normalizer(
                extra_normalizer_context.get("competitors_by_enum"),
                DB_TABLE_CONFIG["competitors"]["key_class"]
            )
            normalized_value = normalizer_func(raw_value)
        elif normalizer_id == 'media_content_normalizer_factory':
            normalizer_func = create_media_content_normalizer(
                extra_normalizer_context.get("direct_access_media"),
            )
            normalized_value = normalizer_func(raw_value)

        #use normalized function (standardized ones like json to list of strings)
        elif callable(normalizer_id):
            try:
                normalized_value = normalizer_id(raw_value)
            except Exception as e:
                logger.warning(
                    f"[{table_style_name}] Normalization failed for '{obj_attr}' with normalizer "
                    f"'{normalizer_id.__name__}': {e}. Value: {raw_value}")
                normalized_value = None

        instance_kwargs[obj_attr] = normalized_value

    return object_class(**instance_kwargs)


def create_context_ids_normalizer(displays_by_id: Dict[str, Any], display_types_enum: Type[Enum]):
    """
    Special relational normalizer for the 'context_ids' field.
    creates a dictionary of {DisplayTypes: Context objects}.
    """

    def normalize_context_ids_field(raw_context_ids_value: str | Dict) -> Dict:
        context_id_map = {}
        # iterate through {DisplayType: uuid}
        if raw_context_ids_value:
            for enum_str_key, display_uuid in raw_context_ids_value.items():
                display_obj = displays_by_id.get(str(display_uuid))
                if display_obj:
                    try:
                        enum_key_member = display_types_enum[enum_str_key]
                        context_id_map[enum_key_member] = display_obj
                    except ValueError:
                        logger.error(
                            f"[screen-test] - '{enum_str_key}' is not a valid member for {display_types_enum.__name__}.")
                else:
                    logger.warning(
                        f"[screen-test] - Child object with UUID '{display_uuid}' not found in displays_by_id.")
        return context_id_map

    return normalize_context_ids_field


def create_collection_items_normalizer(collection_by_id: Dict[str, Collection],
                                       collection_types_enum: Type[Enum]):
    """
    Function to create a normalizer for the 'collection_items' field of Canvas.
    Creates a dictionary of {CollectionNames: Collection objects}.
    """

    def normalize_collection_items_field(raw_collection_items_values: str | Dict) -> Dict:
        collections_map = {}
        # Iterate through {collection type: collection_id}
        if raw_collection_items_values:
            for enum_str_key, collection_id in raw_collection_items_values.items():
                collection_obj = collection_by_id.get(str(collection_id))

                if collection_obj:
                    try:
                        enum_key_member = collection_types_enum[enum_str_key]
                        collections_map[enum_key_member] = collection_obj
                    except ValueError:
                        logger.error(
                            f"[screen-test] - '{enum_str_key}' is not a valid member for {collection_types_enum.__name__}.")
                else:
                    logger.warning(
                        f"[screen-test] - Child object with ID '{collection_id}' not found in displays_by_id.")
        return collections_map

    return normalize_collection_items_field

def create_media_content_normalizer(direct_access: Dict[str, UMCContent]):
    """
    Function to create a normalizer for the 'collection_items' field of Canvas.
    Creates a dictionary of {CollectionNames: Collection objects}.
    """

    def normalize_media_content_field(raw_media_content_values: str | Dict) -> Dict:  # Fixed type hint
        media_content_map = {}
        # Iterate through {media_content:direct_access object}
        if raw_media_content_values:
            for key, direct_access_id in raw_media_content_values.items():
                media_content_obj = direct_access.get(str(direct_access_id))
                if media_content_obj:
                    media_content_map[key] = media_content_obj
                else:
                    logger.warning(
                        f"[screen-test] - Child object with id '{direct_access_id}' not found in direct_access.")
        return media_content_map

    return normalize_media_content_field


# Normalizer for competitors

def create_competitors_normalizer(competitors_by_enum: Dict[Enum, UMCContent], competitor_types_enum: Type[Enum]):
    """
    Factory function to create a normalizer for the 'competitors' field of League.
    The returned normalizer uses external data (competitors_by_enum).
    """

    team_name_to_enum_map: Dict[str, CompetitorNames] = {}
    for enum_member, umc_content_obj in competitors_by_enum.items():
        # Ensure that the UMCContent object's name is consistent with the database list
        team_name_to_enum_map[umc_content_obj.name] = enum_member

    def normalize_competitors_field(raw_competitor_list_value: Any) -> Dict[Enum, UMCContent]:
        if raw_competitor_list_value is None:
            return {}
        else:
            competitor_names_from_db = raw_competitor_list_value

        nested_competitors_map: Dict[Enum, UMCContent] = {}
        for competitor_name_str in competitor_names_from_db:
            enum_member = team_name_to_enum_map.get(competitor_name_str)

            if enum_member:
                umc_content_obj = competitors_by_enum.get(enum_member)

                if umc_content_obj:
                    nested_competitors_map[enum_member] = umc_content_obj
                else:
                    logger.warning(
                        f"UMCContent object for '{competitor_name_str}' (enum: {enum_member.name}) not found in pre-fetched competitors_by_enum.")
            else:
                logger.warning(
                    f"Competitor name '{competitor_name_str}' not found in the mapping to CompetitorNames enum. Skipping.")

        return nested_competitors_map

    return normalize_competitors_field
