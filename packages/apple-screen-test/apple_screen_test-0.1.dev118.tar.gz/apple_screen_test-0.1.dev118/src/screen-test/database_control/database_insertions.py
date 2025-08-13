import logging
import uuid
from copy import deepcopy

import psycopg2
from content_types import UMCContentType
from data_structures.test_data_classes import Canvas, Context, League, Shelf, Collection, Campaign, Person, Sport, \
    Account, Episode, LeagueAvailability, SportingEvent, UMCContent, BoxSet
from data_structures.test_data_keys import LeagueNames, SportNames, ShelfTypes, CampaignNames, PersonNames, \
    CollectionNames, CanvasNames, \
    DisplayTypes, AccountTypes, UTSOfferTypes, Offers
from psycopg2 import sql
from psycopg2.extras import Json, RealDictCursor
from test_data_classes import UTSOffer, Offer

from database_manager import DatabaseManager

# GLOBAL VARIABLES
logger = logging.getLogger(__name__)


# HELPER FUNCTIONS
def execute_db_and_log(db: DatabaseManager, query: sql.Composed, params: tuple, log_entity_name: str,
                       primary_id: str = None) -> None:
    """Helper to execute a database query with logging upon success.
    This does not handle commits or rollbacks
    REQUIREMENT: active cursor are argument
    Parameter:
    db (DatabaseManager): Provides database instance for connection to the screentest Database.
    query (sql.Composed):
    params (tuple):
    log_entity_name (str):
    """
    with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(query, params)
        logger.info(f"[screen-test] - Successfully inserted {log_entity_name} with ID: {primary_id or 'N/A'}.")


def find_display(db: DatabaseManager, display_type_name: str, root: str, canvas: str, shelf: str,
                 environment: str) -> str | None:
    """
    Parameter:
    db (DatabaseManager): Provides database instance for connection to the screentest Database.
    display_type_name (str) -
    root (str) -
    canvas (str) -
    shelf (str) -
    environment (str) -
    Attempts to find an existing Display record based on its unique attributes.
    Returns the display_uuid if found, otherwise None.
    """
    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = sql.SQL(
                """SELECT display_uuid FROM {schema}.{table}
                   WHERE display_type = %s AND root = %s AND canvas = %s AND shelf = %s AND environment = %s;"""
            ).format(schema=sql.Identifier("screentest"), table=sql.Identifier("display"))
            cursor.execute(query, (display_type_name, root, canvas, shelf, environment,))
            result = cursor.fetchone()
            if result:
                logger.info(f"[screen-test] - Found existing Display with UUID: {result['display_uuid']}")
                return result['display_uuid']
            return None
    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Error while finding Display: {e}")
        raise


def find_collection(db: DatabaseManager, collection_type_name: str,
                    environment: str) -> str | None:
    """
    Parameter:
    db (DatabaseManager): Provides database instance for connection to the screentest Database.
    collection_id (str):
    collection_type_name (str):
    environment (str):
    Attempts to find an existing Collection record based on its unique attributes.
    Returns the collection_id if found, otherwise None.
    """
    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = sql.SQL(
                """SELECT collection_id FROM {schema}.{table}
                   WHERE collection_name = %s AND environment = %s;"""
            ).format(schema=sql.Identifier("screentest"), table=sql.Identifier("collection"))

            cursor.execute(query, ( collection_type_name, environment,))
            result = cursor.fetchone()
            if result:
                logger.info(f"[screen-test] - Found existing Collection with ID: {result['collection_id']}")
                return result['collection_id']
            return None
    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Error while finding Collection: {e}")
        raise


def find_canvas(db: DatabaseManager, canvas_id: str, canvas_type_name: str, environment: str) -> str | None:
    """
    db (DatabaseManager): Provides database instance for connection to the screentest Database.
    Attempts to find an existing Canvas record based on its unique attributes.
    Returns the canvas_uuid if found, otherwise None.
    """
    query = sql.SQL(
        """SELECT canvas_uuid FROM {schema}.{table}
           WHERE id = %s AND canvas_type = %s AND environment = %s;"""
    ).format(schema=sql.Identifier("screentest"), table=sql.Identifier("canvas"))
    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (canvas_id, canvas_type_name, environment,))
            result = cursor.fetchone()
            if result:
                logger.info(f"[screen-test] - Found existing Canvas with UUID: {result['canvas_uuid']}")
                return result['canvas_uuid']
            return None
    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Error while finding Canvas: {e}")
        raise


# INSERTION FUNCTIONS

def insert_full_canvas_structure(db: DatabaseManager,
                                 canvas_type_enum: CanvasNames,
                                 original_canvas_obj: Canvas,
                                 environment: str) -> str:
    """
        Inserts a complete Canvas structure, including its nested Collections and Displays,
        into the database, managing the UUID relationships.
        This function searches for existing Displays/Collections to prevent duplicate records before creating any
        missing records.

        This function processes the dependencies in the correct order:
        1. For each nested Display (Context object):
           - Attempts to find an existing Display record. If found, reuses its UUID.
           - If not found, inserts a new Display record.
        2. For each nested Collection:
           - Attempts to find an existing Collection record. If found, reuses its UUID.
           - If not found, inserts a new Collection record. Its `context_ids` are updated
             with the generated/found Display UUIDs.
        3. For the top-level Canvas record:
           - Attempts to find an existing Canvas record. If found, reuses its UUID.
           - If not found, inserts a new Canvas record. Its `collection_items` are updated
             with the generated/found Collection UUIDs.

        Args:
            db (DatabaseManager): Provides database instance for connection to the screentest Database.
            canvas_type_enum (Canvases): The enum key for the top-level Canvas (e.g., Canvases.MLS).
            original_canvas_obj (Canvas): The fully nested Canvas data class object,
                                          including nested Collection and Context objects.
            environment (str): The environment tag for all records (e.g., "prod", "itms11").

        Returns:
            str: The UUID of the newly inserted or found top-level Canvas record on success.

        Side Effects:
            - Inserts or finds multiple rows in 'Display', 'Collection', and 'Canvas' tables.
            - Modifies a *copy* of the input `Canvas` object to replace nested objects with UUIDs
              before final insertion.
            - Logs errors on failure.
    """
    logger.info(f"[screen-test] - Starting full insertion for Canvas: {canvas_type_enum.name}")

    # Create copy to modify
    canvas_obj_to_insert = deepcopy(original_canvas_obj)

    # --- Process nested Collections within Canvas.collection_items ---
    # Collections stored as {CollectionType.name : UUID}
    processed_collection_items = {}
    if canvas_obj_to_insert.collection_items:
        for collection_key_enum, nested_collection_obj in canvas_obj_to_insert.collection_items.items():
            logger.info(f"[screen-test] - Processing nested Collection: {collection_key_enum.name}")

            # --- Process nested Displays (Contexts) within this Collection's context_ids ---
            # Displays stored as {DisplayType.name : UUID}
            processed_context_ids = {}
            if nested_collection_obj.context_ids:
                for display_type_enum, nested_display_obj in nested_collection_obj.context_ids.items():
                    logger.info(f"[screen-test] - Processing nested Display: {display_type_enum.name}")

                    # Attempt to find existing Display
                    found_display_uuid = find_display(
                        db=db,
                        display_type_name=display_type_enum.name,
                        root=nested_display_obj.root,
                        canvas=nested_display_obj.canvas,
                        shelf=nested_display_obj.shelf,
                        environment=environment
                    )

                    if found_display_uuid:
                        display_uuid = found_display_uuid
                    else:
                        # Insert the Display (Context) record
                        display_uuid = insert_display(
                            db=db,
                            display_type=display_type_enum,
                            display_obj=nested_display_obj,
                            environment=environment
                        )
                    # Store the generated/found UUID to replace the object in the Collection's context_ids dict
                    processed_context_ids[display_type_enum.name] = display_uuid  # Store as string name for DB

            # Update the Collection object's context_ids with the UUIDs
            nested_collection_obj.context_ids = processed_context_ids

            # --- Insert or Find the Collection record ---
            # Attempt to find existing Collection
            found_collection_id = find_collection(
                db=db,
                collection_type_name=collection_key_enum.name,
                environment=environment
            )

            if found_collection_id:
                collection_id = found_collection_id
            else:
                collection_id = insert_collection(
                    db=db,
                    collection_obj=nested_collection_obj,
                    collection_type=collection_key_enum,
                    environment=environment
                )
            # Store the generated/found ID to replace the object in the Canvas's collection_items
            processed_collection_items[collection_key_enum.name] = collection_id  # Store as string name for DB

    # Update the Canvas object's collection_items with the IDs
    canvas_obj_to_insert.collection_items = processed_collection_items

    # --- Insert or Find the top-level Canvas record ---
    logger.info(f"[screen-test] - Processing top-level Canvas: {canvas_type_enum.name}")

    # Attempt to find existing Canvas
    found_canvas_uuid = find_canvas(
        db=db,
        canvas_id=canvas_obj_to_insert.id,
        canvas_type_name=canvas_type_enum.name,
        environment=environment
    )

    if found_canvas_uuid:
        final_canvas_uuid = found_canvas_uuid
    else:
        # Insert the Canvas record
        final_canvas_uuid = insert_canvas(
            db=db,
            canvas_obj=canvas_obj_to_insert,
            canvas_type=canvas_type_enum,
            environment=environment
        )
    return final_canvas_uuid


def insert_account(db: DatabaseManager, account_type: AccountTypes, account_obj: Account,
                   environment: str) -> str:
    """
        Inserts a new account record into the 'Account' table.

        Args:
            db (DatabaseManager): Provides database instance for connection to the screentest Database.
            account_type (AccountTypes): An enum representing the type of account (e.g., AccountTypes.COLD_START).
                            Its `.name` attribute is used for `account_type`.
            account_obj (Account): A Account data class object containing details like account_id,
                           email, password and protection status.
            environment (str): The environment tag for the record (e.g., "prod", "itms11").

        Returns:
            str: The UUID of the newly inserted account record on success.

        Side Effects:
            Inserts a row into the 'Account' table.
            Logs an error on failure.
        """
    account_uuid = str(uuid.uuid4())
    query = sql.SQL(

        """INSERT INTO {schema}.{table}(account_uuid, account_type, dsid, cid, email, encrypted_password,
                                        protected, environment)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""").format(schema=sql.Identifier("screentest"),
                                                               table=sql.Identifier("account"))
    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            execute_db_and_log(
                cursor,
                query,
                (account_uuid, account_type.name, account_obj.dsid, account_obj.cid, account_obj.email,
                 account_obj.encrypted_password, account_obj.protected, environment,),
                f"account {account_type.name}",
                account_uuid
            )
            db.connection.commit()  # Explicit commit after successful execution
            logger.info(f"[screen-test] - Insertion successful for account: {account_type.name}.")
    except psycopg2.Error as e:
        db.connection.rollback()  # Explicit rollback on error
        logger.error(f"[screen-test] - Error during account insertion for {account_type.name}: {e}")
    return account_uuid


def insert_league(db: DatabaseManager, league_type: LeagueNames, league_obj: League, environment: str) -> str:
    """
    Inserts a new league record into the 'League' table.

    Args:
        db (DatabaseManager): Provides database instance for connection to the screentest Database.
        league_type (Leagues): An enum representing the type of league (e.g., Leagues.NFL).
                        Its `.name` attribute is used for `league_initials`.
        league_obj (League): A League data class object containing details like name, id,
                       competitors (a dictionary of UMC content objects), and related_content.
        environment (str): The environment tag for the record (e.g., "prod", "itms11").

    Returns:
        str: The UUID of the newly inserted league record on success.

    Side Effects:
        Inserts a row into the 'League' table.
        Logs an error on failure.
        Converts `competitors` (list of UMC content names of Competitors) and `related_content` (dictionary) to JSON
        before insertion.
    """
    logger.info(f"[screen-test] - Starting insertion for '{league_type.name}' league record.")
    league_uuid = str(uuid.uuid4())
    league_initials = league_type.name
    list_of_competitor_names = [umc_content_obj.name for umc_content_obj in league_obj.competitors.values()]
    query = sql.SQL(

        """INSERT INTO {schema}.{table}( league_initials, league_full_name, umc_id, competitors, related_content,
        environment, league_uuid)

           VALUES (%s, %s, %s, %s, %s, %s, %s);""").format(schema=sql.Identifier("screentest"),
                                                           table=sql.Identifier("league"))
    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            execute_db_and_log(cursor, query, (league_initials, league_obj.name,
                                               league_obj.id, psycopg2.extras.Json(list_of_competitor_names),
                                               psycopg2.extras.Json(league_obj.related_content),
                                               environment, league_uuid,),
                               f"league {league_type.name}", league_uuid)
            logger.info(f"[screen-test] - Transaction completed for league: {league_type.name}.")
            db.connection.commit()

    except psycopg2.Error as e:
        db.connection.rollback()
        logger.error(f"[screen-test] - Error during league insertion for {league_type.name}: {e}")
        raise
    return league_uuid


def insert_shelf(db: DatabaseManager, shelf_type: ShelfTypes, shelf_obj: Shelf, environment: str) -> str:
    """
        Inserts a new shelf record into the 'Shelf' table.

        Args:
            db (DatabaseManager): Provides database instance for connection to the screentest Database.
            shelf_type (Shelves): An enum representing the type of shelf (e.g., Shelves.LOCKUP, Shelves.UP_NEXT).
                                  Its `.name` attribute is used for the `shelf_type` column.
            shelf_obj (Shelf): A data class object containing the details for the shelf (shelf_id, display_type).
            environment (str): The environment tag for the record (e.g., "prod", "itms11").

        Returns:
            str: The UUID of the newly inserted shelf record on success.

        Side Effects:
            - Inserts a row into the 'Shelf' table.
            - Logs an error on failure.
        """
    logger.info(f"[screen-test] Starting insertion for '{shelf_type.name}' shelf record.")
    shelf_uuid = str(uuid.uuid4())
    shelf_type_name = shelf_type.name

    query = sql.SQL(
        """INSERT INTO {schema}.{table}( shelf_uuid, shelf_id, display_type, shelf_type, environment)
           VALUES (%s, %s, %s, %s, %s);"""
    ).format(schema=sql.Identifier("screentest"), table=sql.Identifier("shelf"))

    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            execute_db_and_log(cursor, query,
                               (shelf_uuid, shelf_obj.shelf_id, shelf_obj.display_type, shelf_type_name,
                                environment,),
                               f"shelf {shelf_type.name}", shelf_uuid)
            logger.info(f"[screen-test] - Transaction completed for shelf: {shelf_type.name}.")
            db.connection.commit()
    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Error during shelf insertion for {shelf_type.name}: {e}")
        db.connection.rollback()
        raise
    return shelf_uuid


def insert_display(db: DatabaseManager, display_type: DisplayTypes, display_obj: Context,
                   environment: str) -> str:
    """
       Inserts a new display record into the 'Display' table.

       Args:
           db (DatabaseManager): Provides database instance for connection to the screentest Database.
           display_type (DisplayTypes): An enum representing the specific type of display (e.g.,
           DisplayTypes.EPIC_STAGE, DisplayTypes.TEAM_LOCKUP).
                                        Its `.name` attribute is used for the `display_type` column.
           display_obj (Context): A data class object containing the configuration details for the display (root,
           canvas, shelf).
           environment (str): The environment tag for the record (e.g., "prod", "itms11").

       Returns:
           str: The UUID of the newly inserted display record on success.

       Side Effects:
           - Inserts a row into the 'Display' table.
           - Logs an error on failure.
       """
    logger.info(f"[screen-test] - Attempting to insert Display record for {display_type.name}")
    display_uuid = str(uuid.uuid4())
    display_type_name = display_type.name

    query = sql.SQL(
        """INSERT INTO {schema}.{table}(display_uuid, root, canvas, shelf, display_type, environment)
           VALUES (%s, %s, %s, %s, %s, %s);"""
    ).format(
        schema=sql.Identifier("screentest"),
        table=sql.Identifier("display")
    )
    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            execute_db_and_log(
                cursor,
                query,
                (display_uuid, display_obj.root, display_obj.canvas, display_obj.shelf, display_type_name,
                 environment,),
                f"Display record for {display_type.name}",
                display_uuid
            )
            logger.info(f"[screen-test] - Transaction successful for display: {display_type.name}.")
            db.connection.commit()

    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Error during display insertion for {display_type.name}: {e}")
        db.connection.rollback()
        raise
    return display_uuid


def insert_collection(db: DatabaseManager, collection_type: CollectionNames, collection_obj: Collection,
                      environment: str) -> str:
    """
           Inserts a new collection record into the 'Collection' table.

           Args:
               db (DatabaseManager): Provides database instance for connection to the screentest Database.
               collection_type (Collections): An enum representing the type of collection (e.g.,
               Collections.MLS_TEAMS_ROW).
                                              Its `.name` attribute is used for the `collection_type` column.
               collection_obj (Collection): A data class object containing the details for the collection
               (ID, context_ids, items).
               environment (str): The environment tag for the record (e.g., "prod", "itms11").

           Returns:
               str: The UUID of the newly inserted collection record on success.

           Side Effects:
               - Inserts a row into the 'Collection' table.
               - Converts `context_ids` (a dictionary mapping display types to display UUIDs) to JSON before insertion.
               - Converts `items` (a list of content identifiers) to JSON before insertion.
               - Logs an error on failure.
           """
    logger.info(f"[screen-test] - Attempting to insert Collection record for {collection_type.name}")
    collection_uuid = str(uuid.uuid4())
    collection_id = collection_obj.collection_id
    collection_type_name = collection_type.name

    json_items = Json(collection_obj.items)
    processed_context_ids = {}
    if collection_obj.context_ids:
        for display_type_enum, nested_display_obj in collection_obj.context_ids.items():
            logger.info(f"[screen-test] - Processing nested Display: {display_type_enum.name}")

            # Attempt to find existing Display
            found_display_uuid = find_display(
                db=db,
                display_type_name=display_type_enum.name,
                root=nested_display_obj.root,
                canvas=nested_display_obj.canvas,
                shelf=nested_display_obj.shelf,
                environment=environment
            )

            if found_display_uuid:
                display_uuid = found_display_uuid
            else:
                # Insert the Display (Context) record
                display_uuid = insert_display(
                    db=db,
                    display_type=display_type_enum,
                    display_obj=nested_display_obj,
                    environment=environment
                )
            # Store the generated/found UUID to replace the object in the Collection's context_ids
            processed_context_ids[display_type_enum.name] = display_uuid  # Store as string name for DB

    # Update the Collection object's context_ids with the UUIDs
    collection_obj.context_ids = processed_context_ids
    query = sql.SQL(
        """INSERT INTO {schema}.{table}(collection_uuid, collection_id, collection_name, context_ids, items,
         environment)
           VALUES (%s, %s, %s, %s, %s, %s);"""
    ).format(
        schema=sql.Identifier("screentest"),
        table=sql.Identifier("collection")
    )
    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            execute_db_and_log(
                cursor,
                query,
                (collection_uuid, collection_id, collection_type_name, Json(collection_obj.context_ids), json_items,
                 environment,),
                f"Collection record for {collection_type.name}",
                collection_id
            )
            logger.info(f"[screen-test] - Transaction successful for collection: {collection_type.name}.")
            db.connection.commit()

    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Error during collection insertion for {collection_type.name}: {e}")
        db.connection.rollback()
        raise
    return collection_id


def insert_canvas(db: DatabaseManager, canvas_type: CanvasNames, canvas_obj: Canvas,
                  environment: str) -> str:
    """
        Inserts a new canvas record into the 'Canvas' table.

        Args:
            db (DatabaseManager): Provides database instance for connection to the screentest Database.
            canvas_type (Canvases): An enum representing the type of canvas (e.g., Canvases.MLS, Canvases.CHAPMAN).
                                     Its `.name` attribute is used for the `canvas_name` column.
            canvas_obj (Canvas): A data class object containing the details for the canvas.
            environment (str): The environment tag for the record (e.g., "prod", "itms11").

        Returns:
            str: The UUID of the newly inserted canvas record on success.

        Side Effects:
            - Inserts a row into the 'Canvas' table.
            - Converts `child_ids`, `media_content`, `collection_items`, and `up_next_fallback` to JSON
             before insertion.
            - Logs an error on failure.
        """

    logger.info(f"[screen-test] - Attempting to insert Canvas record for {canvas_type.name}")
    canvas_uuid = str(uuid.uuid4())
    canvas_name = canvas_type.name
    child_ids = Json(canvas_obj.child_ids) if canvas_obj.child_ids is not None else None
    media_content = Json(canvas_obj.media_content) if canvas_obj.media_content is not None else None
    collection_items = Json(canvas_obj.collection_items) if canvas_obj.collection_items is not None else None
    up_next_fallback = Json(canvas_obj.up_next_fallback) if canvas_obj.up_next_fallback is not None else None
    query = sql.SQL(
        """INSERT INTO {schema}.{table}(
            canvas_name, child_ids, is_first_party, name, bundle_id, vod_service,
            external_service_id, salable_adam_id, parent_id, id, canvas_uuid,
            canvas_type, salable_adam_id_out_market, salable_adam_id_in_market,
            external_id, is_sports_dynamic, brand_equivalence_id,
            is_enabled_for_editorial_featuring, media_content, collection_items,up_next_fallback, environment
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,  %s, %s, %s, %s, %s
        );"""
    ).format(
        schema=sql.Identifier("screentest"),
        table=sql.Identifier("canvas")
    )
    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            execute_db_and_log(
                cursor,
                query,
                (canvas_name, child_ids, canvas_obj.is_first_party, canvas_obj.name,
                 canvas_obj.bundle_id, canvas_obj.vod_service, canvas_obj.external_service_id,
                 canvas_obj.salable_adam_id, canvas_obj.parent_id, canvas_obj.id,
                 canvas_uuid, canvas_obj.canvas_type.name, canvas_obj.salable_adam_id_out_market,
                 canvas_obj.salable_adam_id_in_market, canvas_obj.external_id,
                 canvas_obj.is_sports_dynamic, canvas_obj.brand_equivalence_id,
                 canvas_obj.is_enabled_for_editorial_featuring, media_content, collection_items,
                 up_next_fallback, environment,),
                f"Canvas record for {canvas_type.name}",
                canvas_uuid
            )
            logger.info(f"[screen-test] - Transaction successful for canvas: {canvas_type.name}.")
            db.connection.commit()

    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Error during canvas insertion for {canvas_type.name}: {e}")
        db.connection.rollback()
        raise
    return canvas_uuid


def insert_campaign(db: DatabaseManager, campaign_type: CampaignNames, campaign_obj: Campaign,
                    environment: str) -> str:
    """
     Inserts a new campaign record into the 'Campaign' table.

     Args:
         db (DatabaseManager): Provides database instance for connection to the screentest Database.
         campaign_type (Campaigns): An enum representing the type of campaign (e.g., Campaigns.TEST_CAMPAIGN).
                                    Its `.name` attribute is used for the `campaign_type` column.
         campaign_obj (Campaign): A data class object containing the details for the campaign (ID, user_id).
         environment (str): The environment tag for the record (e.g., "prod", "itms11").

     Returns:
         str: The ID of the newly inserted campaign record. This is an external ID, not a generated UUID.

     Side Effects:
         - Inserts a row into the 'Campaign' table.
         - Logs an error on failure.
     """
    logger.info(f"[screen-test] - Inserting {campaign_type.name} campaign with ID: {campaign_obj.id}")
    campaign_type_name = campaign_type.name

    query = sql.SQL(
        """INSERT INTO {schema}.{table}(campaign_type, id, user_id, environment)
           VALUES (%s, %s, %s, %s);"""
    ).format(schema=sql.Identifier("screentest"), table=sql.Identifier("campaign"))
    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            execute_db_and_log(
                cursor,
                query,
                (campaign_type_name, campaign_obj.id, campaign_obj.user_id, environment,),
                f"campaign record for {campaign_type.name}",
                campaign_obj.id  # Use campaign_obj.id for logging as it's the returned ID
            )
            logger.info(f"[screen-test] - Transaction completed for campaign: {campaign_type.name}.")
            db.connection.commit()

    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Error during campaign insertion for {campaign_type.name}: {e}")
        db.connection.rollback()
        raise
    return campaign_obj.id


def insert_persons(db: DatabaseManager, person_type: PersonNames, person_obj: Person,
                   environment: str) -> str:
    """
        Inserts a new person record into the 'Persons' table.

        Args:
            db (DatabaseManager): Provides database instance for connection to the screentest Database.
            person_type (Persons): An enum representing the type of person (e.g., Persons.BRAD_BIRD).
                                   Its `.name` attribute is used for the `name` column.
            person_obj (Person): A data class object containing the details for the person (ID, name).
            environment (str): The environment tag for the record (e.g., "prod", "itms11").

        Returns:
            str: The ID of the newly inserted person record. This is an external ID, not a generated UUID.

        Side Effects:
            - Inserts a row into the 'Persons' table.
            - Logs an error on failure.
        """
    logger.info(f"[screen-test] - Processing person: {person_type.name} with ID: {person_obj.id}")
    person_name = person_type.name

    query = sql.SQL(
        """INSERT INTO {schema}.{table}(name, umc_id, full_name, environment)
           VALUES (%s, %s, %s, %s);"""
    ).format(schema=sql.Identifier("screentest"), table=sql.Identifier("persons"))

    # Assuming person_obj.id is the primary key provided by the caller, not generated by DB
    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            execute_db_and_log(
                cursor,
                query,
                (person_name, person_obj.id, person_obj.name, environment,),
                f"person record for {person_type.name}",
                person_obj.id  # Use person_obj.id for logging as it's the returned ID
            )
            logger.info(f"[screen-test] - Transaction completed for person: {person_type.name}.")
            db.connection.commit()

    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Error during person insertion for {person_type.name}: {e}")
        db.connection.rollback()
        raise
    return person_obj.id


def insert_sports(db: DatabaseManager, sport_type: SportNames, sport_obj: Sport, environment: str) -> str:
    """
     Inserts a new sport record into the 'Sports' table.

     Args:
         db (DatabaseManager): Provides database instance for connection to the screentest Database.
         sport_type (Sports): An enum representing the type of sport (e.g., Sports.MLB).
                              Its `.name` attribute is used for the `sport_type` column.
         sport_obj (Sport): A data class object containing the details for the sport (ID, name, related_content,
         umc_tag).
         environment (str): The environment tag for the record (e.g., "prod", "itms11").

     Returns:
         str: The UUID of the newly inserted sport record on success.

     Side Effects:
         - Inserts a row into the 'Sports' table.
         - Converts `related_content` (dictionary) to JSON before insertion.
         - Logs an error on failure.
     """
    sport_uuid = str(uuid.uuid4())
    sport_type_name = sport_type.name
    sports_related_content = Json(sport_obj.related_content)
    logger.info(f"[screen-test] - Processing person: {sport_type_name} with ID: {sport_uuid}")
    query = sql.SQL(
        """INSERT INTO {schema}.{table}(sport_uuid, umc_id, name, related_content, umc_tag, environment, sport_type,
        content_type)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
    ).format(schema=sql.Identifier("screentest"), table=sql.Identifier("sports"))

    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            execute_db_and_log(
                cursor,
                query,
                (sport_uuid, sport_obj.id, sport_obj.name, sports_related_content,
                 sport_obj.umc_tag, environment, sport_type_name, "SPORTS",),
                f"Sports record for {sport_type.name}",
                sport_uuid
            )
            logger.info(f"[screen-test] - Transaction completed for sport: {sport_type.name}.")
            db.connection.commit()

    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Error during sport insertion for {sport_type.name}: {e}")
        db.connection.rollback()
        raise
    return sport_uuid


def insert_umc_content(db: DatabaseManager, umc_content_type: str, umc_content_obj: UMCContentType) -> str:
    """
       Inserts a new UMC content type definition into the 'UMC_Content_Type' table.

       Args:
           db (DatabaseManager): Provides database instance for connection to the screentest Database.
           umc_content_type (str): The unique identifier for the UMC content type (e.g., "MOVIE", "TV_SHOW").
                                   This serves as the primary key for this definition table.
           umc_content_obj (UMCContentType): A data class object containing details for the UMC content type.

       Returns:
           str: The `umc_content_type` string of the newly inserted record on success.

       Side Effects:
           - Inserts a row into the 'UMC_Content_Type' table.
           - Logs an error on failure.
       """

    logger.info(f"[screen-test] - Starting insertion for UMC Content Type: {umc_content_type}")

    query = sql.SQL(
        """INSERT INTO {schema}.{table}(umc_content_type, name, uts_content_type, product_api_path, metadata_api_path)
           VALUES (%s, %s, %s, %s, %s);"""
    ).format(schema=sql.Identifier("screentest"), table=sql.Identifier("umc_content_type"))

    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            execute_db_and_log(
                cursor,
                query,
                (umc_content_type, umc_content_obj.name, umc_content_obj.uts_content_type,
                 umc_content_obj.product_api_path, umc_content_obj.metadata_api_path,),
                f"UMC Content Type record for {umc_content_type}",
                umc_content_type  # Log this as the identifier
            )
            logger.info(f"[screen-test] - Transaction completed for umc content: {umc_content_type}.")
            db.connection.commit()

    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Error during umc content insertion for {umc_content_type}: {e}")
        db.connection.rollback()
        raise
    return umc_content_type


def insert_episode(db: DatabaseManager, episode_key_name: str,
                   episode_obj: Episode, environment: str) -> str:
    """
      Inserts a new episode record into the 'Episode' table.

      Args:
          db (DatabaseManager): Provides database instance for connection to the screentest Database.
          episode_key_name (str): A unique key name for the episode, used for internal lookup.
          episode_obj (Episode): A data class object containing the details for the episode.
          environment (str): The environment tag for the record (e.g., "prod", "itms11").

      Returns:
          str: The UUID of the newly inserted episode record on success.

      Side Effects:
          - Inserts a row into the 'Episode' table.
          - Converts `required_entitlement` (list of entitlements) to JSON before insertion.
          - Also inserts a record into the 'Direct_Access' lookup table.
          - Logs an error on failure.
      """
    logger.info(f"[screen-test] - Starting insertion for Episode: {episode_key_name}")
    episode_uuid = str(uuid.uuid4())
    transformed_entitlements = [
        entitlement.name for entitlement in episode_obj.required_entitlement
    ]
    episode_required_entitlements = Json(transformed_entitlements)

    query = sql.SQL(
        """INSERT INTO {schema}.{table}(episode_uuid, show_id, umc_content_type, name, id,
        required_entitlement, content_name, environment)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
    ).format(schema=sql.Identifier("screentest"), table=sql.Identifier("episode"))

    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            execute_db_and_log(
                cursor,
                query,
                (episode_uuid, episode_obj.show_id, "EPISODE", episode_obj.name, episode_obj.id,
                 episode_required_entitlements, episode_key_name, environment,),
                f"Episode record for {episode_key_name}",
                episode_uuid
            )
            logger.info(f"[screen-test] - Transaction completed for episode: {episode_key_name}.")
            db.connection.commit()

    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Error during episode insertion for {episode_key_name}: {e}")
        db.connection.rollback()
        raise

    return episode_uuid


def insert_league_availability(db: DatabaseManager, league_offer_name: str,
                               league_availability_obj: LeagueAvailability,
                               environment: str) -> str:
    """
     Inserts a new league availability record into the 'League_Availability' table.

     Args:
         db (DatabaseManager): Provides database instance for connection to the screentest Database.
         league_offer_name (str): The name of the offer associated with this availability.
         league_availability_obj (LeagueAvailability): A data class object containing the details for the league
         availability.
         environment (str): The environment tag for the record (e.g., "prod", "itms11").

     Returns:
         str: The UUID of the newly inserted league availability record on success.

     Side Effects:
         - Inserts a row into the 'League_Availability' table.
         - Logs an error on failure.
     """
    logger.info(f"[screen-test] - Starting insertion for League Availability: {league_offer_name}")
    league_availability_uuid = str(uuid.uuid4())

    query = sql.SQL(
        """INSERT INTO {schema}.{table}(league_availability_uuid, offer_name, league, offer_value, environment)
           VALUES (%s, %s, %s, %s, %s);"""
    ).format(schema=sql.Identifier("screentest"), table=sql.Identifier("league_availability"))

    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            execute_db_and_log(
                cursor,
                query,
                (league_availability_uuid, league_offer_name, league_availability_obj.league.name,
                 league_availability_obj.value, environment,),
                f"League Availability record for {league_offer_name}",
                league_availability_uuid
            )
            logger.info(f"[screen-test] - Transaction completed for league availability: {league_offer_name}.")
            db.connection.commit()

    except psycopg2.Error as e:
        logger.error(
            f"[screen-test] - Error during league availability insertion for {league_offer_name}: {e}")
        db.connection.rollback()
        raise
    return league_availability_uuid


def insert_sporting_event(db: DatabaseManager, sporting_event_key_name: str,
                          sporting_event_obj: SportingEvent, environment: str) -> str:
    """
       Inserts a new sporting event record into the 'Sporting_Event' table.

       Args:
           db (DatabaseManager): Provides database instance for connection to the screentest Database.
           sporting_event_key_name (str): A unique key name for the sporting event, used for internal lookup.
           sporting_event_obj (SportingEvent): A data class object containing the details for the sporting event.
           environment (str): The environment tag for the record (e.g., "prod", "itms11").

       Returns:
           str: The UUID of the newly inserted sporting event record on success.

       Side Effects:
           - Inserts a row into the 'Sporting_Event' table.
           - Converts `required_entitlement` (list of entitlements) to JSON before insertion.
           - Also inserts a record into the 'Direct_Access' lookup table.
           - Logs an error on failure.
       """
    logger.info(f"[screen-test] - Starting insertion for Sporting Event: {sporting_event_key_name}")
    sporting_event_uuid = str(uuid.uuid4())
    transformed_entitlements = [
        entitlement.name for entitlement in sporting_event_obj.required_entitlement
    ]
    sporting_events_required_entitlements = Json(transformed_entitlements)

    query = sql.SQL(
        """INSERT INTO {schema}.{table}(sporting_event_uuid, event_name, name, id, required_entitlement,
         league_name, umc_content_type, environment)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
    ).format(schema=sql.Identifier("screentest"), table=sql.Identifier("sporting_event"))

    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            execute_db_and_log(
                cursor,
                query,
                (sporting_event_uuid, sporting_event_key_name, sporting_event_obj.name, sporting_event_obj.id,
                 sporting_events_required_entitlements, sporting_event_obj.league_name,
                 sporting_event_obj.type.name, environment,),
                f"Sporting Event record for {sporting_event_key_name}",
                sporting_event_uuid
            )
            logger.info(f"[screen-test] - Transaction completed for sporting event: {sporting_event_key_name}.")
            db.connection.rollback()
            db.connection.commit()

    except psycopg2.Error as e:
        logger.error(
            f"[screen-test] - Error during sporting event insertion for {sporting_event_key_name}: {e}")
        raise

    return sporting_event_uuid


def insert_movie(db: DatabaseManager, movie_key_name: str,
                 movie_obj: UMCContent, environment: str) -> str:
    """
       Inserts a new movie record into the 'Movie' table.

       Args:
           db (DatabaseManager): Provides database instance for connection to the screentest Database.
           movie_key_name (str): A unique key name for the movie, used for internal lookup.
           movie_obj (UMCContent): A data class object containing the details for the movie.
           environment (str): The environment tag for the record (e.g., "prod", "itms11").

       Returns:
           str: The UUID of the newly inserted movie record on success.

       Side Effects:
           - Inserts a row into the 'Movie' table.
           - Converts `required_entitlement` (list of entitlements) and `related_content` (dictionary) to
           JSON before insertion.
           - Also inserts a record into the 'Direct_Access' lookup table.
           - Logs an error on failure.
       """
    logger.info(f"[screen-test] - Starting insertion for Movie: {movie_key_name}")
    movie_uuid = str(uuid.uuid4())
    transformed_entitlements = [
        entitlement.name for entitlement in movie_obj.required_entitlement
    ]
    movie_required_entitlements = Json(transformed_entitlements)
    movie_related_content = Json(movie_obj.related_content)

    query = sql.SQL(
        """INSERT INTO {schema}.{table}( movie_uuid, movie_element_name, id, name, umc_content_type,
        required_entitlement, adam_id, description, related_content, environment)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    ).format(schema=sql.Identifier("screentest"), table=sql.Identifier("movie"))

    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            execute_db_and_log(
                cursor,
                query,
                (movie_uuid, movie_key_name, movie_obj.id, movie_obj.name, movie_obj.type.name,
                 movie_required_entitlements, movie_obj.adam_id, movie_obj.description, movie_related_content,
                 environment,),
                f"Movie record for {movie_key_name}",
                movie_uuid
            )
            logger.info(f"[screen-test] - Transaction completed for movie: {movie_key_name}.")
            db.connection.commit()

    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Error during movie insertion for {movie_key_name}: {e}")
        db.connection.rollback()
        raise

    return movie_uuid


def insert_tv_show(db: DatabaseManager, tv_show_key_name: str,
                   tv_show_obj: UMCContent, environment: str) -> str:
    """
      Inserts a new TV show record into the 'TV_Show' table.

      Args:
          db (DatabaseManager): Provides database instance for connection to the screentest Database.
          tv_show_key_name (str): A unique key name for the TV show, used for internal lookup.
          tv_show_obj (UMCContent): A data class object containing the details for the TV show.
          environment (str): The environment tag for the record (e.g., "prod", "itms11").

      Returns:
          str: The UUID of the newly inserted TV show record on success.

      Side Effects:
          - Inserts a row into the 'TV_Show' table.
          - Converts `required_entitlement` (list of entitlements) and `related_content` (dictionary) to
          JSON before insertion.
          - Also inserts a record into the 'Direct_Access' lookup table.
          - Logs an error on failure.
      """
    logger.info(f"[screen-test] - Starting insertion for TV Show: {tv_show_key_name}")
    tv_show_uuid = str(uuid.uuid4())
    transformed_entitlements = [
        entitlement.name for entitlement in tv_show_obj.required_entitlement
    ]
    tv_required_entitlements = Json(transformed_entitlements)
    tv_related_content = Json(tv_show_obj.related_content)

    query = sql.SQL(
        """INSERT INTO {schema}.{table}( tv_show_uuid, tv_show_element_name, id, name, umc_content_type,
        required_entitlement, adam_id, description, related_content, environment)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    ).format(schema=sql.Identifier("screentest"), table=sql.Identifier("tv_show"))

    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            execute_db_and_log(
                cursor,
                query,
                (tv_show_uuid, tv_show_key_name, tv_show_obj.id, tv_show_obj.name, tv_show_obj.type.name,
                 tv_required_entitlements, tv_show_obj.adam_id, tv_show_obj.description,
                 tv_related_content, environment,),
                f"TV Show record for {tv_show_key_name}",
                tv_show_uuid
            )
            logger.info(f"[screen-test] - Transaction completed for tv_show: {tv_show_key_name}.")
            db.connection.commit()

    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Error during tv show insertion for {tv_show_key_name}: {e}")
        db.connection.rollback()
        raise

    return tv_show_uuid


def insert_season(db: DatabaseManager, season_key_name: str,
                  season_obj: UMCContent, environment: str) -> str:
    """
       Inserts a new season record into the 'Season' table.

       Args:
           db (DatabaseManager): Provides database instance for connection to the screentest Database.
           season_key_name (str): A unique key name for the season, used for internal lookup.
           season_obj (UMCContent): A data class object containing the details for the season.
           environment (str): The environment tag for the record (e.g., "prod", "itms11").

       Returns:
           str: The UUID of the newly inserted season record on success.

       Side Effects:
           - Inserts a row into the 'Season' table.
           - Converts `required_entitlement` (list of entitlements) and `related_content` (dictionary) to
           JSON before insertion.
           - Also inserts a record into the 'Direct_Access' lookup table.
           - Logs an error on failure.
       """
    logger.info(f"[screen-test] - Starting insertion for Season: {season_key_name}")
    season_uuid = str(uuid.uuid4())

    query = sql.SQL(
        """INSERT INTO {schema}.{table}( season_uuid, season_element_name, id, name, umc_content_type,
         adam_id, description, environment)
           VALUES (%s,  %s, %s, %s, %s, %s, %s, %s);"""
    ).format(schema=sql.Identifier("screentest"), table=sql.Identifier("season"))

    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            execute_db_and_log(
                cursor,
                query,
                (season_uuid, season_key_name, season_obj.id, season_obj.name, season_obj.type.name,
                 season_obj.adam_id, season_obj.description,
                 environment,),
                f"Season record for {season_key_name}",
                season_uuid
            )
            logger.info(f"[screen-test] - Transaction completed for season: {season_key_name}.")
            db.connection.commit()

    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Error during season insertion for {season_key_name}: {e}")
        db.connection.rollback()
        raise

    return season_uuid


def insert_other_umc_content(db: DatabaseManager, other_key_name: str,
                             other_obj: UMCContent, environment: str) -> str:
    """
      Inserts a new generic UMC content record into the 'Other' table.

      Args:
          db (DatabaseManager): Provides database instance for connection to the screentest Database.
          other_key_name (str): A unique key name for the content, used for internal lookup.
          other_obj (UMCContent): A data class object containing the details for the generic content.
          environment (str): The environment tag for the record (e.g., "prod", "itms11").

      Returns:
          str: The UUID of the newly inserted content record on success.

      Side Effects:
          - Inserts a row into the 'Other' table.
          - Also inserts a record into the 'Direct_Access' lookup table.
          - Logs an error on failure.
      """
    logger.info(f"[screen-test] - Starting insertion for Other UMC Content: {other_key_name}")
    other_uuid = str(uuid.uuid4())

    query = sql.SQL(
        """INSERT INTO {schema}.{table}( other_uuid, other_element_name, id, name, type,
         adam_id, secondary_id, environment)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
    ).format(schema=sql.Identifier("screentest"), table=sql.Identifier("other"))

    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            execute_db_and_log(
                cursor,
                query,
                (other_uuid, other_key_name, other_obj.id, other_obj.name, other_obj.type.name,
                 other_obj.adam_id, other_obj.secondary_id, environment,),
                f"Other UMC Content record for {other_key_name}",
                other_uuid
            )
            logger.info(f"[screen-test] - Transaction completed for umc content: {other_key_name}.")
            db.connection.commit()

    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Error during umc content insertion for {other_key_name}: {e}")
        db.connection.rollback()
        raise

    return other_uuid


def insert_box_set(db: DatabaseManager, box_set_key_name: str,
                   box_set_obj: BoxSet, environment: str) -> str:
    """
       Inserts a new box set record into the 'Other' table.

       Args:
           db (DatabaseManager): Provides database instance for connection to the screentest Database.
           box_set_key_name (str): A unique key name for the box set, used for internal lookup.
           box_set_obj (BoxSet): A data class object containing the details for the box set.
           environment (str): The environment tag for the record (e.g., "prod", "itms11").

       Returns:
           str: The UUID of the newly inserted box set record on success.

       Side Effects:
           - Inserts a row into the 'Other' table (as a BOX_SET type).
           - Also inserts a record into the 'Direct_Access' lookup table.
           - Logs an error on failure.
       """
    logger.info(f"[screen-test] - Starting insertion for Box Set: {box_set_key_name}")
    box_set_uuid = str(uuid.uuid4())

    query = sql.SQL(
        """INSERT INTO {schema}.{table}( other_uuid, other_element_name, id, name, type,
         adam_id, show_id, environment)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
    ).format(schema=sql.Identifier("screentest"), table=sql.Identifier("other"))

    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            execute_db_and_log(
                cursor,
                query,
                (box_set_uuid, box_set_key_name, box_set_obj.id, box_set_obj.name, box_set_obj.type.name,
                 box_set_obj.adam_id, box_set_obj.show_id, environment,),
                f"Box Set record for {box_set_key_name}",
                box_set_uuid
            )
            logger.info(f"[screen-test] - Transaction completed for box set: {box_set_key_name}.")
            db.connection.commit()

    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Error during box set insertion for {box_set_key_name}: {e}")
        db.connection.rollback()
        raise

    return box_set_uuid


def insert_uts_offers(db: DatabaseManager, uts_offer_name: UTSOfferTypes,
                      uts_offer_obj: UTSOffer, environment: str) -> str:
    """
       Inserts a new UTS (Universal Test System) offer record into the 'UTS_Offer' table.

       Args:
           db (DatabaseManager): Provides database instance for connection to the screentest Database.
           uts_offer_name (UTSOffers): An enum representing the type of UTS offer (e.g., UTSOffers.TEST_OFFER).
                                       Its `.name` attribute is used for the `uts_offer_name` column.
           uts_offer_obj (UTSOffer): A data class object containing the details for the UTS offer.
           environment (str): The environment tag for the record (e.g., "prod", "itms11").

       Returns:
           str: The UUID of the newly inserted UTS offer record on success.

       Side Effects:
           - Inserts a row into the 'UTS_Offer' table.
           - Logs an error on failure.
       """
    logger.info(f"[screen-test] - Starting insertion for UTS Offer: {uts_offer_name}")
    uts_offer_uuid = str(uuid.uuid4())
    query = sql.SQL(
        """INSERT INTO {schema}.{table}( uts_offer_uuid, uts_offer_name, ad_hoc_offer_id, free_duration_period,
        offer_intent,  device_purchased, provider_name, eligibility_type, carrier_name, account_types,
        product_code, adam_id, subscription_bundle_id, general_offer_type,  environment)
           VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s);"""
    ).format(schema=sql.Identifier("screentest"), table=sql.Identifier("uts_offer"))

    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            execute_db_and_log(
                cursor,
                query,
                (uts_offer_uuid, uts_offer_name.name, uts_offer_obj.ad_hoc_offer_id,
                 uts_offer_obj.free_duration_period,
                 uts_offer_obj.offer_intent, uts_offer_obj.device_purchased, uts_offer_obj.provider_name,
                 uts_offer_obj.eligibility_type, uts_offer_obj.carrier_name, uts_offer_obj.account_types,
                 uts_offer_obj.product_code, uts_offer_obj.adam_id, uts_offer_obj.subscription_bundle_id,
                 uts_offer_obj.offer_type, environment,),
                f"Other UTS Offer record for {uts_offer_name}",
                uts_offer_uuid
            )
            logger.info(f"[screen-test] - Transaction completed for uts offers: {uts_offer_name}.")
            db.connection.commit()

    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Error during uts offers insertion for {uts_offer_name}: {e}")
        db.connection.rollback()
        raise

    return uts_offer_uuid


def insert_offers(db: DatabaseManager, offer_name: Offers,
                  offer_obj: Offer, environment: str) -> str:
    """
       Inserts a new general QA automation offer record into the 'Offer' table.

       Args:
           db (DatabaseManager): Provides database instance for connection to the screentest Database.
           offer_name (Offers): An enum representing the type of offer (e.g., Offers.DEFAULT_OFFER).
                                Its `.name` attribute is used for the `offer_type` column.
           offer_obj (Offer): A data class object containing the details for the offer.
           environment (str): The environment tag for the record (e.g., "prod", "itms11").

       Returns:
           str: The UUID of the newly inserted offer record on success.

       Side Effects:
           - Inserts a row into the 'Offer' table.
           - Converts `primary_intents`, `secondary_intents`, `editorial_events`, and `experiment` to
           JSON before insertion.
           - Logs an error on failure.
       """
    logger.info(f"[screen-test] - Starting insertion for UTS Offer: {offer_name.name}")
    offer_uuid = str(uuid.uuid4())

    query = sql.SQL(
        """INSERT INTO {schema}.{table}( offer_uuid, id, name, entity_id, primary_intents, secondary_intents,
         editorial_events, experiment, entity_type, status, deleted, created_by_id, version, published, latest,
          environment, offer_type)
           VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    ).format(schema=sql.Identifier("screentest"), table=sql.Identifier("offer"))

    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            execute_db_and_log(
                cursor,
                query,
                (offer_uuid, offer_obj.id, offer_obj.name, offer_obj.entityId, Json(offer_obj.primaryIntents),
                 Json(offer_obj.secondaryIntents), Json(offer_obj.editorialEvents), Json(offer_obj.experiment),
                 offer_obj.entityType, offer_obj.status, offer_obj.deleted, offer_obj.createdById, offer_obj.version,
                 offer_obj.published, offer_obj.latest, environment, offer_name.name,),
                f"Other Offer record for {offer_name.name}",
                offer_uuid
            )
            logger.info(f"[screen-test] - Transaction completed for offer: {offer_name}.")
            db.connection.commit()

    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Error during offers insertion for {offer_name}: {e}")
        db.connection.rollback()
        raise

    return offer_uuid


def insert_storefront(db: DatabaseManager, country_code: str,
                      storefront_response: dict) -> str:
    """
       Inserts a new general QA automation offer record into the 'Offer' table.

       Args:
        db (DatabaseManager): Provides database instance for connection to the screentest Database.
        storefront_response: Dictionary of the API response based on country code key, contains things like country, default_language and storefront_id
        country_code: str initials symbolizing a specific country

       Returns:
           str: The UUID of the newly inserted offer record on success.

       Side Effects:
           - Inserts a row into the 'Offer' table.
           - Converts `primary_intents`, `secondary_intents`, `editorial_events`, and `experiment` to
           JSON before insertion.
           - Logs an error on failure.
       """
    logger.info(f"[screen-test] - Starting insertion for Storefront: {storefront_response["storefrontId"]}")

    query = sql.SQL(
        """INSERT INTO {schema}.{table}( country_code, country, default_language, default_locale, languages_supported, locales_supported, storefront_id)
           VALUES ( %s, %s, %s, %s, %s, %s, %s);"""
    ).format(schema=sql.Identifier("screentest"), table=sql.Identifier("storefront"))

    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            execute_db_and_log(
                cursor,
                query,
                (country_code, storefront_response["country"], storefront_response["defaultLanguage"],
                 storefront_response["defaultLocale"],
                 Json(storefront_response["languagesSupported"]), Json(storefront_response["localesSupported"]),
                 storefront_response["storefrontId"],
                 ), f"storefront id: {storefront_response["storefrontId"]}")
            logger.info(f"[screen-test] - Transaction completed for storefront: {storefront_response["storefrontId"]}.")
            db.connection.commit()

    except psycopg2.Error as e:
        logger.error(f"[screen-test] - Error during offers insertion for {storefront_response["storefrontId"]}: {e}")
        db.connection.rollback()
        raise

    return storefront_response["storefrontId"]
