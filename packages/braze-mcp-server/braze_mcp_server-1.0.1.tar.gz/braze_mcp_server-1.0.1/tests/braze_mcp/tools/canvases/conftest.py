import pytest


@pytest.fixture
def sample_canvas_data():
    return {
        "canvases": [
            {
                "id": "canvas_id_1",
                "name": "Test Canvas 1",
                "last_edited": "2025-01-01T12:00:00Z",
                "tags": [],
            },
            {
                "id": "canvas_id_2",
                "name": "Test Canvas 2",
                "last_edited": "2025-01-02T12:00:00Z",
                "tags": ["tag1", "tag2"],
            },
        ],
        "message": "success",
    }


@pytest.fixture
def sample_canvas_details_data():
    return {
        "message": "success",
        "created_at": "2023-01-01T12:00:00Z",
        "updated_at": "2023-01-10T12:00:00Z",
        "name": "Test Canvas Details",
        "description": "A test canvas for unit testing",
        "archived": False,
        "draft": False,
        "enabled": True,
        "has_post_launch_draft": True,
        "schedule_type": "date",
        "first_entry": "2023-01-01T12:00:00Z",
        "last_entry": "2023-01-10T12:00:00Z",
        "channels": ["email", "push"],
        "variants": [
            {
                "name": "Variant 1",
                "id": "variant_1_id",
                "first_step_ids": ["step_1"],
            }
        ],
        "tags": ["test", "unit-testing"],
        "teams": ["Engineering Team"],
        "steps": [
            {
                "name": "Welcome Email",
                "type": "email",
                "id": "step_1",
                "next_step_ids": [],
                "next_paths": [],
                "channels": ["email"],
                "messages": {
                    "message_1": {
                        "channel": "email",
                        "subject": "Welcome!",
                        "body": "<html><body>Welcome!</body></html>",
                    }
                },
            }
        ],
    }


@pytest.fixture
def sample_canvas_data_summary():
    return {
        "message": "success",
        "data": {
            "name": "Test Canvas",
            "total_stats": {
                "revenue": 1234.56,
                "conversions": 42,
                "conversions_by_entry_time": 38,
                "entries": 150,
            },
            "variant_stats": {
                "variant_1_id": {
                    "name": "Variant 1",
                    "revenue": 823.45,
                    "conversions": 28,
                    "entries": 100,
                }
            },
            "step_stats": {
                "step_1_id": {
                    "name": "Welcome Email",
                    "revenue": 500.25,
                    "conversions": 15,
                    "conversions_by_entry_time": 12,
                    "messages": {
                        "email": [
                            {
                                "sent": 100,
                                "opens": 75,
                                "influenced_opens": 60,
                                "bounces": 5,
                            }
                        ],
                        "android_push": [
                            {
                                "sent": 50,
                                "opens": 30,
                                "influenced_opens": 25,
                                "bounces": 2,
                            }
                        ],
                    },
                }
            },
        },
    }


@pytest.fixture
def sample_canvas_data_series():
    """Sample Canvas data series API response"""
    return {
        "message": "success",
        "data": {
            "name": "Test Canvas Data Series",
            "stats": [
                {
                    "time": "2023-01-01",
                    "total_stats": {},
                    "variant_stats": {
                        "variant-1-id": {
                            "name": "Control",
                            "revenue": 600.30,
                            "conversions": 15,
                            "conversions_by_entry_time": 13,
                            "entries": 60,
                        },
                        "variant-2-id": {
                            "name": "Treatment",
                            "revenue": 400.20,
                            "conversions": 10,
                            "conversions_by_entry_time": 9,
                            "entries": 40,
                        },
                    },
                    "step_stats": {
                        "step-1-id": {
                            "name": "Welcome Email",
                            "revenue": 500.25,
                            "conversions": 12,
                        },
                    },
                }
            ],
        },
    }
