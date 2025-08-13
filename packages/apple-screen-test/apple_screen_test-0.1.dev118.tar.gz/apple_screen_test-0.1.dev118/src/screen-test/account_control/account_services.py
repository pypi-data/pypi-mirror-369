import os
import random
import time

from ampplato.helper import get_random_string
from data_structures.test_data_classes import Account, encrypt_password

from cakepy.utils.http_clients.plato_client import PlatoClient
from cakepy.utils.report_utils.logger import logger


# Access Key to connect for account creation/subscription purchase
def plato_client(charles_session, env_from_pytest_config):
    """
    JUBEO_KEY expires August 9th 2025
    Go here to generate a new key: https://jubeo.apple.com/ui/keys/generate
    """
    return PlatoClient('itms11', jubeo_key=os.getenv("JUBEO_KEY", "6cd499c0-0643-4958-b9a0-0fbb1ed1eb0a"))


def client_account_from_plato(plato_client, account_name='ase-uts-api'):
    """
    This helper should NOT be called at a test level unless all of uts-api-qa team agrees to use it.
    """
    user_email = f'{account_name}+{get_random_string(6)}@apple.com'
    # password should have at leas one capital letter and at least one number
    password = get_random_string(8).capitalize() + str(random.randint(0, 9))
    for i in range(3):
        time.sleep(i)
        dsid = plato_client.create_account(email=user_email, is_visa=True, country_code='USA', password=password)
        if dsid:
            logger.debug(f"Password: {password}")
            account = Account(
                dsid=dsid,
                cid=plato_client.get_consumer_id_by_dsid(dsid),
                email=user_email,
                encrypted_password=encrypt_password(password)
            )
            return plato_client, account
        else:
            logger.debug("[Plato] Account creation failed, retrying...")
    else:
        logger.error("[Plato] Account not created")
        return plato_client, None


def unsubscribed_client_account(plato_client) -> Account:
    account = client_account_from_plato(plato_client)[1]
    logger.info([f"[Plato] Account created: {account}"])
    return account


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


def add_subscription_to_account(client, account, subscription_name):
    for i in range(3):
        time.sleep(i)
        is_bought = client.buy_tv_plus_add_on_subscription(account.email, subscription_name, account.decrypt_password())
        if is_bought:
            logger.info([f"[Plato] {subscription_name} added: {account.dsid}"])
            return account
    logger.warning(f"[Plato] Failed to add {subscription_name} for: {account}")
    return None


def mls_monthly_client_account(plato_client) -> Account:
    subscription_name = 'mls_monthly'
    client, account = client_account_from_plato(plato_client, subscription_name)
    logger.info([f"[Plato] Account created: {account}"])

    return add_subscription_to_account(client, account, subscription_name)


def mls_annual_client_account(plato_client) -> Account:
    subscription_name = 'mls_annually'
    client, account = client_account_from_plato(plato_client, subscription_name)
    logger.info([f"[Plato] Account created: {account}"])

    return add_subscription_to_account(client, account, subscription_name)


def tv_plus_mls_monthly_client_account(plato_client) -> Account:
    client, account = client_account_from_plato(plato_client)
    logger.info([f"[Plato] Account created: {account}"])

    for i in range(3):
        time.sleep(i)
        is_bought = client.buy_tv_plus(account.email, subscription="paid")
        if is_bought:
            logger.info([f"[Plato] TV+ subscription added: {account}"])
            subscription_name = "mls_monthly"
            return add_subscription_to_account(client, account, subscription_name)

        logger.warning(f"[Plato] Failed to add TV+ Subscription for: {account}")
    return None
