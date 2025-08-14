from pydantic import Field

from .common import BrazeBaseModel


class SDKAuthenticationKey(BrazeBaseModel):
    """Model representing an SDK Authentication key."""

    id: str = Field(..., description="The ID of the SDK Authentication key")
    rsa_public_key: str = Field(..., description="The RSA public key string")
    description: str = Field(..., description="Description of the SDK Authentication key")
    is_primary: bool = Field(
        ..., description="Whether this key is the primary SDK Authentication key"
    )


class SDKAuthenticationKeysResponse(BrazeBaseModel):
    """Response model for SDK Authentication keys list endpoint."""

    keys: list[SDKAuthenticationKey] = Field(
        ..., description="Array of SDK Authentication key objects"
    )
