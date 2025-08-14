from pydantic import Field

from .common import BrazeBaseModel


class ContentBlock(BrazeBaseModel):
    """
    Model representing a Content Block from the Braze API.
    """

    content_block_id: str = Field(..., description="The Content Block identifier")
    name: str = Field(..., description="The name of the Content Block")
    content_type: str = Field(..., description="The content type, html or text")
    liquid_tag: str = Field(..., description="The Liquid tags")
    inclusion_count: int = Field(..., description="The inclusion count")
    created_at: str = Field(..., description="The time the Content Block was created in ISO 8601")
    last_edited: str = Field(
        ..., description="The time the Content Block was last edited in ISO 8601"
    )
    tags: list[str] = Field(..., description="An array of tags formatted as strings")


class ContentBlocksResponse(BrazeBaseModel):
    """
    Model representing the response from the Content Blocks list endpoint.
    """

    count: int = Field(..., description="The number of Content Blocks returned")
    content_blocks: list[ContentBlock] = Field(..., description="List of Content Blocks")


class ContentBlockInclusionData(BrazeBaseModel):
    """
    Model representing inclusion data for where a Content Block is used.
    Can be either a campaign or canvas step inclusion.
    """

    campaign_id: str | None = Field(
        None, description="Campaign ID (present for campaign inclusions)"
    )
    canvas_step_id: str | None = Field(
        None, description="Canvas step ID (present for canvas inclusions)"
    )
    message_variation_id: str = Field(..., description="Message variation API identifier")


class ContentBlockInfo(BrazeBaseModel):
    """
    Model representing detailed information for a specific Content Block.
    """

    content_block_id: str = Field(..., description="The Content Block identifier")
    name: str = Field(..., description="The name of the Content Block")
    content: str = Field(..., description="The content in the Content Block")
    description: str = Field(..., description="The Content Block description")
    content_type: str = Field(..., description="The content type, html or text")
    tags: list[str] = Field(..., description="An array of tags formatted as strings")
    created_at: str = Field(..., description="The time the Content Block was created in ISO 8601")
    last_edited: str = Field(
        ..., description="The time the Content Block was last edited in ISO 8601"
    )
    inclusion_count: int = Field(..., description="The inclusion count")
    inclusion_data: list[ContentBlockInclusionData] | None = Field(
        None, description="The inclusion data (only present when include_inclusion_data=true)"
    )
    message: str = Field(..., description="Status message")


class EmailTemplate(BrazeBaseModel):
    """
    Model representing an email template from the templates list endpoint.
    """

    email_template_id: str = Field(..., description="Your email template's API Identifier")
    template_name: str | None = Field(None, description="The name of your email template")
    created_at: str = Field(..., description="The time the email was created at in ISO 8601")
    updated_at: str = Field(..., description="The time the email was updated in ISO 8601")
    tags: list[str] = Field(..., description="Tags appended to the template")


class EmailTemplatesResponse(BrazeBaseModel):
    """
    Model representing the response from the Email Templates list endpoint.
    """

    count: int = Field(..., description="The number of templates returned")
    templates: list[EmailTemplate] = Field(..., description="List of email templates")


class EmailTemplateInfo(BrazeBaseModel):
    """
    Model representing detailed information for a specific email template.
    """

    email_template_id: str = Field(..., description="Your email template's API Identifier")
    template_name: str | None = Field(None, description="The name of your email template")
    description: str = Field(..., description="The email template description")
    subject: str = Field(..., description="The email template subject line")
    preheader: str | None = Field(
        None, description="The email preheader used to generate previews in some clients"
    )
    body: str | None = Field(None, description="The email template body that may include HTML")
    plaintext_body: str | None = Field(
        None, description="A plaintext version of the email template body"
    )
    should_inline_css: bool | None = Field(
        None,
        description="Whether there is inline CSS in the body of the template - defaults to the css inlining value for the workspace",
    )
    tags: list[str] = Field(..., description="Tag names")
    created_at: str = Field(..., description="The time the email was created at in ISO 8601")
    updated_at: str = Field(..., description="The time the email was updated in ISO 8601")
