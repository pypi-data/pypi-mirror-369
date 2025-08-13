import database_fetches
from assertpy import assert_that

from data import itms11
from data.itms11 import canvases, collections
from data.itms11.direct_access import direct_access_movies
from data.itms11.direct_access.direct_access_mls import MLS_LEAGUE_NAME
from database_fetches import fetch_canvases_with_collections_and_displays, fetch_direct_access
from database_insertions import insert_full_canvas_structure, insert_movie, insert_collection, insert_sporting_event
from database_manager import DatabaseManager
from test_data_classes import Account, Canvas, Collection, UMCContent, UMCContentType, MOVIE, SportingEvent, \
    UPCOMING_SPORTING_EVENT, LIVE_SPORTING_EVENT
from test_data_keys import AccountTypes, CanvasNames, CanvasTypes, CollectionNames, ContentDatas, ContentTypes


def test_can_connect_to_database(screentest_db_connection):
    """
    Tests that a connection can be established.
    """
    # Connect to Database
    connection = screentest_db_connection.get_connection()

    # Assert connection was successful
    assert_that(connection).is_not_none()


def test_pull_dsid(account_command):
    """
    Tests that a dsid can be pulled using an account type and that a non-existent account_Type will not return a dsid.
    """
    db = DatabaseManager()
    db.connect_to_database()
    dsid = database_fetches.fetch_value(db, "account", AccountTypes.MCC1_INTRO, "dsid", "itms11")
    assert_that(dsid).is_equal_to("995000000629498143")


def test_pull_cid(account_command):
    """
    Tests that a cid can be pulled using an account type and that a non-existent account_Type will not return a cid.
    """

    cid = account_command.fetch_account_value("accounts", AccountTypes.MCC1_INTRO, "cid")

    assert_that(cid).is_equal_to("4f1c0d2dbd49400483b5da476390cdc1002")

    none_cid = account_command.fetch_account_value("Accounts", None, "cid")
    assert_that(none_cid).is_equal_to(None)


def test_pull_account(account_command):
    """
    Tests that an account can be pulled and the data matches
    """
    # Connect to Database
    account = account_command.fetch_account("accounts", AccountTypes.MCC1_INTRO)
    original_account = Account(dsid='998000005433469016', cid='c55bf6ab75da423895c19a66dd9d1f7d001',
                               email='mls_annually+ketfhb@apple.com', encrypted_password=b'WmlqcmNia3Iz',
                               protected=False)
    assert_that(account.dsid).is_equal_to(original_account.dsid)
    assert_that(account.cid).is_equal_to(original_account.cid)
    assert_that(account.email).is_equal_to(original_account.email)


def test_canvas_insertion_no_additional_content(screentest_db_connection):
    '''
    :return: True on success
    '''
    # Connect to Database
    screentest_db_connection.connect_to_database()
    new_canvas_type = CanvasNames.GENERIC_GENRE
    new_canvas = Canvas(canvas_type=CanvasTypes.GENRE, id="123DefaultTest", name="Generic Test for Canvas" )
    result = insert_full_canvas_structure(screentest_db_connection, new_canvas_type, new_canvas, "itms11")
    screentest_db_connection.close_connection()
    assert_that(result).is_not_none()

def test_canvas_insertion_with_collections(screentest_db_connection):
    '''
    Test to insert a new canvas with collections into the database
    The canvas info here is paired down, but any attributed from teh Canvas dataclass can be added via the object instance
    NOTE: to re-run the current version must be deleted or the collection id must be changed otherwise the insertion will the fail
    :param screentest_db_connection:
    :return: True on success
    '''
    screentest_db_connection.connect_to_database()
    new_canvas_type = CanvasNames.GENERIC_GENRE
    new_canvas = Canvas(canvas_type=CanvasTypes.GENRE, id="123DefaultTest2", name="Generic Test for Canvas with Collections", collection_items={ CollectionNames.APPLE_ORIGINALS: Collection(collection_id="Default Collection")})
    result = insert_full_canvas_structure(screentest_db_connection, new_canvas_type, new_canvas, "itms11")
    screentest_db_connection.close_connection()
    assert_that(result).is_not_none()


def test_canvas_insertion_with_media_content(screentest_db_connection):
    '''
    Test  to insert a canvas with media content (formerly Direct Access). The piece(s) of media content must be
    inserted prior to the canvas that contains them OR insert a blank media_content dictionary and stitch the
    name:id pairs manually in Postico.
    :param screentest_db_connection:
    :return: True on success
    '''
    screentest_db_connection.connect_to_database()
    #Inserting a new movie
    new_movie = UMCContent(id= "123_Test_Movie", name="The Test_Movie", type= MOVIE )
    insert_movie(screentest_db_connection, "123_Test_Movie", new_movie, "itms11")

    # Inserting new Canvas
    new_canvas_type = CanvasNames.GENERIC_GENRE
    new_canvas = Canvas(canvas_type=CanvasTypes.GENRE, id="123DefaultTest3",
                        name="Generic Test for Canvas with MMedia Content", media_content={"Movie": str(new_movie.id)})
    result = insert_full_canvas_structure(screentest_db_connection, new_canvas_type, new_canvas, "itms11")
    screentest_db_connection.close_connection()
    assert_that(result).is_not_none()

def test_collection_insertion(screentest_db_connection):
    '''
   Test to insert a new collection into the database
   NOTE: to re-run the current version must be deleted or the collection id must be changed or the insertion will the fail
   :return: True on success
    '''
    screentest_db_connection.connect_to_database()
    collection_type = CollectionNames.APPLE_ORIGINALS
    new_collection = Collection(collection_id="Default Collection 2")
    result = insert_collection(screentest_db_connection, collection_type, new_collection, "itms11")
    screentest_db_connection.close_connection()
    assert_that(result).is_not_none()

def test_direct_access_insertion_movie(screentest_db_connection):
    '''
    Test to insert a movie as part of direct access content
    NOTE: To Re-run the previous version must be deleted or the id must be changed
    :param screentest_db_connection:
    :return: True on success
    '''
    screentest_db_connection.connect_to_database()
    # Inserting a new movie
    new_movie = UMCContent(id="123_Test_Movie_2", name="The Test_Movie Part 2", type=MOVIE)
    result = insert_movie(screentest_db_connection, "123_Test_Movie_2", new_movie, "itms11")
    screentest_db_connection.close_connection()
    assert_that(result).is_not_none()

def test_direct_access_insertion_sporting_event(screentest_db_connection):
    '''
    Test to insert a sporting event as part of direct access content
    NOTE: To Re-run the previous version must be deleted or the id must be changed
    :param screentest_db_connection:
    :return: True on success
    '''
    screentest_db_connection.connect_to_database()
    sporting_event = "upcoming_test_sporting_event_2"
    new_sporting_event = SportingEvent(
    id='umc.cse.1qmzr2rhzs267qs6czmj9xi0r',  # this event expires
    name='',
    type=LIVE_SPORTING_EVENT
)
    result = insert_sporting_event(screentest_db_connection, sporting_event, new_sporting_event, "itms11")
    screentest_db_connection.close_connection()
    assert_that(result).is_not_none()


def test_canvas_fetch(screentest_db_connection):
    '''
    Test fetch full canvas dictionary from database
    :param screentest_db_connection:
    :return: True on success
    '''
    expected_canvas = canvases.CANVASES[CanvasNames.SHOWTIME_MCCORMICK]
    fetched_canvas = fetch_canvases_with_collections_and_displays(screentest_db_connection, "itms11")[CanvasNames.SHOWTIME_MCCORMICK]
    assert_that(expected_canvas).is_equal_to(fetched_canvas)


def test_collection_fetch(screentest_db_connection):
    '''
    Test fetch full collection dictionary from database
    :param screentest_db_connection:
    :return: True on success
    '''
    expected_collections = collections.COLLECTIONS[CollectionNames.MLS_CHANNEL_UPSELL]
    fetched_collections = database_fetches.fetch_collections_with_displays(screentest_db_connection, "itms11")[CollectionNames.MLS_CHANNEL_UPSELL]
    assert_that(expected_collections).is_equal_to(fetched_collections)

def test_direct_access_fetch_movie(screentest_db_connection):
    '''
    Test fetch movies dictionary info from database
    :param screentest_db_connection:
    :return: True on success
    '''
    movie_tv_plus_the_elephant_queen = UMCContent(
        id='umc.cmc.1uagm4smdgondtxfbcqy5ssmn',
        name='The Elephant Queen',
        type=MOVIE,
        required_entitlement=[CanvasNames.TV_PLUS],
    )
    expected_movie = database_fetches.fetch_direct_access_table(screentest_db_connection, "movie", "itms11")["movie_tv_plus_the_elephant_queen"]
    assert_that(movie_tv_plus_the_elephant_queen).is_equal_to(expected_movie)

def test_direct_access_fetch_sporting_event(screentest_db_connection):
    '''
    Test fetch for upcoming sporting event info from database
    :param screentest_db_connection:
    :return: True on success
    '''
    upcoming_sporting_event_2 = SportingEvent(
        id='umc.cse.1qmzr2rhzs267qs6czmj9xi0r',  # this event expires
        name='',
        type=LIVE_SPORTING_EVENT
    )
    expected_event = database_fetches.fetch_direct_access_table(screentest_db_connection, "sporting_event", "itms11")["upcoming_sporting_event_2"]
    assert_that(upcoming_sporting_event_2).is_equal_to(expected_event)


'''
For Later
def _normalize_for_semantic_comparison(obj: Any) -> Any:
    """
    Recursively transforms an object into a canonical representation for semantic comparison.
    - Dictionaries are converted to dictionaries with sorted keys.
    - Lists/tuples are processed recursively.
    - Dataclass instances are converted to dictionaries of their normalized fields.
    - Enum members are represented by their values for consistent sorting.
    """
    if isinstance(obj, dict):
        # Normalize dictionary: recursively normalize keys and values,
        # then sort items and convert back to a dictionary.
        # Use str() for the key in lambda for robust sorting of mixed key types
        # (e.g., Enum members and strings) that might appear as dict keys.
        return dict(sorted([
            (_normalize_for_semantic_comparison(k), _normalize_for_semantic_comparison(v))
            for k, v in obj.items()
        ], key=lambda item: str(item[0]))) # Sort by string representation of the key

    elif isinstance(obj, (list, tuple)):
        # Recursively normalize elements.
        # If the order of elements in lists/tuples should also be ignored,
        # you would add a `sorted()` call here: `return type(obj)(sorted(normalized_elements))`.
        # For now, we assume list/tuple order matters unless it's a dictionary key.
        return type(obj)(_normalize_for_semantic_comparison(elem) for elem in obj)

    elif isinstance(obj, Enum):
        # Represent enum by its value (e.g., the integer) for consistent comparison.
        # If the enum's name is more semantically meaningful for comparison, use obj.name.
        return obj.value # or obj.name

    elif hasattr(obj, '__dataclass_fields__'): # Check if it's a dataclass instance
        # Convert dataclass to a dictionary of its fields, then normalize that dictionary.
        normalized_dict_representation = {}
        for field in dataclasses.fields(obj):
            field_value = getattr(obj, field.name)
            normalized_dict_representation[field.name] = _normalize_for_semantic_comparison(field_value)
        
        # Sort the fields of the dataclass's dict representation for consistent comparison
        # (This ensures the dataclass itself is compared by its fields' values,
        # and the order of fields doesn't matter if the default dataclass __eq__ is not used).
        return dict(sorted(normalized_dict_representation.items()))

    else:
        # For primitives (int, str, bool, None) and other non-dataclass objects, return as is.
        return obj

def are_canvases_semantically_equal(canvas1: Any, canvas2: Any) -> bool:
    """
    Compares two Canvas objects (or any complex Python objects) semantically,
    ignoring the insertion order of keys in dictionaries and the order of fields
    in dataclass instances.
    """
    normalized_canvas1 = _normalize_for_semantic_comparison(canvas1)
    normalized_canvas2 = _normalize_for_semantic_comparison(canvas2)
    
    return normalized_canvas1 == normalized_canvas2
'''