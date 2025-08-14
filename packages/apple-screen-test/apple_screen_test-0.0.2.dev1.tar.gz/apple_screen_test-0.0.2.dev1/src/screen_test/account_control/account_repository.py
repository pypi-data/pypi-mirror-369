import psycopg2
from database_manager import DatabaseManager
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

from cakepy.utils.report_utils.logger import logger
from data_structures.test_data_classes import Account
from data_structures.test_data_keys import AccountTypes

'''
Fetches all accounts from the database "Accounts" table
Params - db: DatabaseManager -> Should have an active connection/ call .connect_to_database() beforehand
Returns account_collection -> dict of Accounts as {AccountType: Account(dsid, cid, email, password, protected), ...}
'''


def get_account_collections(screentest_db_connection: DatabaseManager):
    account_collection = {}
    logger.info("[screentest] -  Fetching Accounts from Database")
    try:
        with screentest_db_connection.connection.cursor(cursor_factory=RealDictCursor) as cur:
            query = sql.SQL("""SELECT *
                               FROM {schema}.{table};""").format(schema=sql.Identifier("screentest"),
                                                                 table=sql.Identifier("Accounts"))
            cur.execute(query)
            account_rows = cur.fetchall()
        for account_data in account_rows:
            account_type_name = AccountTypes[account_data.get('account_type')]
            new_account = Account(dsid=account_data.get('dsid', ""),
                                  cid=account_data.get('cid', ""),
                                  email=account_data.get('email', ""),
                                  encrypted_password=account_data.get('encrypted_password'),
                                  protected=account_data.get('protected', False))
            account_collection[account_type_name] = new_account
            # environment and account_id current exist in table as well, but are being restructured
        return account_collection
    except psycopg2.Error as e:
        logger.error(f"[screentest] - Error while fetching table: {e}")
    return None


'''Write NEW Account Types with new subscription to Database
Params - db: DatabaseManager
- account_type: AccountTypes
- account - Account
Returns Bool on if the account successfully created and wrote to the database
'''


def write_new_account_to_database(db: DatabaseManager, account_type: AccountTypes, account: Account):
    try:
        with db.connection.cursor(cursor_factory=RealDictCursor) as cur:
            query = sql.SQL(
                """INSERT INTO {schema}.{table}(account_type, dsid, cid, email, encrypted_password, protected)
                   VALUES (%s, %s, %s, %s, %s, %s);""").format(schema=sql.Identifier("screentest"),
                                                               table=sql.Identifier("Accounts"))
            cur.execute(query,
                        (str(account_type.name), account.dsid, account.cid,
                         account.email,
                         account.encrypted_password,
                         account.protected,
                         ))

            db.connection.commit()
            return True
    except psycopg2.Error as e:
        logger.error(f"[screentest] - Error while inserting new account to database: {e}")
        return False


'''Updating Existing Account Types with new subscription in Database
Params - db: DatabaseManager
- account_type: AccountTypes
- account - Account
Returns Bool on if the account successfully created and wrote to the database
'''


def update_account_in_database(screentest_db_connection, account: Account, account_type: str):
    if account is None:
        return False
    else:
        try:
            with screentest_db_connection.connection.cursor(cursor_factory=RealDictCursor) as cur:
                query = sql.SQL("""UPDATE {schema}.{table}
                                   SET dsid = %s, cid = %s, email = %s, encrypted_password = %s, protected = %s
                                   WHERE account_type = %s;""").format(schema=sql.Identifier("screentest"),
                                                                       table=sql.Identifier("Accounts"))
                cur.execute(query,
                            (account.dsid, account.cid,
                             account.email,
                             account.encrypted_password,
                             account.protected, account_type
                             ))
                if cur.rowcount == 0:
                    logger.info("[screentest] - No row found with id {} in table {}".format(account_type, "Accounts"))
                    screentest_db_connection.connection.rollback()
                    return False
                else:
                    screentest_db_connection.connection.commit()
                    return True
        except psycopg2.Error as e:
            logger.error(f"[screentest] - Error while inserting new account to database {e}")
            return False

#
# # Update Existing Accounts from Database with New Subscription
# @pytest.fixture(scope="function")
# def update_account_with_new_subscription_tv_plus_subscribed(tv_plus_subscribed_client_account):
#     account = tv_plus_subscribed_client_account
#     account_type = AccountTypes.TV_PLUS_SUBSCRIBED.name
#     result = update_account_in_database(account, account_type)
#     yield result
#
#
# # Helper to Update Account Subscription in Database
# def update_account_in_database(account: Account, account_type: str):
#     if account is None:
#         return False
#     else:
#         db = DatabaseManager()
#         db.connect_to_database()
#         try:
#             with db.connection.cursor(cursor_factory=RealDictCursor) as cur:
#                 query = sql.SQL("""UPDATE {schema}.{table}
#                                    SET dsid = %s, cid = %s, email = %s, encrypted_password = %s, protected = %s
#                                    WHERE account_type = %s;""").format(schema=sql.Identifier("screentest"),
#                                                                        table=sql.Identifier("Accounts"))
#                 cur.execute(query,
#                             (account.dsid, account.cid,
#                              account.email,
#                              account.encrypted_password,
#                              account.protected, account_type
#                              ))
#                 db.connection.commit()
#                 return True
#         except psycopg2.Error as e:
#             db.connection.rollback()  # Remove any failed changes from commit
#             logger.error(f"[screentest] - Error while inserting new account to database {e}")
#             return False
