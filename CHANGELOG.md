# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
