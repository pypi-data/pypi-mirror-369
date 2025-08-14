from pydantic import Field

from .common import BrazeBaseModel


class IOSPushMessageStatistics(BrazeBaseModel):
    """
    Model representing iOS push message statistics.
    """

    variation_name: str | None = Field(None, description="The variation name")
    variation_api_id: str | None = Field(None, description="The variation API identifier")
    sent: int | None = Field(None, description="The number of sends")
    delivered: int | None = Field(None, description="The number of messages successfully delivered")
    undelivered: int | None = Field(None, description="The number of undelivered")
    delivery_failed: int | None = Field(None, description="The number of rejected")
    direct_opens: int | None = Field(None, description="The number of direct opens")
    total_opens: int | None = Field(None, description="The number of total opens")
    bounces: int | None = Field(None, description="The number of bounces")
    body_clicks: int | None = Field(None, description="The number of body clicks")
    revenue: float | None = Field(None, description="The number of dollars of revenue (USD)")
    unique_recipients: int | None = Field(None, description="The number of unique recipients")
    conversions: int | None = Field(None, description="The number of conversions")
    conversions_by_send_time: int | None = Field(
        None, description="The number of conversions attributed to the date the campaign was sent"
    )
    conversions1: int | None = Field(
        None, description="The number of conversions for the second conversion event"
    )
    conversions1_by_send_time: int | None = Field(
        None,
        description="The number of conversions for the second conversion event attributed to the date the campaign was sent",
    )
    conversions2: int | None = Field(
        None, description="The number of conversions for the third conversion event"
    )
    conversions2_by_send_time: int | None = Field(
        None,
        description="The number of conversions for the third conversion event attributed to the date the campaign was sent",
    )
    conversions3: int | None = Field(
        None, description="The number of conversions for the fourth conversion event"
    )
    conversions3_by_send_time: int | None = Field(
        None,
        description="The number of conversions for the fourth conversion event attributed to the date the campaign was sent",
    )
    enrolled: int | None = Field(None, description="The number of enrolled users")


class AndroidPushMessageStatistics(BrazeBaseModel):
    """
    Model representing Android push message statistics.
    """

    variation_api_id: str = Field(..., description="The variation API identifier")
    sent: int = Field(..., description="The number of sends")
    direct_opens: int = Field(..., description="The number of direct opens")
    total_opens: int = Field(..., description="The number of total opens")
    bounces: int = Field(..., description="The number of bounces")
    body_clicks: int = Field(..., description="The number of body clicks")


class WebhookMessageStatistics(BrazeBaseModel):
    """
    Model representing webhook message statistics.
    """

    variation_name: str | None = Field(None, description="The variation name")
    variation_api_id: str = Field(..., description="The variation API identifier")
    sent: int | None = Field(None, description="The number of sends")
    errors: int | None = Field(None, description="The number of errors")
    revenue: float | None = Field(None, description="The number of dollars of revenue (USD)")
    unique_recipients: int | None = Field(None, description="The number of unique recipients")
    conversions: int | None = Field(None, description="The number of conversions")
    conversions_by_send_time: int | None = Field(
        None, description="The number of conversions attributed to the date the campaign was sent"
    )
    conversions1: int | None = Field(
        None, description="The number of conversions for the second conversion event"
    )
    conversions1_by_send_time: int | None = Field(
        None,
        description="The number of conversions for the second conversion event attributed to the date the campaign was sent",
    )
    conversions2: int | None = Field(
        None, description="The number of conversions for the third conversion event"
    )
    conversions2_by_send_time: int | None = Field(
        None,
        description="The number of conversions for the third conversion event attributed to the date the campaign was sent",
    )
    conversions3: int | None = Field(
        None, description="The number of conversions for the fourth conversion event"
    )
    conversions3_by_send_time: int | None = Field(
        None,
        description="The number of conversions for the fourth conversion event attributed to the date the campaign was sent",
    )
    enrolled: int | None = Field(None, description="The number of enrolled users")


class EmailMessageStatistics(BrazeBaseModel):
    """
    Model representing email message statistics.
    """

    variation_name: str | None = Field(None, description="The variation name")
    variation_api_id: str | None = Field(None, description="The variation API identifier")
    sent: int | None = Field(None, description="The number of sends")
    opens: int | None = Field(None, description="The number of opens")
    unique_opens: int | None = Field(None, description="The number of unique opens")
    clicks: int | None = Field(None, description="The number of clicks")
    unique_clicks: int | None = Field(None, description="The number of unique clicks")
    unsubscribes: int | None = Field(None, description="The number of unsubscribes")
    bounces: int | None = Field(None, description="The number of bounces")
    delivered: int | None = Field(None, description="The number of messages delivered")
    reported_spam: int | None = Field(None, description="The number of messages reported as spam")


class SMSMessageStatistics(BrazeBaseModel):
    """
    Model representing SMS message statistics.
    """

    variation_api_id: str = Field(..., description="The variation API identifier")
    sent: int = Field(..., description="The number of sends")
    sent_to_carrier: int = Field(..., description="The number of messages sent to the carrier")
    delivered: int = Field(..., description="The number of delivered messages")
    rejected: int = Field(..., description="The number of rejected messages")
    delivery_failed: int = Field(..., description="The number of failed deliveries")
    clicks: int = Field(..., description="The number of clicks on shortened links")
    opt_out: int = Field(..., description="The number of opt outs")
    help: int = Field(..., description="The number of help messages received")


class WhatsAppMessageStatistics(BrazeBaseModel):
    """
    Model representing WhatsApp message statistics.
    """

    variation_api_id: str = Field(..., description="The variation API identifier")
    sent: int = Field(..., description="The number of sends")
    delivered: int = Field(..., description="The number of delivered messages")
    failed: int = Field(..., description="The number of failed deliveries")
    read: int = Field(..., description="The number of opened messages")


class ContentCardMessageStatistics(BrazeBaseModel):
    """
    Model representing content card message statistics.
    """

    variation_api_id: str = Field(..., description="The variation API identifier")
    sent: int = Field(..., description="The number of sends")
    total_clicks: int = Field(..., description="The number of total clicks")
    total_dismissals: int = Field(..., description="The number of total dismissals")
    total_impressions: int = Field(..., description="The number of total impressions")
    unique_clicks: int = Field(..., description="The number of unique clicks")
    unique_dismissals: int = Field(..., description="The number of unique dismissals")
    unique_impressions: int = Field(..., description="The number of unique impressions")


class InAppMessageStatistics(BrazeBaseModel):
    """
    Model representing in-app message statistics.
    """

    variation_api_id: str = Field(..., description="The variation API identifier")
    impressions: int = Field(..., description="The number of impressions")
    clicks: int = Field(..., description="The number of clicks")
    first_button_clicks: int = Field(..., description="The number of first button clicks")
    second_button_clicks: int = Field(..., description="The number of second button clicks")


class KindlePushMessageStatistics(BrazeBaseModel):
    """
    Model representing Kindle push message statistics.
    """

    variation_api_id: str = Field(..., description="The variation API identifier")
    sent: int = Field(..., description="The number of sends")
    direct_opens: int = Field(..., description="The number of direct opens")
    total_opens: int = Field(..., description="The number of total opens")
    bounces: int = Field(..., description="The number of bounces")
    body_clicks: int = Field(..., description="The number of body clicks")


class WebPushMessageStatistics(BrazeBaseModel):
    """
    Model representing web push message statistics.
    """

    variation_api_id: str = Field(..., description="The variation API identifier")
    sent: int = Field(..., description="The number of sends")
    direct_opens: int = Field(..., description="The number of direct opens")
    total_opens: int = Field(..., description="The number of total opens")
    bounces: int = Field(..., description="The number of bounces")
    body_clicks: int = Field(..., description="The number of body clicks")


class TriggerInAppMessageStatistics(BrazeBaseModel):
    """
    Model representing trigger in-app message statistics for multivariate campaigns.
    """

    variation_name: str | None = Field(None, description="The variation name")
    impressions: int | None = Field(None, description="The number of impressions")
    clicks: int | None = Field(None, description="The number of clicks")
    first_button_clicks: int | None = Field(None, description="The number of first button clicks")
    second_button_clicks: int | None = Field(None, description="The number of second button clicks")
    revenue: float = Field(..., description="The number of dollars of revenue (USD)")
    unique_recipients: int = Field(..., description="The number of unique recipients")
    conversions: int = Field(..., description="The number of conversions")
    conversions_by_send_time: int = Field(
        ..., description="The number of conversions attributed to the date the campaign was sent"
    )
    conversions1: int | None = Field(
        None, description="The number of conversions for the second conversion event"
    )
    conversions1_by_send_time: int | None = Field(
        None,
        description="The number of conversions for the second conversion event attributed to the date the campaign was sent",
    )
    conversions2: int | None = Field(
        None, description="The number of conversions for the third conversion event"
    )
    conversions2_by_send_time: int | None = Field(
        None,
        description="The number of conversions for the third conversion event attributed to the date the campaign was sent",
    )
    conversions3: int | None = Field(
        None, description="The number of conversions for the fourth conversion event"
    )
    conversions3_by_send_time: int | None = Field(
        None,
        description="The number of conversions for the fourth conversion event attributed to the date the campaign was sent",
    )
    enrolled: int | None = Field(None, description="The number of enrolled users")


class MessageStatistics(BrazeBaseModel):
    """
    Model representing message statistics by channel for both campaign and send data series.
    """

    ios_push: list[IOSPushMessageStatistics] | None = Field(None, description="IOS push messages")
    android_push: list[AndroidPushMessageStatistics] | None = Field(
        None, description="Android push messages"
    )
    kindle_push: list[KindlePushMessageStatistics] | None = Field(
        None, description="Kindle push messages"
    )
    web_push: list[WebPushMessageStatistics] | None = Field(None, description="Web push messages")
    webhook: list[WebhookMessageStatistics] | None = Field(None, description="Webhook messages")
    email: list[EmailMessageStatistics] | None = Field(None, description="Email messages")
    sms: list[SMSMessageStatistics] | None = Field(None, description="SMS messages")
    whats_app: list[WhatsAppMessageStatistics] | None = Field(None, description="WhatsApp messages")
    content_cards: list[ContentCardMessageStatistics] | None = Field(
        None, description="Content card messages"
    )
    in_app_message: list[InAppMessageStatistics] | None = Field(None, description="In-app messages")
    trigger_in_app_message: list[TriggerInAppMessageStatistics] | None = Field(
        None, description="Trigger in-app messages for multivariate campaigns"
    )
