# Changelog

## v0.4.0

- **Garmin auth vendored**: Replaced the `garminconnect` dependency with a vendored `garmin_client` package (from [garminspo2](https://github.com/yeled/garminspo2)). Uses a five-strategy SSO fallback chain with `curl_cffi` TLS fingerprinting and DI OAuth2 tokens with rotating-refresh persistence, fixing sessions expiring every ~2 days. Tokens are still stored in the keyring; a one-time re-login is required to migrate from the old token format.

## v0.3.0

- **Garmin auth rewritten**: Migrated to garminconnect>=0.3.0 due to Garmin SSO/OAuth changes; replaces garth-based authentication. Re-login required.

## v0.2.0

### Installation & Setup

- **Simpler installation**: Install directly from GitHub with `pip install "git+https://github.com/..."`
- **Optional Bluetooth**: Bluetooth support is now optional—install only if needed
- **Better setup wizard**: `omramin init` now only saves config after successful completion

### Configuration

- **Platform-native config locations**:
  - Linux: `~/.config/omramin/config.json`
  - macOS: `~/Library/Application Support/omramin/config.json`
  - Windows: `%APPDATA%\omramin\config.json`
- **Secure token storage**: Tokens now stored in system keyring (macOS Keychain, Linux SecretService) for better security

### Synchronization

- **Flexible date ranges**: Use `--from` and `--to` for specific date ranges
- **Filter by category**: Sync only blood pressure monitors or scales with `--category`
- **Regional API support**: Automatic handling of different OMRON API versions worldwide

### Authentication

- **Dedicated login/logout commands**: Separate `garmin login/logout` and `omron login/logout` commands
- **Better credential management**: Improved token handling and refresh

### Device Management

- **List OMRON devices**: New `omramin omron list` command shows all devices in your account
- **Easier device discovery**: Multiple discovery methods (API, Bluetooth, manual MAC entry)
