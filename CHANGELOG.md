# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2026-04-10

### Changed
- Rebuilt the SDK from the original cloud-only helper-based client into a provider-based architecture under the `pydreo/` package.
- Introduced a unified top-level `DreoClient` facade backed by explicit `core`, `cloud`, and `local` modules.
- Split cloud functionality into dedicated auth, transport, and provider layers instead of routing everything through `helpers.py`.
- Migrated cloud device operations to the v2 device APIs (`/api/v2/device/list`, `/api/v2/device/state`, and `/api/v2/device/control`) while keeping OAuth login in place.
- Moved Dreo cloud password MD5 handling into the SDK so callers can pass plaintext credentials while preserving compatibility with already-hashed passwords.
- Updated packaging metadata, project documentation, and distribution naming to align with the `pydreo-client` package layout.

### Added
- Added normalized core models for device identity, discovery, state, and command results.
- Added provider routing, provider registry, and connection strategy support for future multi-channel orchestration.
- Added a dedicated cloud compatibility client at `pydreo.cloud.client.DreoClient`.
- Added a `LocalProvider` shell with config, discovery, protocol, and transport extension points for future LAN support.
- Added unit tests covering the unified client facade, cloud provider mapping, token-region handling, and the local provider shell.

### Removed
- Removed the legacy helper-centric implementation in `helpers.py`.
- Removed the old top-level `const.py` and `exceptions.py` modules in favor of the new provider/core exception and transport structure.
- Removed the old single-layer internal design that tightly coupled authentication, device discovery, and control behavior.

## [0.0.7] - 2024-08-22

### 🆕 Added
- **European Region Support**: Added support for European region user login
  - Automatic detection of token suffix (EU/NA) to determine API endpoint
  - Support for token format: `token:EU` (European region) and `token:NA` (North American region)
  - Tokens without suffix default to North American endpoint
- **Smart Region Detection**: Automatically select correct API server based on user token
- **Backward Compatibility**: Maintain full compatibility with existing North American users

### 🔧 Technical Improvements
- Added `parse_token_and_get_endpoint()` method for parsing token region information
- Added `clean_token()` method for removing token suffix during API calls
- Optimized device status query and update token handling logic
- Improved error handling and logging

### 🛡️ Security Enhancements
- Automatically clean token suffix during API calls to prevent sensitive information leakage
- Enhanced token validation and error handling mechanisms

### 📝 Documentation
- Updated API usage documentation
- Added usage examples for region detection functionality

### 🔄 Backward Compatibility
- Fully backward compatible with existing code
- Existing North American users require no code modifications
- Automatic detection and handling of different region token formats

---

## [0.0.6] - Previous Release

### Features
- Initial release with US region support
- Basic authentication and device management
- Device status query and control functionality

### Dependencies
- requests
- tzlocal  
- pycryptodome
