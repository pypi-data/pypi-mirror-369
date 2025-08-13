# ArborXR CLI

This CLI tool provides commands for managing apps and files via the ArborXR API. The tool is organized into command groups: apps and files. Each group has several subcommands to perform specific operations through the command line.

## Prerequisites

Before using the CLI tool, you must perform the following:
* Python 3 installed on your system.
* An API Token for authentication
    * Login to your ArborXR Account
    * Navigate to Settings > Access Tokens
    * Create an API Access Token for your organization
* Setting the API token
    * The environment variable ABXR_API_TOKEN (or the alternative ARBORXR_ACCESS_TOKEN), or
    * The command line option --token.

## Setup

ArborXR CLI is available through PyPI. If you have `pip` installed, you can get the latest version by installing via:
```
pip install abxrcli
```

## Global Options

### The CLI tool accepts the following global options:
`-u, --url`
* Description: API Base URL
* Default: https://api.xrdm.app/api/v2 (or the value of ABXR_API_URL environment variable)

`-t, --token`
* Description: API Token for authentication
* Default: Value of ABXR_API_TOKEN (or ARBORXR_ACCESS_TOKEN)

`-f, --format`
* Description: Data output format
* Choices: json or yaml
* Default: yaml

`-v, --version`
* Description: Show the CLI tool version and exit

`-s, --silent`
* Description: Disable any terminal printing of progress bars for longer operations, like file uploads.

## Command Groups

The CLI tool is divided into two main groups: apps and files. Each group has its own set of subcommands.

### Apps Commands

These commands manage app-related operations.

#### Subcommands

##### list
* Usage:
`abxr-cli apps list`
* Description: List all available apps.


##### details
* Usage:
`abxr-cli apps details <app_id>`
* Positional Argument:
    * <app_id>: The unique identifier of the app.
* Description: Retrieve detailed information about a specific app.


##### versions
* Usage:
`abxr-cli apps versions <app_id>`
* Positional Argument:
    * <app_id>: The unique identifier of the app.
* Description: List all versions available for a specific app.


##### release_channels
* Usage:
`abxr-cli apps release_channels <app_id>`
* Positional Argument:
    * <app_id>: The unique identifier of the app.
* Description: List all release channels associated with a specific app.


##### release_channel_details
* Usage:
`abxr-cli apps release_channel_details <app_id> [--release_channel_id RELEASE_CHANNEL_ID]`
* Positional Argument:
    * <app_id>: The unique identifier of the app.
* Optional Argument:
    * --release_channel_id: The identifier for a specific release channel.
* Description: Get details for a release channel of an app.

##### release_channel_set_version
* Usage:
`abxr-cli apps release_channel_set_version <app_id> [--release_channel_id RELEASE_CHANNEL_ID] [--version_id VERSION_ID]`
* Positional Argument:
    * <app_id>: The unique identifier of the app.
* Optional Arguments:
    * --release_channel_id: The identifier for the release channel.
    * --version_id: The version identifier to set for the channel.
* Description: Assign a specific version to a release channel.

##### upload
* Usage:
`abxr-cli apps upload <app_id> <filename> [--version VERSION] [--notes NOTES]`
* Positional Arguments:
    * <app_id>: The unique identifier of the app.
	* <filename>: Local path of the APK/ZIP (apk+obb) file to upload.
* Optional Arguments:
	* -v, --version: Version number (note that the Uploaded APK itself can override this value).
	* -n, --notes: Release notes for the new version.
* Description: Upload a new version of an app.

##### share
* Usage:
`abxr-cli apps share <app_id> --release_channel_id RELEASE_CHANNEL_ID --organization_slug ORGANIZATION_SLUG`
* Positional Argument:
	* <app_id>: The unique identifier of the app.
* Required Options:
	* --release_channel_id: The release channel to be shared.
	* --organization_slug: The organization slug with which the app is to be shared.
* Description: Share an app with a specific organization and release channel.

##### revoke
* Usage:
`abxr-cli apps revoke <app_id> --release_channel_id RELEASE_CHANNEL_ID --organization_slug ORGANIZATION_SLUG`
* Positional Argument:
	* <app_id>: The unique identifier of the app.
* Required Options:
	* --release_channel_id: The release channel from which to revoke sharing.
	* --organization_slug: The organization slug from which the app sharing should be revoked.
* Description: Revoke sharing of an app from a specific organization and release channel.


### Files Commands

These commands are used for file-related operations.

#### Subcommands

##### list
* Usage:
`abxr-cli files list`
* Description: List all files available.


##### details
* Usage:
`abxr-cli files details <file_id>`
* Positional Argument:
	* <file_id>: The unique identifier of the file.
* Description: Get detailed information for a specific file.

### Devices Commands

These commands are used for device-related operations

#### Subcommands

##### list
* Usage:
`abxr-cli devices list`
* Description: List all devices


##### details
* Usage:
`abxr-cli devices details <device_id>`
* Positional Argument:
    * <device_id>: The unique identifier for the device.
* Description: Get detailed information about a device.


##### launch
* Usage:
`abxr-cli devices launch <device_id> --app_id=<app_id>`
* Positional Argument:
    * <device_id>: The unique identifier for the device.
* Required Options:
    * --app_id: The unique identifier of the application you want to launch
* Description: Launch an application immediately on a device.


##### reboot
* Usage:
`abxr-cli devices reboot <device_id>`
* Positional Argument:
    * <device_id>: The unique identifier for the device.
* Description: Reboot a device immediately.



## CLI Usage Examples

These examples assume you have set the `ABXR_API_TOKEN` in your environment. 

### Listing all apps

`abxr-cli apps list`

### Getting details of a specific app

`abxr-cli apps details 123e4567-e89b-12d3-a456-426614174000`

### Listing versions of an app

`abxr-cli apps versions 123e4567-e89b-12d3-a456-426614174000`

### Uploading a new version of an app

`abxr-cli apps upload 123e4567-e89b-12d3-a456-426614174000 /path/to/app.apk --version 1.2.3 --notes "Bug fixes and performance improvements"`

### Sharing an app with an organization

`abxr-cli apps share 123e4567-e89b-12d3-a456-426614174000 --release_channel_id 6789 --organization_slug myorg`

### Listing all files

`abxr-cli files list`


## Error Handling

* If the API token is missing (not provided via --token or environment variables), the tool will print:

`API Token is required. Please set the ABXR_API_TOKEN environment variable or use the --token command line param`

