# Real API Validation Tests

Tests that validate MCP tools against **real Braze API endpoints**. Organized by tool category, disabled by default.

## Requirements

These tests require real entities (campaigns, canvases, segments, custom attributes, etc.) to exist in the Braze workspace associated with your API key. Tests will fail or return empty results if the workspace doesn't contain the relevant data for each tool category.

## Usage

```bash
# Regular tests (real API tests skipped)
make test

# Run all real API tests
BRAZE_REAL_API_TEST=1 \
BRAZE_API_KEY=your_api_key \
BRAZE_BASE_URL=https://elsa.braze.com \
uv run pytest tests/validation/ -m real_api -v

# Run specific tool category
BRAZE_REAL_API_TEST=1 \
BRAZE_API_KEY=your_api_key \
BRAZE_BASE_URL=https://elsa.braze.com \
uv run pytest tests/validation/test_campaigns.py -v
```