import pytest


@pytest.fixture
def sample_campaign_data():
    return {
        "campaigns": [
            {
                "id": "campaign_id_1",
                "name": "Test Campaign 1",
                "is_api_campaign": False,
                "last_edited": "2025-01-01T12:00:00Z",
                "tags": [],
            },
            {
                "id": "campaign_id_2",
                "name": "Test Campaign 2",
                "is_api_campaign": True,
                "last_edited": "2025-01-02T12:00:00Z",
                "tags": [],
            },
        ],
        "message": "success",
    }


@pytest.fixture
def sample_campaign_details_data():
    return {
        "message": "success",
        "name": "Test Campaign Details",
        "description": "Test campaign description",
        "archived": False,
        "draft": False,
        "enabled": True,
        "created_at": "2025-01-01T10:00:00Z",
        "updated_at": "2025-01-01T12:00:00Z",
        "channels": ["email", "push"],
        "conversion_behaviors": [{"type": "Opens App", "window": 86400}],
    }


@pytest.fixture
def sample_campaign_dataseries_response():
    """Sample campaign DataSeries API response"""
    return {
        "message": "success",
        "data": [
            {
                "time": "2024-01-01",
                "conversions_by_send_time": 10,
                "conversions1_by_send_time": 5,
                "conversions2_by_send_time": 3,
                "conversions3_by_send_time": 2,
                "conversions": 15,
                "conversions1": 8,
                "conversions2": 4,
                "conversions3": 3,
                "unique_recipients": 1000,
                "revenue": 1250.50,
                "messages": {
                    "ios_push": [
                        {
                            "variation_api_id": "variation_123",
                            "sent": 500,
                            "direct_opens": 50,
                            "total_opens": 75,
                            "bounces": 5,
                            "body_clicks": 25,
                        }
                    ],
                    "email": [
                        {
                            "variation_api_id": "variation_456",
                            "sent": 500,
                            "opens": 200,
                            "unique_opens": 180,
                            "clicks": 50,
                            "unique_clicks": 45,
                            "unsubscribes": 2,
                            "bounces": 10,
                            "delivered": 490,
                            "reported_spam": 1,
                        }
                    ],
                    "in_app_message": [
                        {
                            "variation_api_id": "variation_789",
                            "impressions": 100,
                            "clicks": 25,
                            "first_button_clicks": 15,
                            "second_button_clicks": 10,
                        }
                    ],
                },
            }
        ],
    }


@pytest.fixture
def sample_multivariate_dataseries_response():
    """Sample multivariate campaign DataSeries API response"""
    return {
        "message": "success",
        "data": [
            {
                "time": "2024-01-01",
                "conversions": 25,
                "revenue": 750.0,
                "conversions_by_send_time": 20,
                "conversions1_by_send_time": 10,
                "conversions2_by_send_time": 5,
                "conversions3_by_send_time": 2,
                "conversions1": 12,
                "conversions2": 6,
                "conversions3": 3,
                "unique_recipients": 1500,
                "messages": {
                    "trigger_in_app_message": [
                        {
                            "variation_name": "Variation A",
                            "impressions": 800,
                            "clicks": 80,
                            "first_button_clicks": 50,
                            "second_button_clicks": 30,
                            "revenue": 300.0,
                            "unique_recipients": 750,
                            "conversions": 15,
                            "conversions_by_send_time": 12,
                            "conversions1": 8,
                            "conversions1_by_send_time": 6,
                            "conversions2": 4,
                            "conversions2_by_send_time": 3,
                            "conversions3": 2,
                            "conversions3_by_send_time": 1,
                        },
                        {
                            "variation_name": "Variation B",
                            "impressions": 700,
                            "clicks": 70,
                            "first_button_clicks": 40,
                            "second_button_clicks": 30,
                            "revenue": 250.0,
                            "unique_recipients": 650,
                            "conversions": 8,
                            "conversions_by_send_time": 6,
                            "conversions1": 4,
                            "conversions1_by_send_time": 3,
                            "conversions2": 2,
                            "conversions2_by_send_time": 1,
                        },
                        {
                            "variation_name": "Control Group",
                            "revenue": 200.0,
                            "unique_recipients": 100,
                            "conversions": 2,
                            "conversions_by_send_time": 2,
                            "conversions1": 0,
                            "conversions1_by_send_time": 0,
                            "conversions2": 0,
                            "conversions2_by_send_time": 0,
                            "conversions3": 0,
                            "conversions3_by_send_time": 0,
                            "enrolled": 100,
                        },
                    ]
                },
            }
        ],
    }


@pytest.fixture
def sample_webhook_dataseries_response():
    """Sample webhook campaign DataSeries API response with real-world webhook structure"""
    return {
        "message": "success",
        "data": [
            {
                "time": "2024-07-20",
                "conversions_by_send_time": 0,
                "conversions1_by_send_time": 0,
                "conversions2_by_send_time": 0,
                "conversions3_by_send_time": 0,
                "conversions": 0,
                "conversions1": 0,
                "conversions2": 0,
                "conversions3": 0,
                "unique_recipients": 0,
                "revenue": 0.0,
                "messages": {
                    "ios_push": None,
                    "android_push": None,
                    "kindle_push": None,
                    "web_push": None,
                    "webhook": [
                        {
                            "variation_name": "Variant 1",
                            "variation_api_id": "7d7983ee-8cb6-456a-9c49-1e4df3c9fcfb",
                            "sent": 0,
                            "errors": 0,
                            "revenue": 0.0,
                            "unique_recipients": 0,
                            "conversions": 0,
                            "conversions_by_send_time": 0,
                            "conversions1": 0,
                            "conversions1_by_send_time": 0,
                            "conversions2": 0,
                            "conversions2_by_send_time": 0,
                            "conversions3": 0,
                            "conversions3_by_send_time": 0,
                            "enrolled": None,
                        },
                        {
                            "variation_name": "Control Group",
                            "variation_api_id": "84fb1e3e-e4df-4c07-825b-a38242c193a0",
                            "sent": None,
                            "errors": None,
                            "revenue": 0.0,
                            "unique_recipients": 0,
                            "conversions": 0,
                            "conversions_by_send_time": 0,
                            "conversions1": 0,
                            "conversions1_by_send_time": 0,
                            "conversions2": 0,
                            "conversions2_by_send_time": 0,
                            "conversions3": 0,
                            "conversions3_by_send_time": 0,
                            "enrolled": 0,
                        },
                    ],
                    "email": None,
                    "sms": None,
                    "whats_app": None,
                    "content_cards": None,
                    "in_app_message": None,
                    "trigger_in_app_message": None,
                },
            }
        ],
    }


@pytest.fixture
def sample_ios_push_extended_response():
    """Sample iOS push DataSeries response with extended fields including variation names and conversions"""
    return {
        "data": [
            {
                "time": "2024-05-31",
                "messages": {
                    "ios_push": [
                        {
                            "variation_name": "Original",
                            "variation_api_id": "695c1670-042d-4335-aa64-d119d64b0f11",
                            "sent": 0,
                            "direct_opens": 0,
                            "total_opens": 0,
                            "bounces": 0,
                            "body_clicks": 0,
                            "revenue": 0.0,
                            "unique_recipients": 0,
                            "conversions": 0,
                            "conversions_by_send_time": 0,
                            "conversions1": 0,
                            "conversions1_by_send_time": 0,
                            "conversions2": 0,
                            "conversions2_by_send_time": 0,
                            "conversions3": 0,
                            "conversions3_by_send_time": 0,
                        },
                        {
                            "variation_name": "Control Group",
                            "variation_api_id": "8374447a-d784-46d7-878a-40ee185f1840",
                            "sent": None,
                            "direct_opens": None,
                            "total_opens": None,
                            "bounces": None,
                            "body_clicks": None,
                            "enrolled": 0,
                            "revenue": 0.0,
                            "unique_recipients": 0,
                            "conversions": 0,
                            "conversions_by_send_time": 0,
                            "conversions1": 0,
                            "conversions1_by_send_time": 0,
                            "conversions2": 0,
                            "conversions2_by_send_time": 0,
                            "conversions3": 0,
                            "conversions3_by_send_time": 0,
                        },
                    ]
                },
                "conversions_by_send_time": 0,
                "conversions1_by_send_time": 0,
                "conversions2_by_send_time": 0,
                "conversions3_by_send_time": 0,
                "conversions": 0,
                "conversions1": 0,
                "conversions2": 0,
                "conversions3": 0,
                "unique_recipients": 0,
                "revenue": 0.0,
            }
        ],
        "message": "success",
    }


@pytest.fixture
def sample_all_channels_dataseries_response():
    """Sample campaign DataSeries API response with all supported channel types"""
    return {
        "message": "success",
        "data": [
            {
                "time": "2024-01-01",
                "unique_recipients": 1000,
                "revenue": 500.0,
                "messages": {
                    "ios_push": [
                        {
                            "variation_api_id": "ios_1",
                            "sent": 100,
                            "direct_opens": 10,
                            "total_opens": 15,
                            "bounces": 1,
                            "body_clicks": 5,
                        }
                    ],
                    "android_push": [
                        {
                            "variation_api_id": "android_1",
                            "sent": 100,
                            "direct_opens": 8,
                            "total_opens": 12,
                            "bounces": 2,
                            "body_clicks": 4,
                        }
                    ],
                    "kindle_push": [
                        {
                            "variation_api_id": "kindle_1",
                            "sent": 50,
                            "direct_opens": 5,
                            "total_opens": 8,
                            "bounces": 1,
                            "body_clicks": 3,
                        }
                    ],
                    "web_push": [
                        {
                            "variation_api_id": "web_1",
                            "sent": 75,
                            "direct_opens": 6,
                            "total_opens": 9,
                            "bounces": 1,
                            "body_clicks": 4,
                        }
                    ],
                    "email": [
                        {
                            "variation_api_id": "email_1",
                            "sent": 200,
                            "opens": 50,
                            "unique_opens": 45,
                            "clicks": 10,
                            "unique_clicks": 8,
                            "unsubscribes": 1,
                            "bounces": 3,
                            "delivered": 195,
                            "reported_spam": 0,
                        }
                    ],
                    "sms": [
                        {
                            "variation_api_id": "sms_1",
                            "sent": 150,
                            "sent_to_carrier": 148,
                            "delivered": 145,
                            "rejected": 2,
                            "delivery_failed": 1,
                            "clicks": 5,
                            "opt_out": 1,
                            "help": 0,
                        }
                    ],
                    "whats_app": [
                        {
                            "variation_api_id": "wa_1",
                            "sent": 80,
                            "delivered": 78,
                            "failed": 2,
                            "read": 70,
                        }
                    ],
                    "content_cards": [
                        {
                            "variation_api_id": "cc_1",
                            "sent": 300,
                            "total_clicks": 20,
                            "total_dismissals": 50,
                            "total_impressions": 250,
                            "unique_clicks": 15,
                            "unique_dismissals": 35,
                            "unique_impressions": 200,
                        }
                    ],
                    "in_app_message": [
                        {
                            "variation_api_id": "iam_1",
                            "impressions": 120,
                            "clicks": 12,
                            "first_button_clicks": 8,
                            "second_button_clicks": 4,
                        }
                    ],
                    "trigger_in_app_message": [
                        {
                            "variation_name": "Promo IAM",
                            "impressions": 100,
                            "clicks": 15,
                            "first_button_clicks": 10,
                            "second_button_clicks": 5,
                            "revenue": 150.0,
                            "unique_recipients": 90,
                            "conversions": 8,
                            "conversions_by_send_time": 7,
                        }
                    ],
                    "webhook": [
                        {
                            "variation_name": "Test Webhook",
                            "variation_api_id": "webhook_123",
                            "sent": 25,
                            "errors": 1,
                            "revenue": 50.0,
                            "unique_recipients": 24,
                            "conversions": 3,
                            "conversions_by_send_time": 2,
                            "conversions1": 1,
                            "conversions1_by_send_time": 1,
                            "conversions2": None,
                            "conversions2_by_send_time": None,
                            "conversions3": None,
                            "conversions3_by_send_time": None,
                            "enrolled": None,
                        }
                    ],
                },
            }
        ],
    }
