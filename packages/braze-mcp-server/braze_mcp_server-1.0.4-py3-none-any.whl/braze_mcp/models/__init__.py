# Campaign models
from .campaign_dataseries import (
    CampaignDataSeriesData,
    CampaignDataSeriesResponse,
)
from .campaigns import (
    Campaign,
    CampaignDetails,
    CampaignListResponse,
    CampaignMessage,
    ConversionBehavior,
)

# Canvas models
from .canvas_dataseries import (
    CanvasDataSeriesData,
    CanvasDataSeriesEmailMessageStats,
    CanvasDataSeriesResponse,
    CanvasDataSeriesSMSMessageStats,
    CanvasDataSeriesStatsData,
    CanvasDataSeriesStepMessages,
    CanvasDataSeriesStepStats,
    CanvasDataSeriesTotalStats,
    CanvasDataSeriesVariantStats,
)
from .canvases import (
    Canvas,
    CanvasDataSummaryResponse,
    CanvasDetails,
    CanvasListResponse,
)

# Catalog models
from .catalogs import (
    Catalog,
    CatalogField,
    CatalogItem,
    CatalogItemsResponse,
    CatalogItemsWithPagination,
    CatalogSelection,
    CatalogsResponse,
)

# Common models
from .common import (
    BrazeBaseModel,
    PaginationInfo,
)

# Custom attributes models
from .custom_attributes import (
    CustomAttribute,
    CustomAttributesResponse,
    CustomAttributesWithPagination,
)

# Error response models
from .errors import (
    BrazeError,
    ErrorResponse,
    ErrorType,
    # Convenience functions for error creation
    api_error,
    function_not_found_error,
    http_error,
    internal_error,
    invalid_params_error,
    parsing_error,
    unexpected_response_error,
    validation_error,
)

# Events models
from .events import (
    Event,
    EventDataSeriesDataPoint,
    EventDataSeriesResponse,
    EventListResponse,
    EventsResponse,
    EventsWithPagination,
)

# Integrations models
from .integrations import (
    Integration,
    IntegrationsListResponse,
    JobSyncStatus,
    JobSyncStatusResponse,
)

# KPI models
from .kpi import (
    DAUDataSeriesResponse,
    MAUDataSeriesResponse,
    NewUsersDataSeriesResponse,
    UninstallsDataSeriesResponse,
)

# Message statistics models
from .message_statistics import (
    AndroidPushMessageStatistics,
    ContentCardMessageStatistics,
    EmailMessageStatistics,
    InAppMessageStatistics,
    IOSPushMessageStatistics,
    KindlePushMessageStatistics,
    MessageStatistics,
    SMSMessageStatistics,
    TriggerInAppMessageStatistics,
    WebhookMessageStatistics,
    WebPushMessageStatistics,
    WhatsAppMessageStatistics,
)

# Messages models
from .messages import (
    ScheduledBroadcast,
    ScheduledBroadcastsResponse,
)

# Preference Centers models
from .preference_centers import PreferenceCenter, PreferenceCenterDetails, PreferenceCentersResponse

# Purchases models
from .purchases import (
    ProductListResponse,
    QuantitySeriesResponse,
    RevenueSeriesResponse,
)

# SDK Authentication models
from .sdk_authentication import (
    SDKAuthenticationKey,
    SDKAuthenticationKeysResponse,
)

# Segments models
from .segments import (
    Segment,
    SegmentDataSeriesResponse,
    SegmentDetails,
    SegmentListResponse,
)

# Send models
from .send_dataseries import (
    SendDataSeriesData,
    SendDataSeriesResponse,
)

# Sessions models
from .sessions import (
    SessionDataPoint,
    SessionDataSeriesResponse,
)

# Subscription Groups models
from .subscription_groups import (
    SubscriptionGroup,
    SubscriptionGroupsResponse,
    SubscriptionGroupStatusResponse,
    UserSubscriptionGroups,
)

# Templates models
from .templates import (
    ContentBlock,
    ContentBlockInclusionData,
    ContentBlockInfo,
    ContentBlocksResponse,
    EmailTemplate,
    EmailTemplateInfo,
    EmailTemplatesResponse,
)

__all__ = [
    # Campaign models
    "Campaign",
    "CampaignDetails",
    "CampaignListResponse",
    "CampaignMessage",
    "ConversionBehavior",
    "CampaignDataSeriesData",
    "CampaignDataSeriesResponse",
    # Canvas models
    "Canvas",
    "CanvasDataSummaryResponse",
    "CanvasDetails",
    "CanvasListResponse",
    "CanvasDataSeriesData",
    "CanvasDataSeriesEmailMessageStats",
    "CanvasDataSeriesResponse",
    "CanvasDataSeriesSMSMessageStats",
    "CanvasDataSeriesStatsData",
    "CanvasDataSeriesStepMessages",
    "CanvasDataSeriesStepStats",
    "CanvasDataSeriesTotalStats",
    "CanvasDataSeriesVariantStats",
    # Catalog models
    "Catalog",
    "CatalogField",
    "CatalogItem",
    "CatalogItemsResponse",
    "CatalogItemsWithPagination",
    "CatalogSelection",
    "CatalogsResponse",
    # Custom attributes models
    "CustomAttribute",
    "CustomAttributesResponse",
    "CustomAttributesWithPagination",
    # Events models
    "Event",
    "EventDataSeriesDataPoint",
    "EventDataSeriesResponse",
    "EventListResponse",
    "EventsResponse",
    "EventsWithPagination",
    # Integrations models
    "Integration",
    "IntegrationsListResponse",
    "JobSyncStatus",
    "JobSyncStatusResponse",
    # KPI models
    "DAUDataSeriesResponse",
    "MAUDataSeriesResponse",
    "NewUsersDataSeriesResponse",
    "UninstallsDataSeriesResponse",
    # Messages models
    "ScheduledBroadcast",
    "ScheduledBroadcastsResponse",
    # Preference Centers models
    "PreferenceCenter",
    "PreferenceCenterDetails",
    "PreferenceCentersResponse",
    # Message statistics models
    "AndroidPushMessageStatistics",
    "ContentCardMessageStatistics",
    "EmailMessageStatistics",
    "InAppMessageStatistics",
    "IOSPushMessageStatistics",
    "KindlePushMessageStatistics",
    "MessageStatistics",
    "SMSMessageStatistics",
    "TriggerInAppMessageStatistics",
    "WebhookMessageStatistics",
    "WebPushMessageStatistics",
    "WhatsAppMessageStatistics",
    # Purchases models
    "ProductListResponse",
    "QuantitySeriesResponse",
    "RevenueSeriesResponse",
    # SDK Authentication models
    "SDKAuthenticationKey",
    "SDKAuthenticationKeysResponse",
    # Segments models
    "Segment",
    "SegmentDataSeriesResponse",
    "SegmentDetails",
    "SegmentListResponse",
    # Subscription Groups models
    "SubscriptionGroup",
    "SubscriptionGroupsResponse",
    "SubscriptionGroupStatusResponse",
    "UserSubscriptionGroups",
    # Send models
    "SendDataSeriesData",
    "SendDataSeriesResponse",
    # Sessions models
    "SessionDataPoint",
    "SessionDataSeriesResponse",
    # Common models
    "BrazeBaseModel",
    "PaginationInfo",
    # Error response models
    "BrazeError",
    "ErrorResponse",
    "ErrorType",
    # Convenience functions
    "api_error",
    "function_not_found_error",
    "http_error",
    "internal_error",
    "invalid_params_error",
    "parsing_error",
    "unexpected_response_error",
    "validation_error",
    "ContentBlock",
    "ContentBlockInclusionData",
    "ContentBlockInfo",
    "ContentBlocksResponse",
    "EmailTemplate",
    "EmailTemplateInfo",
    "EmailTemplatesResponse",
]
