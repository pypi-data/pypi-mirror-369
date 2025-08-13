import os
import time

import database_fetches
import psycopg2
import pytest
from account_control.account_services import client_account_from_plato, add_subscription_to_account
from database_control.database_manager import DatabaseManager
from database_insertions import insert_account
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from test_data_classes import Account
from test_data_keys import AccountTypes

from cakepy.utils.http_clients.plato_client import PlatoClient
from cakepy.utils.report_utils.logger import logger


# --- Fixtures for DatabaseManager Testing ---
@pytest.fixture(scope="session")
def screentest_db_connection():
    """
    Connects to an existing screentest database for the entire test session.
    """

    logger.info("\n[screen-test] Connecting to existing PostgreSQL DB: screentest")
    try:
        db = DatabaseManager()
        db.connect_to_database()
        logger.info("Database Connected....")
        yield db
    except Exception as e:
        logger.error(f"\n[screen-test] Error connecting to PostgreSQL database: {e}")
        pytest.fail(f"Could not connect to PostgreSQL database: {e}")
    finally:
        if 'db' in locals() and db:
            db.close_connection()
            logger.info("\n[screen-test] Disconnected from existing PostgreSQL DB: screentest.")


# --- Fixtures for DatabaseManager Testing ---
@pytest.fixture(scope="session")
def initialize_account_collections(account_command):
    """

    Pulls account information.
    """
    account_collection = account_command.get_account_collections()
    logger.info("[screentest] Fetched account information")
    return account_collection


@pytest.fixture(scope="function")
def refresh_account_collections(account_command):
    """
    Refreshes account information.
    """
    account_collection = account_command.get_account_collections()
    logger.info("[screentest] Fetched account information")
    return account_collection


@pytest.fixture(scope="session")
def account_command(screentest_db_connection):
    """
    Provides an instance of TestAccountOperations for database interactions with an account.
    """
    logger.info("[screentest] - Setting up TestAccountOperations instance.")
    ops = TestAccountOperations(screentest_db_connection)
    yield ops
    logger.info("[screentest] - Tearing down TestAccountOperations instance.")


# Write NEW Account Types with new subscription to Database
@pytest.fixture(scope="function")
def create_and_write_to_db_TV_PLUS_SUBSCRIBED(screentest_db_connection, tv_plus_subscribed_client_account):
    '''
    Creates new TV_Plus Subscribed Account and adds row to DB - Not possible if account type already in database
    :param screentest_db_connection: Access Database
    :param tv_plus_subscribed_client_account:  Create new account + subscription
    :return: Bool of successful creation + write to DB
    '''
    account = tv_plus_subscribed_client_account
    logger.info(f"[screen-test] Account created {account}")
    try:
        db = DatabaseManager()
        db.connect_to_database()
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            insert_account(cursor, AccountTypes.TV_PLUS_SUBSCRIBED, account, "itms11")
            logger.info("[screen-test] Account write successful to DB")
            db.connection.commit()
            db.connection.close()
            return True
    except Exception as e:
        logger.error("[screen-test] Account did not write to DB", e)
        return False


@pytest.fixture(scope="function")
def create_and_write_to_db_TV_PLUS_UNSUBSCRIBED(screentest_db_connection, unsubscribed_client_account):
    '''
    Creates new TV_Plus UnSubscribed Account and adds row to DB - Not possible if account type already in database
    :param screentest_db_connection: Access Database
    :param unsubscribed_client_account:  Create new account + subscription
    :return: Bool of successful creation + write to DB
    '''
    account = unsubscribed_client_account
    try:
        db = DatabaseManager()
        db.connect_to_database()
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            insert_account(cursor, AccountTypes.TV_PLUS_UNSUBSCRIBED, account, "itms11")
            logger.info("[screen-test] Account write successful to DB")
            db.connection.commit()
            db.connection.close()
            return True
    except Exception as e:
        logger.error("[screen-test] Account did not write to DB", e)
        return False


@pytest.fixture(scope="function")
def create_and_write_to_db_MLS_SUBSCRIBED_ANNUALLY(screentest_db_connection, mls_annual_client_account):
    '''
   Creates new MLS Annual Subscribed Account and adds row to DB - Not possible if account type already in database
   :param screentest_db_connection: Access Database
   :param mls_annual_client_account:  Create new account + subscription
   :return: Bool of successful creation + write to DB
   '''
    account = mls_annual_client_account
    try:
        db = DatabaseManager()
        db.connect_to_database()
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            insert_account(cursor, AccountTypes.MLS_SUBSCRIBED_ANNUALLY, account, "itms11")
            logger.info("[screen-test] Account write successful to DB")
            db.connection.commit()
            db.connection.close()
            return True
    except Exception as e:
        logger.error("[screen-test] Account did not write to DB", e)
        return False


@pytest.fixture(scope="function")
def create_and_write_to_db_MLS_SUBSCRIBED(screentest_db_connection, mls_monthly_client_account):
    '''
   Creates new MLS Monthly Subscribed Account and adds row to DB - Not possible if account type already in database
   :param screentest_db_connection: Access Database
   :param mls_monthly_client_account:  Create new account + subscription
   :return: Bool of successful creation + write to DB
   '''
    account = mls_monthly_client_account
    try:
        db = DatabaseManager()
        db.connect_to_database()
        with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            insert_account(cursor, AccountTypes.MLS_SUBSCRIBED, account, "itms11")
            logger.info("[screen-test] Account write successful to DB")
            db.connection.commit()
            db.connection.close()
            return True
    except Exception as e:
        logger.error("[screen-test] Account did not write to DB", e)
        return False


#
# # Update Existing Accounts from Database with New Subscription
# @pytest.fixture(scope="function")
# def update_account_with_new_subscription_TV_PLUS_SUBSCRIBED(screentest_db_connection,
#                                                             tv_plus_subscribed_client_account):
#     '''
#    Updates TV_Plus Subscribed Account and updates corresponding row in DB - Not possible if account type not in database
#    :param screentest_db_connection: Access Database
#    :param tv_plus_subscribed_client_account:  Create new account + subscription ,update value in DB
#    :return: Bool of successful creation + update in DB
#    '''
#     db = DatabaseManager()
#     db.connect_to_database()
#     account = tv_plus_subscribed_client_account
#     if account is None:
#         return False
#     try:
#         screentest_db_connection.update_account("Accounts", AccountTypes.TV_PLUS_SUBSCRIBED, account)
#         return True
#     except Exception as e:
#         logger.error(f"[screen-test] Account did not update in DB with error: {e}")
#         return False

#
# @pytest.fixture(scope="function")
# def update_account_with_new_subscription_TV_PLUS_UNSUBSCRIBED(screentest_db_connection, unsubscribed_client_account):
#     '''
#    Updates TV_Plus UnSubscribed Account and updates corresponding row in DB
#    - Not possible if account type not in database
#    :param screentest_db_connection: Access Database
#    :param unsubscribed_client_account:  Create new account + subscription ,update value in DB
#    :return: Bool of successful creation + update in DB
#    '''
#     account = unsubscribed_client_account
#     if account is None:
#         return False
#     try:
#         screentest_db_connection.update_account("Accounts", AccountTypes.TV_PLUS_UNSUBSCRIBED, account)
#         return True
#     except Exception as e:
#         logger.error(f"[screen-test] Account did not update in DB with error: {e}")
#         return False
#
#
# @pytest.fixture(scope="function")
# def update_account_with_new_subscription_MLS_SUBSCRIBED(screentest_db_connection, mls_monthly_client_account):
#     '''
#    Updates MLS Monthly Account and updates corresponding row in DB - Not possible if account type not in database
#    :param screentest_db_connection: Access Database
#    :param mls_monthly_client_account:  Create new account + subscription ,update value in DB
#    :return: Bool of successful creation + update in DB
#    '''
#     account = mls_monthly_client_account
#     if account is None:
#         return False
#     try:
#         screentest_db_connection.update_account("Accounts", AccountTypes.MLS_SUBSCRIBED, account)
#         return True
#     except Exception as e:
#         logger.error(f"[screen-test] Account did not update in DB with error: {e}")
#         return False
#
#
# @pytest.fixture(scope="function")
# def update_account_with_new_subscription_MLS_SUBSCRIBED_ANNUALLY(screentest_db_connection, mls_annual_client_account):
#     '''
#        Updates MLS Annual Account and updates corresponding row in DB - Not possible if account type not in database
#        :param screentest_db_connection: Access Database
#        :param mls_annual_client_account:  Create new account + subscription ,update value in DB
#        :return: Bool of successful creation + update in DB
#        '''
#     account = mls_annual_client_account
#     if account is None:
#         return False
#     try:
#         screentest_db_connection.update_account("Accounts", AccountTypes.MLS_SUBSCRIBED_ANNUALLY, account)
#         return True
#     except Exception as e:
#         logger.error(f"[screen-test] Account did not update in DB with error: {e}")
#         return False
#

@pytest.fixture(scope='session')
def plato_client():
    """
    JUBEO_KEY expires August 9th 2025
    Go here to generate a new key: https://jubeo.apple.com/ui/keys/generate
    """
    return PlatoClient('itms11', jubeo_key=os.getenv("JUBEO_KEY", "6cd499c0-0643-4958-b9a0-0fbb1ed1eb0a"))


@pytest.fixture(scope='session')
def unsubscribed_client_account(plato_client) -> Account:
    account = client_account_from_plato(plato_client)[1]
    logger.info([f"[Plato] Account created: {account}"])
    return account


@pytest.fixture(scope='session')
def tv_plus_subscribed_client_account(plato_client) -> Account:
    client, account = client_account_from_plato(plato_client)
    logger.info([f"[Plato] Account created: {account}"])

    for i in range(3):
        time.sleep(i)
        is_bought = client.buy_tv_plus(account.email, subscription="paid", password=account.decrypt_password())
        if is_bought:
            logger.info([f"[Plato] TV+ subscription added: {account}"])
            return account
    logger.error(f"[Plato] Failed to add TV+ Subscription for: {account}")
    return None


@pytest.fixture(scope='session')
def mls_monthly_client_account(plato_client) -> Account:
    subscription_name = 'mls_monthly'
    client, account = client_account_from_plato(plato_client, subscription_name)
    logger.info([f"[Plato] Account created: {account}"])

    return add_subscription_to_account(client, account, subscription_name)


@pytest.fixture(scope='session')
def mls_annual_client_account(plato_client) -> Account:
    subscription_name = 'mls_annually'
    client, account = client_account_from_plato(plato_client, subscription_name)
    logger.info([f"[Plato] Account created: {account}"])

    return add_subscription_to_account(client, account, subscription_name)


# ---- Helper Class for Operations on a Database to Accounts Table -----
class TestAccountOperations:
    """
    A helper class for tests to perform various operations on account data
    within the test database.
    """

    def __init__(self, db_instance: DatabaseManager):
        self.db = db_instance

    def fetch_account(self, table_name: str, account_type: AccountTypes):
        """Fetches a specific account row."""
        return database_fetches.fetch_account(table_name, account_type)

    def fetch_account_value(self, table_name: str, account_type: AccountTypes, selection: str):
        """Fetches a specific account row."""
        return database_fetches.fetch_value(table_name, account_type, selection)

    # def update_account_value(self, table_name: str, account_type: AccountTypes, account: Account):
    #     """
    #     Updates an account dsid.
    #     """
    #     update_account(table_name, account_type, account)

    def delete_account(self, table_name: str, account_type: AccountTypes):
        """
        Deletes an account row.
        """
        self.db.delete_account(table_name, account_type)

    # Refresh account collections if updates are made to get freshest data from db
    def get_account_collections(self):
        '''
        Pulls Accounts Information
        '''

        account_collection = {}

        try:
            with self.db.connection.cursor(cursor_factory=RealDictCursor) as cur:
                query = sql.SQL("""SELECT *
                                   FROM {schema}.{table};""").format(schema=sql.Identifier("screentest"),
                                                                     table=sql.Identifier("Accounts"))
                cur.execute(query)
                account_rows = cur.fetchall()
            for account_data in account_rows:
                account_type_name = AccountTypes[account_data.get('account_type')]
                new_account = Account(dsid=account_data.get('dsid'),
                                      cid=account_data.get('cid'),
                                      email=account_data.get('email', ""),
                                      encrypted_password=account_data.get('encrypted_password'),
                                      protected=account_data.get('protected', False))
                account_collection[account_type_name] = new_account
                # environment and account_id current exist in table as well, but are being restructured
            return account_collection
        except psycopg2.Error as e:
            logger.error(f"[screentest] - Error while fetching table: {e}")
            return None

        finally:
            if self.db:
                self.db.close_connection()
                logger.info("[screentest] -  Disconnected from existing PostgreSQL DB: screentest.")
