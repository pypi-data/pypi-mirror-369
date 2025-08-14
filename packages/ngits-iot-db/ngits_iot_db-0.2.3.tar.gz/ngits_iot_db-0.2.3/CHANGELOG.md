# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.3] - 2025-08-13

### Added
- Added `receivers` field to `AlertDefinition` model for storing alert notification recipients as JSON
- Database migration `314a5d69646a_add_receivers_to_alert_definition.py` adds the receivers column

## [0.2.2] - 2025-08-05

### Changed
- Removed unique constraint on `alert_definition` table for `tenant` and `meter_id` columns
- Database migration `90c1158cc2ba_delete_alert_uniqueness.py` removes the uniqueness constraint

## [0.2.1] - 2025-08-04

### Fixed
- Fixed missing imports: Added `AlertLevels` and `AlertTypes` to package exports

## [0.2.0] - 2025-08-04

### Added
- Alert system models for IoT monitoring
- `AlertDefinition` model for defining alert rules with JSON properties
- `AlertBase` abstract base class with type, level, and device name fields
- New enum types for alert categorization:
  - `AlertTypes`: threshold_high, threshold_low, sudden_change, offline, data_gap, data_delayed, invalid_reading, stuck_value, noise
  - `AlertLevels`: emergency, critical, warning, info
- Database migration `0d7bea8f4d60_create_alerts_models.py` for alert_definition table

## [0.1.2] - 2025-07-31

### Changed
- **BREAKING**: Restructured package layout from `models.*` to `iot_db.models.*`
- Updated import paths: use `from iot_db.models import WaterMeasurement` instead of `from models import WaterMeasurement`
- Updated Alembic configuration to work with new package structure

### Migration Guide
- Change imports from `from models import *` to `from iot_db.models import *`
- All model classes remain the same, only import paths have changed

## [0.1.1] - 2025-07-31

### Fixed
- Fixed package metadata configuration for PyPI compatibility
- Resolved license file inclusion issues

### Changed
- Updated package name to `ngits-iot-db`
- Improved build configuration

## [0.1.0] - 2025-07-30

### Added
- Initial release of IoT Database Models
- SQLAlchemy models for IoT sensor data:
  - ElectricityMeasurement and usage models
  - WaterMeasurement and usage models  
  - HeatMeasurement and usage models
  - TemperatureMeasurement model
  - RawMeasurement model for unprocessed data
- Alembic migrations support with existing migration history
- Multi-tenant support via tenant UUID field
- Type-safe enums for sensor types (electricity, water, heat, temperature)
- Helper functions for model mapping
- Full type annotations with py.typed marker

### Features
- PostgreSQL backend support
- Automatic timestamping (created_ts, updated_ts)  
- Unique constraints to prevent duplicate measurements
- Daily and monthly usage aggregation models
- Raw sensor data storage with JSON fields
- External system integration support via external_id and meter_id

### Migration History Included
- 78371c256762_init_schema.py - Initial database schema
- fc391d505594_add_temperature.py - Temperature sensor support