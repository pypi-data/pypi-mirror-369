import logging
import os
import subprocess
import tempfile
from pathlib import Path

import psycopg2
from data_structures.test_data_keys import AccountTypes
from database_control.security_manager import get_secrets
from psycopg2 import sql, OperationalError
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

'''
Class manages all Database Access including connection and CRUD operations'''

'''
IMPORTANT!!!! - Adding Dictionaries to the Database needs a wrap around the dictionary = psycopg2.extras.Json()
'''


class DatabaseManager:

    def __init__(self, env="dev"):
        self.connection = None
        self.DB_SECRETS_DIRECTORY = str(Path.home()) + '/.green-room'
        self.database_env = env
        self.secrets = {}

    def connect_to_database(self):
        if self.connection is not None and not self.connection.closed:
            logger.info("[screentest] - Database connection already active.")
            return
        self.secrets = get_secrets(self.DB_SECRETS_DIRECTORY, False, True, "green-room")
        try:
            if self.database_env == "dev":
                # Load in Whisper protected secrets -> Currently using Read-Write Access in Dev
                logger.info("[screentest] - Accessing dev database")
                self.secrets = self.secrets['screentest_DEV_RW_access']['screentest']

            else:
                logger.info("[screentest] - Accessing prod database")
                self.secrets = self.secrets['screentest_PROD_RW_access']['screentest']
            self.connection = psycopg2.connect(
                database=self.secrets['DB_NAME'],
                user=self.secrets['DB_USER'],
                password=self.secrets['DB_PASSWORD'],
                host=self.secrets['DB_HOST'],
                port=int(self.secrets['DB_PORT']),
                options=self.secrets['DB_OPTIONS'],
                sslmode=self.secrets['DB_SSLMODE']
            )

            logger.info("[screentest] - Database connected successfully")
        except OperationalError as e:
            logger.error(f"[screentest] - Failed to connect to database: {e}")
            self.connection = None  # Reset connection to None on failure
            raise
        except Exception as e:
            logger.error(f"[screentest] - An unexpected error occurred during database connection: {e}")
            self.connection = None
            raise

    # Check if connection is established with Database
    def get_connection(self):
        return self.connection

    # Close Database connection at end of session
    def close_connection(self):
        if self.connection:
            self.connection.close()

    '''
    Delete account from database
    Params - table_name currently always "Accounts" since that's the only table in use
    - account_type - type of account to delete from database
    '''

    def delete_account(self, table_name: str, account_type: AccountTypes) -> None:
        if not self.connection:
            logger.error("Database not connected. Call connect_to_database() first.")
            return
        try:
            account_type = str(account_type).replace("AccountTypes.", "")
            with self.connection.cursor(cursor_factory=RealDictCursor) as cur:
                query = sql.SQL("""DELETE
                                   FROM {schema}.{table}
                                   WHERE account_type = %s;""").format(schema=sql.Identifier("screentest"),
                                                                       table=sql.Identifier(table_name))
                cur.execute(query, (account_type,))
                if cur.rowcount == 0:
                    logger.info("No row found with id {} in table {}".format(account_type, table_name))
                    self.connection.rollback()
                else:
                    self.connection.commit()
        except psycopg2.Error as e:
            logger.error("Error while deleting row/account", e)
            self.connection.rollback()

    def get_db_connection_params(self, db_env: str) -> dict:
        """Helper to get connection parameters for a specific environment."""
        all_secrets = get_secrets(self.DB_SECRETS_DIRECTORY, False, True, "green-room")
        if db_env == "dev":
            return all_secrets['screentest_DEV_RW_access']['screentest']
        elif db_env == "prod":
            return all_secrets['screentest_PROD_RW_access']['screentest']
        else:
            raise ValueError(f"Unknown environment: {db_env}. Must be 'dev' or 'prod'.")

    def check_pg_tools_available(self):
        """Checks if pg_dump and psql/pg_restore are available in the system's PATH. Needed to perform a SQL dump locally"""
        try:
            subprocess.run(["pg_dump", "--version"], check=True, capture_output=True)
            subprocess.run(["pg_restore", "--version"], check=True,
                           capture_output=True)  # Use pg_restore for custom format
            return True
        except FileNotFoundError:
            logger.error(
                "pg_dump or pg_restore not found. Please ensure PostgreSQL client tools are installed and in your system's PATH.")
            return False
        except subprocess.CalledProcessError as e:
            logger.error(f"Error checking pg_dump/pg_restore versions: {e.stderr.decode().strip()}")
            return False

    def dump_and_restore_database(self, source_env: str, target_env: str, dump_schema_only: bool = False,
                                  drop_existing_data: bool = True) -> bool:
        """
        Dumps the database from source_env and restores it to target_env.

        This method uses CLI interaction to ensure intentional overwrite of prod db.

        Args:
            source_env (str): The environment to dump from ('dev' or 'prod').
            target_env (str): The environment to restore to ('dev' or 'prod').
            dump_schema_only (bool): If True, only dump the schema (no data).
            drop_existing_data (bool): If True, drop existing objects in target before restoring.
             **USE WITH EXTREME CAUTION ON PROD! - This deletes the Prod DB and overwrites with DEV db**

        Returns:
            bool: True if successful, False otherwise.
        """

        #check pg dump/restore tools exist on user's system
        if not self.check_pg_tools_available():
            return False

        if source_env == target_env:
            logger.error(f"Source and target environments cannot be the same ({source_env}).")
            return False

        # --- SAFETY PROMPT ---
        if target_env == "prod":
            logger.warning("!!! WARNING: You are attempting to restore to the PRODUCTION database. !!!")
            logger.warning("!!! This operation will OVERWRITE or DELETE existing data. !!!")
            confirm = input("Type 'YES' to confirm this destructive operation: ")
            if confirm.upper() != 'YES':
                logger.info("Operation cancelled by user.")
                return False

        logger.info(f"Begin attempting to dump database from '{source_env}' and restore to '{target_env}'...")

        try:
            source_params = self.get_db_connection_params(source_env)
            target_params = self.get_db_connection_params(target_env)
        except Exception as e:
            logger.error(f"Missing secrets for environment. Check your '~/.green-room' configuration. Error: {e}")
            return False

        # Can dump only structure or all data
        dump_options = []
        if dump_schema_only:
            dump_options.append("-schema-only")  # Schema only
        else:
            dump_options.append("-Fc")  # Custom format for pg_restore (more flexible)

        # Environment variables for pg_dump
        pg_dump_env = os.environ.copy()
        pg_dump_env['PGHOST'] = source_params['DB_HOST']
        pg_dump_env['PGPORT'] = str(source_params['DB_PORT'])
        pg_dump_env['PGUSER'] = source_params['DB_USER']
        pg_dump_env['PGPASSWORD'] = source_params['DB_PASSWORD']

        # Environment variables for pg_restore
        psql_env = os.environ.copy()
        psql_env['PGHOST'] = target_params['DB_HOST']
        psql_env['PGPORT'] = str(target_params['DB_PORT'])
        psql_env['PGUSER'] = target_params['DB_USER']
        psql_env['PGPASSWORD'] = target_params['DB_PASSWORD']

        # Use a temporary file for the dump
        with tempfile.NamedTemporaryFile(delete=True, suffix=".dump") as temp_dump_file:
            dump_file_path = temp_dump_file.name
            logger.info(f"Temporary dump file created at: {dump_file_path}")

            # pg_dump
            pg_dump_cmd = [
                "pg_dump",
                "-d", source_params['DB_NAME'],
                *dump_options,
                "-f", dump_file_path,
                "-x",  # No sending privileges
                "-O",  # No sending ownership rules
                "--exclude-extension=pgcrypto", # unnecessary to redump
                "--exclude-extension=pgaudit" # unnecessary to redump
            ]

            logger.info(f"Executing pg_dump: {' '.join(pg_dump_cmd)}")
            try:
                subprocess.run(pg_dump_cmd, env=pg_dump_env, check=True, capture_output=True)
                logger.info(f"Database '{source_params['DB_NAME']}' dumped successfully to '{dump_file_path}'.")
            except subprocess.CalledProcessError as e:
                logger.error(f"pg_dump failed: {e.stderr.decode().strip()}")
                return False
            except FileNotFoundError:
                logger.error(
                    "pg_dump command not found. Ensure PostgreSQL client tools are installed and in your PATH.")
                return False
            except Exception as e:
                logger.error(f"An unexpected error occurred during pg_dump: {e}")
                return False

            # pg_restore
            pg_restore_cmd = [
                "pg_restore",
                "-d", target_params['DB_NAME'],
                "-v",  # print verbose output about results
                "--clean" if drop_existing_data else "",
                "--if-exists" if drop_existing_data else "",
                "-x",  # No sending privileges
                "-O",  # No sending ownership
                dump_file_path
            ]
            pg_restore_cmd = [cmd for cmd in pg_restore_cmd if cmd]  # Remove empty strings

            logger.info(f"Executing pg_restore: {' '.join(pg_restore_cmd)}")
            try:
                subprocess.run(pg_restore_cmd, env=psql_env, check=True, capture_output=True)
                logger.info(f"Database restored successfully from '{dump_file_path}' to '{target_params['DB_NAME']}'.")
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"pg_restore failed: {e.stderr.decode().strip()}")
                return False
            except FileNotFoundError:
                logger.error(
                    "pg_restore command not found. Ensure PostgreSQL client tools are installed and in your PATH.")
                return False
            except Exception as e:
                logger.error(f"An unexpected error occurred during pg_restore: {e}")
                return False