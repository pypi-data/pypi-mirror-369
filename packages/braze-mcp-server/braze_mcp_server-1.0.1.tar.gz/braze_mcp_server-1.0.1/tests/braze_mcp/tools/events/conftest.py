import pytest


@pytest.fixture
def sample_events_list_data():
    return {
        "message": "success",
        "events": ["Event A", "Event B", "Event C"],
    }


@pytest.fixture
def sample_events_data_series_data():
    return {
        "message": "success",
        "data": [
            {"time": "2024-01-01", "count": 100},
            {"time": "2024-01-02", "count": 150},
            {"time": "2024-01-03", "count": 120},
        ],
    }


@pytest.fixture
def sample_events_data():
    return {
        "message": "success",
        "events": [
            {
                "name": "Test Event 1",
                "description": "Description for test event 1",
                "included_in_analytics_report": True,
                "status": "Active",
                "tag_names": ["Tag One", "Tag Two"],
            },
            {
                "name": "Test Event 2",
                "description": "Description for test event 2",
                "included_in_analytics_report": False,
                "status": "Inactive",
                "tag_names": ["Tag Three"],
            },
        ],
    }
