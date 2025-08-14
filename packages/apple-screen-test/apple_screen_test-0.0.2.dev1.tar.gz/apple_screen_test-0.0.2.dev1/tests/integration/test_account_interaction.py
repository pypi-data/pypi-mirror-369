from assertpy import assert_that

from database_fetches import fetch_table
from database_manager import DatabaseManager
from test_data_keys import AccountTypes

'''
THESE CREATE ACCOUNT TESTS ARE NOT USABLE MORE THAN ONCE DUE TO SQL DB RESTRICTIONS
USE THE UPDATE TESTS WHEN TESTING IF NEW SUBSCRIPTIONS OVERWRITE DB DATA
'''


def test_new_account_to_db_TV_PLUS_SUBSCRIBED(create_and_write_to_db_TV_PLUS_SUBSCRIBED):
    assert_that(create_and_write_to_db_TV_PLUS_SUBSCRIBED).is_true()


def test_new_account_to_db_TV_PLUS_UNSUBSCRIBED(create_and_write_to_db_TV_PLUS_UNSUBSCRIBED):
    assert_that(create_and_write_to_db_TV_PLUS_UNSUBSCRIBED).is_true()


def test_new_account_to_db_MLS_SUBSCRIBED_ANNUALLY(create_and_write_to_db_MLS_SUBSCRIBED_ANNUALLY):
    assert_that(create_and_write_to_db_MLS_SUBSCRIBED_ANNUALLY).is_true()


def test_new_account_to_db_MLS_SUBSCRIBED(create_and_write_to_db_MLS_SUBSCRIBED):
    assert_that(create_and_write_to_db_MLS_SUBSCRIBED).is_true()

#TESTS IF SUBSCRIPTIONS UPDATE - Needs Adjusted Update Functions to match new structure
#
# def test_update_account_to_db_TV_PLUS_SUBSCRIBED(update_account_with_new_subscription_TV_PLUS_SUBSCRIBED):
#     '''
#     Tests that account values are updated in the database after a new account/subscription is created for a
#     TV_PLUS_SUBSCRIBED account
#     '''
#     old_value = fetch_table("account", "itms11")[AccountTypes.TV_PLUS_SUBSCRIBED]
#     assert_that(update_account_with_new_subscription_TV_PLUS_SUBSCRIBED).is_true()
#     new_value = fetch_table(db, "account", "itms11")[AccountTypes.TV_PLUS_SUBSCRIBED]
#     assert_that(old_value).is_equal_to(new_value)
#
#
# def test_update_account_to_db_TV_PLUS_UNSUBSCRIBED(update_account_with_new_subscription_TV_PLUS_UNSUBSCRIBED,
#                                                    get_account_collection):
#     """
#     Tests that account values are updated in the database after a new account/subscription is created for a
#     TV_PLUS_UNSUBSCRIBED account
#     """
#     old_value = get_account_collection[AccountTypes.TV_PLUS_UNSUBSCRIBED]
#     assert_that(update_account_with_new_subscription_TV_PLUS_UNSUBSCRIBED).is_true()
#     new_value = get_account_collection[AccountTypes.TV_PLUS_UNSUBSCRIBED]
#     assert_that(old_value).is_equal_to(new_value)
#
#
# def test_update_account_to_db_MLS_SUBSCRIBED_ANNUALLY(update_account_with_new_subscription_MLS_SUBSCRIBED_ANNUALLY,
#                                                       get_account_collection):
#     """
#     Tests that account values are updated in the database after a new account/subscription is created for a
#     MLS_SUBSCRIBED_ANNUALLY account
#     """
#     old_value = get_account_collection[AccountTypes.MLS_SUBSCRIBED_ANNUALLY]
#     assert_that(update_account_with_new_subscription_MLS_SUBSCRIBED_ANNUALLY).is_true()
#     new_value = get_account_collection[AccountTypes.MLS_SUBSCRIBED_ANNUALLY]
#     assert_that(old_value).is_equal_to(new_value)
#
#
# def test_update_account_to_db_MLS_SUBSCRIBED(update_account_with_new_subscription_MLS_SUBSCRIBED,
#                                              get_account_collection):
#     """
#     Tests that account values are updated in the database after a new account/subscription is created for a
#     MLS_SUBSCRIBED account
#     """
#     old_value = get_account_collection[AccountTypes.MLS_SUBSCRIBED]
#     assert_that(update_account_with_new_subscription_MLS_SUBSCRIBED).is_true()
#     new_value = get_account_collection[AccountTypes.MLS_SUBSCRIBED]
#     assert_that(old_value).is_equal_to(new_value)
#
#
# def test_account_db_data_pull(get_account_collection):
#     assert_that(get_account_collection[AccountTypes.UP_NEXT_TESTS].dsid == "995000000653926845")
