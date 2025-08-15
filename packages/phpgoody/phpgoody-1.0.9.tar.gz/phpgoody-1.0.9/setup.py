from setuptools import setup, find_packages
import re
import os

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

package_name = 'phpgoody'

def get_new_version():
    """
    Determines the new version number for the package.

    If the PHPGODDY_VERSION environment variable is set, that version is used.
    Otherwise, it increments the latest version found in the 'dist' directory.
    If 'dist' directory does not exist or is empty, it defaults to '1.0.0'.
    """
    # Use version from environment variable if available
    env_version = os.environ.get('PHPGODDY_VERSION')
    if env_version:
        return env_version

    # Default version if dist directory doesn't exist or is empty
    if not os.path.exists('./dist') or not os.listdir('./dist'):
        return '1.0.0'

    dists = os.listdir('./dist')
    latest_dist = sorted(dists)[-1]

    # Extract version from filename
    match = re.search(r'^phpgoody-(\d+\.\d+\.\d+)', latest_dist)
    if not match:
        raise ValueError("Could not find version number in distribution file names.")

    latest_dist_version = match.groups()[0]

    # Increment the patch version number
    version_parts = latest_dist_version.split('.')
    version_parts[2] = str(int(version_parts[2]) + 1)

    return '.'.join(version_parts)

new_version = get_new_version()

setup(
    name=package_name,
    version=new_version,
    description="Some useful php functions implemented by python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Elevioux",
    author_email="elevioux@live.com",
    url="https://blog.gwlin.com",
    install_requires=["dateutils>=0.6"],
    license="MIT License",
    packages=find_packages(),
    platforms=["all"],
    python_requires=">=3.11",
)
