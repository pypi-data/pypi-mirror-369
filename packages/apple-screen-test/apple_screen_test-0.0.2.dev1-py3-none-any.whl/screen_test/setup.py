from __future__ import annotations
from setuptools import setup


def version_func():
    from setuptools_scm.version import only_version

    #Adds dev versioning to new packages - not currently using for screen-test,
    # but optional to add back in under 'version_scheme': my_release_branch_semver_version
    def my_release_branch_semver_version(version):
        version.distance = int(version.distance/2)
        return version.format_next_version(only_version, fmt="{guessed}.{distance}")

    return {
        'version_scheme': 'post-release',
        'local_scheme': 'no-local-version',
    }

setup(use_scm_version=version_func)
