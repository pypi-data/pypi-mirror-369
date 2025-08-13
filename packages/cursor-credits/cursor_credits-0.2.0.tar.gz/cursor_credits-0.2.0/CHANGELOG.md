# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-08-13

### Added

-   **Auto-Detection:** Automatic Cursor installation path detection (no config file needed!)
-   **Better Token Handling:** Improved JWT token extraction and session token creation
-   **Enhanced Display:** Better handling of unavailable data with cleaner output
-   **Dependencies:** Added PyJWT for proper token processing
-   **MIT License:** Added proper license file

### Fixed

-   **API Integration:** Corrected API endpoint from cursor.sh to cursor.com
-   **Authentication:** Fixed authentication method from Bearer token to session cookie
-   **Security:** Proper session cookie authentication instead of Bearer tokens

### Changed

-   **Code Cleanup:** Removed outdated email extraction code and reduced verbose logging
-   **Performance:** Streamlined code with 25% fewer lines and better error handling
-   **User Experience:** No configuration file required for standard installations
-   **Output:** Cleaner, less verbose console output
-   **Reliability:** More reliable authentication and data retrieval
-   **Compatibility:** Better cross-platform compatibility

### Removed

-   **Configuration Fallback:** Removed manual configuration file requirement
-   **Email Extraction:** Removed non-functional email extraction attempts
-   **Verbose Logging:** Reduced unnecessary warning and info messages

## [0.1.0] - 2024-08-13

### Added

-   Initial release with basic functionality
-   Manual configuration file setup
-   Basic token extraction and API calls
-   Cross-platform support for Windows, macOS, and Linux
-   Color-coded output with emojis
-   Fast (GPT-4) and Slow (GPT-3.5) request monitoring
