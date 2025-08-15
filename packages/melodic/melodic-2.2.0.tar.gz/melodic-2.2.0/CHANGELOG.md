# Changelog

All notable changes to **melodic** will be documented in this file.

## v2.2.0 (2025-08-15)

### Added

- implement full fetching logic & update public api
- add core networking logic
- minimize http status magic numbers
- add client config model dataclass for cleaner setup
- refactor public api import format
- add artist and song parsing methods
- improve exceptions, song models and public api

### Changed

- optimize the storing of song data
- improve initialization schema
- improve base interface implementations
- reduce default headers to user agent

## v2.1.0 (2025-08-08)

### Added

- add SQLiteStorage implementation
- add schema for initialize database tables
- add abstract interface for storage implementations
- add SQLiteStorage public api
- add custom exceptions for storage operations
- implement storage handling in main client
- add storage public apis

## v2.0.0 (2025-08-08)

### Added

- add project constants
- add main client with async enter/exit & workflow stub
- add project init with public api section
- add music model representations
- add custom project exceptions

### Build

- add project metadata
- add project github workflows

### Chores

- add project general information
- add gitignore