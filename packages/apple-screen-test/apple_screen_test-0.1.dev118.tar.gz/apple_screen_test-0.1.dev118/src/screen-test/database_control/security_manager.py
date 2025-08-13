import json
import os
import subprocess
from pathlib import Path

SECRETS_DIRECTORY = str(Path.home()) + "/.green-room"


def parse_whisper_secrets(directory):
    secrets = {}
    # Iterate over all files in the specified directory
    for filename in os.listdir(directory):
        if filename.startswith('.'):
            continue
        file_path = os.path.join(directory, filename)

        # Check if it is a file
        if os.path.isfile(file_path):
            # Read file contents
            with open(file_path, 'r') as file:
                file_contents = file.read()

            # Set the environment variable with the filename as the key and file contents as the value
            env_var_name = filename.replace('.', '_').upper()  # Avoid invalid env var characters like '.'
            os.environ[env_var_name] = file_contents
            secrets[filename.replace('.', '_')] = json.loads(file_contents)

    return secrets


def get_secrets(secret_dir=None, store_secrets=False, update_stored_secrets=False, namespace="cup-cake-secrets"):
    if not secret_dir:
        secret_dir = SECRETS_DIRECTORY

    if os.path.isdir(secret_dir) and not update_stored_secrets:
        print('Reading secrets from', secret_dir)
    elif 'RIO_NARRATIVE_CHAIN_PATH' in os.environ:
        print('Calling Whisper with Rio certificates')
        subprocess.run(["whisperctl", "secret", "fetch",
                        "--output-dir", secret_dir,
                        "--namespace", namespace,
                        "--client-certificate-format", "PEM",
                        "--client-certificate", os.environ["RIO_NARRATIVE_CHAIN_PATH"],
                        "--client-key", os.environ["RIO_NARRATIVE_PRIVATE_KEY_PATH"]
                        ])
    else:
        print('Calling Whisper with Memento auth')
        subprocess.run(["whisperctl", "secret", "fetch",
                        "--output-dir", secret_dir, "--namespace", namespace,
                        ])

    secrets = parse_whisper_secrets(secret_dir)
    if not store_secrets and not update_stored_secrets:
        subprocess.run(["rm", "-rf", secret_dir])
    return secrets
