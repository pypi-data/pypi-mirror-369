"""Version information for this package."""

### IMPORTS
### ============================================================================
## Standard Library
import datetime  # pylint: disable=unused-import

## Installed

## Application

### CONSTANTS
### ============================================================================
## Version Information - DO NOT EDIT
## -----------------------------------------------------------------------------
# These variables will be set during the build process. Do not attempt to edit.
PACKAGE_VERSION = "3.0.1"
BUILD_VERSION = "3.0.1"
BUILD_GIT_HASH = "aaf649522573c468fa354a0f34c693db6c0cface"
BUILD_GIT_HASH_SHORT = "aaf6495"
BUILD_GIT_BRANCH = "main"
BUILD_TIMESTAMP = 1755251856
BUILD_DATETIME = datetime.datetime.utcfromtimestamp(1755251856)

## Version Information Strings
## -----------------------------------------------------------------------------
VERSION_INFO_SHORT = f"{BUILD_VERSION}"
VERSION_INFO = f"{PACKAGE_VERSION} ({BUILD_VERSION})"
VERSION_INFO_LONG = (
    f"{PACKAGE_VERSION} ({BUILD_VERSION}) ({BUILD_GIT_BRANCH}@{BUILD_GIT_HASH_SHORT})"
)
VERSION_INFO_FULL = (
    f"{PACKAGE_VERSION} ({BUILD_VERSION})\n"
    f"{BUILD_GIT_BRANCH}@{BUILD_GIT_HASH}\n"
    f"Built: {BUILD_DATETIME}"
)
