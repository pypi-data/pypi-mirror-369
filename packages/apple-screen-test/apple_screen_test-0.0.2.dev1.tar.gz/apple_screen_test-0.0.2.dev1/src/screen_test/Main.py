'''
USING AS SCRATCHPAD DURING BUILD
NOT INTENDED FOR OFFICIAL FUNCTIONS
RECOMMEND NOT TO BUILD ANYTHING IN THIS FILE

'''
from data.itms11.direct_access import direct_access_movies
from database_fetches import fetch_canvases_with_collections_and_displays
from database_insertions import insert_canvas, insert_full_canvas_structure
from database_manager import DatabaseManager
from test_data_classes import Canvas, Collection, Context
from test_data_keys import CanvasNames, CollectionNames, DisplayTypes


def main():

    db = DatabaseManager()
    db.connect_to_database()

    # Overwrites the Prod database with the dev database
    # db.dump_and_restore_database("dev", "prod", False, True)


if __name__ == "__main__":
    main()
