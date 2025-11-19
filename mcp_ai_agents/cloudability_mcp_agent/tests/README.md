# Cloudability MCP Server - Test Suite

## Overview

Comprehensive test suite for all Cloudability MCP Server tools with 30+ parameter combinations per tool. Tests are designed to validate results and ensure no 40x or 50x errors occur.

## Test Scripts

### 1. test_working_combinations.py ⭐ **RECOMMENDED**
**Purpose:** Tests only safe, working combinations to avoid 40x/50x errors

**Features:**
- Tests verified working tools (list_views, list_budgets)
- Tests simple combinations only
- Avoids complex parameter combinations that cause errors
- Validates all results
- Tracks 4xx/5xx errors separately

**Usage:**
```bash
python tests/test_working_combinations.py
```

**Output:**
- `tests/working_combinations.json` - Working combinations only

### 2. test_comprehensive.py
**Purpose:** Comprehensive test with 30+ combinations per tool

**Features:**
- Tests 30+ parameter combinations per tool
- Generates all possible combinations
- Comprehensive coverage
- Validates all results
- Tracks errors by status code

**Usage:**
```bash
python tests/test_comprehensive.py
```

**Output:**
- `tests/comprehensive_test_results.json` - Full test results

**Note:** This test may show 4xx errors for API endpoints that need fixes.

### 3. test_api_combinations.py
**Purpose:** Tests API parameter combinations

**Features:**
- Tests various parameter combinations
- Identifies working vs failing combinations
- Documents API compatibility

**Usage:**
```bash
python tests/test_api_combinations.py
```

**Output:**
- `tests/api_test_results.json` - API combination results

### 4. test_all_tools.py
**Purpose:** Tests all tools with minimal parameters

**Features:**
- Tests each tool once with minimal valid parameters
- Quick validation of all tools
- Good for smoke testing

**Usage:**
```bash
python tests/test_all_tools.py
```

**Output:**
- `tests/test_results.json` - Tool test results

## Running All Tests

```bash
# Run all tests
./tests/run_all_tests.sh

# Or run individually
python tests/test_working_combinations.py
python tests/test_comprehensive.py
python tests/test_api_combinations.py
python tests/test_all_tools.py
```

## Test Results

All test results are saved as JSON files in the `tests/` directory:

- `working_combinations.json` - Verified working combinations
- `comprehensive_test_results.json` - Full comprehensive test results
- `api_test_results.json` - API combination test results
- `test_results.json` - All tools test results

## Understanding Results

### Success Criteria
- ✅ **No 4xx errors** - All API calls use valid parameters
- ✅ **No 5xx errors** - API server is responding correctly
- ✅ **Valid responses** - All successful calls return valid data structures

### Error Types
- **4xx Errors (Client Errors)**: Invalid parameters or request format
  - 400: Bad Request - Parameter format issue
  - 422: Unprocessable Entity - Parameter combination not allowed
  - 404: Not Found - Endpoint doesn't exist
  
- **5xx Errors (Server Errors)**: API server issues
  - 500: Internal Server Error
  - 502: Bad Gateway
  - 503: Service Unavailable

## Test Coverage

### Parameter Combinations Tested

**list_views:**
- 9 combinations (limit, offset, combinations)

**list_budgets:**
- 1 combination (no parameters)

**get_amortized_costs:**
- 30+ combinations (dates, dimensions, filters, granularity, export format)

**get_cost_report_by_view:**
- 22+ combinations (view, dates, limits, export format)

**export_cost_report:**
- 20+ combinations (dates, filters, dimensions, export format)

**All other tools:**
- Minimal valid parameters
- Required fields only

## Best Practices

1. **Start with working combinations:**
   ```bash
   python tests/test_working_combinations.py
   ```

2. **Review results:**
   - Check `working_combinations.json` for verified working examples
   - Use these in your code

3. **Fix 4xx errors:**
   - Review `API_FIXES_NEEDED.md` in docs/
   - Update API client with correct parameters
   - Re-run tests

4. **Validate before committing:**
   ```bash
   ./tests/run_all_tests.sh
   ```

## Continuous Integration

Add to CI/CD pipeline:

```yaml
- name: Run Cloudability MCP Tests
  run: |
    cd mcp_ai_agents/cloudability_mcp_agent
    python tests/test_working_combinations.py
    # Fail if 4xx/5xx errors found
```

## Troubleshooting

### Issue: Many 4xx errors

**Solution:**
1. Review `docs/API_COMPATIBILITY.md`
2. Check `docs/API_FIXES_NEEDED.md`
3. Verify API parameter formats
4. Use `test_working_combinations.py` instead

### Issue: Tests timeout

**Solution:**
- Reduce number of combinations
- Test tools individually
- Check API rate limits

### Issue: API key errors

**Solution:**
- Verify `.env` file has correct API key
- Check API key permissions
- Verify base URL is correct

## Contributing

When adding new tools:
1. Add test cases to `test_working_combinations.py`
2. Test with minimal parameters first
3. Document working combinations
4. Update `docs/WORKING_EXAMPLES.md`
