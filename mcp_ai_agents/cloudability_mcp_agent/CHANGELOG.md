# Changelog - Cloudability MCP Server

## [3.1.0] - 2025-11-19

### Major API Fixes
- **Fixed API Parameter Names**: Changed from `start`/`end` to `start_date`/`end_date` to match Cloudability API v3 documentation
- **Fixed Filter Parameter**: Changed from `filter` (singular) to `filters` (plural) as per API specification
- **Enhanced Filter Support**: Added support for:
  - Wildcards: `namespace=@ici` (for patterns like `ici*`)
  - IN operator: `region[]==us-east-1,us-west-2`
  - Comparison operators: `cost>100`, `cost<=500`
  - Contains operator: `region=@us-east-`
- **Fixed Filters with Views**: Views and filters can now be combined (previously filters were removed when view was specified)
- **Fixed Date Parameters with Views**: Views have their own date ranges - date parameters are now omitted when a view is specified
- **Updated Metric Names**: Changed to `total_amortized_cost` and `total_cost` as per API documentation
- **Improved Default Dimensions**: Changed default from `service` to `vendor` (more universal)

### Enhanced Error Handling
- Automatic fallback to alternative parameter formats on 422 errors
- Special handling for views (no date parameters)
- Better error messages and logging
- Retry logic with multiple fallback strategies

### Documentation
- Created `API_FIXES_SUMMARY.md` with comprehensive migration guide
- Added `Makefile` for easy test execution
- Updated `README.md` with Makefile usage and recent changes
- Removed 15+ redundant documentation files
- Consolidated documentation in `docs/` folder

### Testing
- Created `Makefile` with test targets:
  - `make test` - Run all tests
  - `make test-working` - Working combinations
  - `make test-comprehensive` - Comprehensive tests
  - `make test-api` - API combination tests
  - `make test-quick` - Quick smoke tests

### Files Changed
- `src/api_client.py` - Major API parameter fixes
- `src/api_client_extended.py` - Updated container cost functions
- `src/utils.py` - Enhanced filter string building
- `src/api_validator.py` - Updated view parameter validation
- `README.md` - Updated with Makefile and API fixes
- `Makefile` - New file for test automation

### Files Removed (Redundant Documentation)
- `docs/API_FIXES_NEEDED.md`
- `docs/FIXES_COMPLETE.md`
- `docs/TOOL_ENABLEMENT_PLAN.md`
- `docs/TOOLS_UNBLOCKED.md`
- `docs/REFACTORING_COMPLETE.md`
- `docs/REFACTORING_SUMMARY.md`
- `docs/DEPLOYMENT.md`
- `docs/DEPLOYMENT_COMPLETE.md`
- `docs/EXTENSION_SUMMARY.md`
- `docs/USAGE_EXAMPLES.md`
- `docs/WORKING_EXAMPLES.md`
- `docs/README_EXTENDED.md`
- `docs/API_STATUS.md`
- `docs/API_ENDPOINTS.md`
- `docs/API_COMPATIBILITY.md`
- `COMPREHENSIVE_USAGE_EXAMPLES.md` (moved to docs/)

### Breaking Changes
- **Date Parameters**: When using views, date parameters are automatically omitted (views have their own date ranges)
- **Filter Parameter**: Changed from `filter` to `filters` in API calls
- **Default Dimension**: Changed from `service` to `vendor`

### Migration Guide
See [API_FIXES_SUMMARY.md](API_FIXES_SUMMARY.md) for detailed migration instructions.

## [3.0.0] - Previous Release
- Initial framework-based implementation
- 19+ tools implemented
- Comprehensive test suite
- Framework architecture

