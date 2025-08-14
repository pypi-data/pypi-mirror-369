import json
import logging
import os
import random
import string
import subprocess

from requests import Response


# from ampplato import __version__, app_name


def get_required_env_var(key) -> str:
    try:
        with open(os.getenv(key)) as f:
            value = f.read().strip()
            if not value:
                raise ValueError(f"Environment variable '{key}' is not set or has an empty value")
            return value
    except FileNotFoundError:
        if os.getenv(key) is not None:
            return os.getenv(key).strip()
    except TypeError:
        if os.getenv(key) is not None:
            return os.getenv(key).strip()


class HttpUtil:
    hades_url = 'https://hades.amp.apple.com'
    jubeo_url = 'https://jubeo-api.apple.com'
    jubeo_key = None

    def __init__(self, jubeo_key, hades_key='c847b89f-011c-4019-a0d7-90940b560ccc'):
        try:
            if self.jubeo_key is None and jubeo_key is None:
                try:
                    self.jubeo_key = get_required_env_var('JUBEO_KEY')
                    self.hades_key = hades_key
                except TypeError:
                    self.jubeo_key = jubeo_key
                    self.hades_key = hades_key
            else:
                self.jubeo_key = jubeo_key
                self.hades_key = hades_key
        except ValueError as e:
            logging.warning('JUBEO_KEY environment variable is not set. You can generate a key at '
                            'https://jubeo.apple.com/ui/keys/generate.')
            raise e

        proc = subprocess.Popen('/usr/local/bin/appleconnect s -d -D -I 170932', shell=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE)
        output, err = proc.communicate()
        cookie = output.decode("utf-8")

        logging.info("Processed cookie", cookie)

        self.headers_for_jubeo = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Apple-Jubeo-Key': self.jubeo_key,
            # 'User-Agent': f'{app_name}/{__version__}'
        }

        self.headers_for_hades = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Hades-API-Token': self.hades_key,
            # 'User-Agent': f'{app_name}/{__version__}',
        }

    @staticmethod
    def _is_ok_response(response: Response) -> bool:
        if response.ok is not True:
            logging.info(f'Unexpected response: {response.status_code} {response.text}')
            return False
        return True

    def is_successful_jubeo_response(self, response: Response) -> bool:
        if not self._is_ok_response(response):
            print([response.text])
            return False

        json_response = json.loads(response.text)
        if 'success' not in json_response or not json_response['success']:
            message = []
            if 'advisedAction' in json_response:
                message.append(json_response['advisedAction'])
            else:
                message.append('If you require help please contact us on Slack in #jubeo-support channel')
                message.append('Please attach all relevant information to your message')
            if 'errors' in json_response:
                message.append(f'Errors: {json_response["errors"]}')
            if 'X-Apple-Jubeo-History-Id' in response.headers:
                message.append(f'History Id: {response.headers["X-Apple-Jubeo-History-Id"]}')
            if 'X-Apple-Jubeo-Correlation-Key' in response.headers:
                message.append(f'Jubeo Correlation Key: {response.headers["X-Apple-Jubeo-Correlation-Key"]}')

            logging.warning('\n'.join(message))
            return False
        return True


news_plus_supported_countries = frozenset(['GBR', 'AUS', 'CAN', 'USA'])


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))
