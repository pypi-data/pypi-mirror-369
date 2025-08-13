"""Real API validation tests for templates tools."""

import pytest

from braze_mcp.models.templates import (
    ContentBlockInfo,
    ContentBlocksResponse,
    EmailTemplateInfo,
    EmailTemplatesResponse,
)
from braze_mcp.tools.templates import (
    get_content_block_info,
    get_content_blocks,
    get_email_template_info,
    get_email_templates,
)
from braze_mcp.utils import get_logger

logger = get_logger(__name__)


@pytest.mark.real_api
class TestTemplatesRealAPI:
    """Real API tests for templates tools."""

    @pytest.mark.asyncio
    async def test_get_content_blocks_success(self, real_context):
        """Test get_content_blocks with real API call."""
        result = await get_content_blocks(real_context)

        assert isinstance(result, ContentBlocksResponse), (
            f"Expected ContentBlocksResponse, got {type(result)}"
        )

        logger.info(f"Found {result.count} content blocks in workspace")
        logger.info(f"Response returned {len(result.content_blocks)} content block objects")

        # Verify count matches actual items
        assert result.count == len(result.content_blocks), (
            "Count field should match number of content blocks returned"
        )

        # If there are content blocks, validate their structure
        if result.count > 0:
            first_block = result.content_blocks[0]

            # Verify required fields are present and have correct types
            assert isinstance(first_block.content_block_id, str), (
                "content_block_id should be string"
            )
            assert isinstance(first_block.name, str), "name should be string"
            assert isinstance(first_block.content_type, str), "content_type should be string"
            assert isinstance(first_block.liquid_tag, str), "liquid_tag should be string"
            assert isinstance(first_block.inclusion_count, int), "inclusion_count should be int"
            assert isinstance(first_block.created_at, str), "created_at should be string"
            assert isinstance(first_block.last_edited, str), "last_edited should be string"
            assert isinstance(first_block.tags, list), "tags should be list"

            # Verify content type is one of expected values
            assert first_block.content_type in ["html", "text"], (
                f"content_type should be 'html' or 'text', got '{first_block.content_type}'"
            )

            logger.info(f"Sample content block: {first_block.name} ({first_block.content_type})")
            logger.info(f"Tags: {first_block.tags}")
            logger.info(f"Inclusion count: {first_block.inclusion_count}")
        else:
            logger.info("No content blocks found in workspace")

    @pytest.mark.asyncio
    async def test_get_content_blocks_with_limit(self, real_context):
        """Test get_content_blocks with limit parameter."""
        limit = 5
        result = await get_content_blocks(real_context, limit=limit)

        assert isinstance(result, ContentBlocksResponse), (
            f"Expected ContentBlocksResponse, got {type(result)}"
        )

        # Should return at most the limit number of items
        assert len(result.content_blocks) <= limit, (
            f"Should return at most {limit} items, got {len(result.content_blocks)}"
        )

        logger.info(f"Requested limit {limit}, got {len(result.content_blocks)} content blocks")

    @pytest.mark.asyncio
    async def test_get_content_blocks_with_offset(self, real_context):
        """Test get_content_blocks with offset parameter."""
        # First get all content blocks to understand the dataset
        all_result = await get_content_blocks(real_context)
        assert isinstance(all_result, ContentBlocksResponse)

        if all_result.count <= 1:
            logger.info("Not enough content blocks to test offset - skipping")
            pytest.skip("Need at least 2 content blocks to test offset")

        # Now test with offset
        offset = 1
        offset_result = await get_content_blocks(real_context, offset=offset)

        assert isinstance(offset_result, ContentBlocksResponse)

        all_result_keys = {result.content_block_id for result in all_result.content_blocks}
        offset_result_keys = {result.content_block_id for result in offset_result.content_blocks}

        # Verify that there is a difference of one id between them.
        assert len(all_result_keys - offset_result_keys) == 1
        assert len(offset_result_keys - all_result_keys) == 1

    @pytest.mark.asyncio
    async def test_get_content_blocks_with_date_filters(self, real_context):
        """Test get_content_blocks with date filter parameters."""
        # Test with a date range (last 30 days)
        from datetime import datetime, timedelta

        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        modified_after = start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        modified_before = end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        result = await get_content_blocks(
            real_context, modified_after=modified_after, modified_before=modified_before
        )

        assert isinstance(result, ContentBlocksResponse)

        logger.info(f"Found {result.count} content blocks modified in last 30 days")

        if result.count > 0:
            for block in result.content_blocks:
                # Note: This is testing that we can make calls to the API with correctly formatted timestamps,
                # not ensuring that the API correctly handles them.
                assert isinstance(block.created_at, str), "created_at should be string"
                assert isinstance(block.last_edited, str), "last_edited should be string"
                logger.info(f"Block '{block.name}' last edited: {block.last_edited}")

    @pytest.mark.asyncio
    async def test_get_content_blocks_invalid_parameters(self, real_context):
        """Test get_content_blocks with invalid parameters."""
        # Test with invalid limit (too high)
        result = await get_content_blocks(real_context, limit=5000)  # Max is 1000

        # Should return error dict for invalid limit
        assert isinstance(result, dict), "Expected error dict for invalid limit"

        # Check for error structure
        assert "error" in result, "Should contain error information"

        logger.info("Correctly handled invalid limit parameter")

    @pytest.mark.asyncio
    async def test_get_content_block_info_without_inclusion_data(self, real_context):
        """Test get_content_block_info without inclusion data."""
        content_block_id = "92ed12a2-efd5-4967-9283-cfb8a5254581"

        result = await get_content_block_info(
            real_context, content_block_id=content_block_id, include_inclusion_data=False
        )

        assert isinstance(result, ContentBlockInfo), (
            f"Expected ContentBlockInfo, got {type(result)}"
        )

        # Verify content type is valid
        assert result.content_type in ["html", "text"], (
            f"content_type should be 'html' or 'text', got '{result.content_type}'"
        )

        # Verify inclusion_data is None when not requested
        assert result.inclusion_data is None, (
            "inclusion_data should be None when include_inclusion_data=False"
        )

        logger.info(f"Content block info: {result.name} ({result.content_type})")
        logger.info(f"Inclusion count: {result.inclusion_count}")
        logger.info(f"Tags: {result.tags}")

    @pytest.mark.asyncio
    async def test_get_content_block_info_with_inclusion_data(self, real_context):
        """Test get_content_block_info with inclusion data."""
        content_block_id = "92ed12a2-efd5-4967-9283-cfb8a5254581"

        result = await get_content_block_info(
            real_context, content_block_id=content_block_id, include_inclusion_data=True
        )

        assert isinstance(result, ContentBlockInfo), (
            f"Expected ContentBlockInfo, got {type(result)}"
        )

        # Verify basic structure
        assert result.content_block_id == content_block_id
        assert isinstance(result.name, str), "name should be string"
        assert isinstance(result.inclusion_count, int), "inclusion_count should be int"

        # Verify inclusion_data structure when requested
        if result.inclusion_count > 0:
            assert result.inclusion_data is not None, (
                "inclusion_data should not be None when include_inclusion_data=True and inclusion_count > 0"
            )
            assert isinstance(result.inclusion_data, list), "inclusion_data should be list"

            # Verify structure of inclusion data items
            for inclusion in result.inclusion_data:
                assert isinstance(inclusion.message_variation_id, str), (
                    "message_variation_id should be string"
                )
                # Either campaign_id OR canvas_step_id should be present, but not both
                has_campaign_id = inclusion.campaign_id is not None
                has_canvas_step_id = inclusion.canvas_step_id is not None
                assert has_campaign_id or has_canvas_step_id, (
                    "Each inclusion should have either campaign_id or canvas_step_id"
                )
                assert not (has_campaign_id and has_canvas_step_id), (
                    "Each inclusion should not have both campaign_id and canvas_step_id"
                )

            logger.info(f"Found {len(result.inclusion_data)} inclusions:")
            campaign_count = sum(1 for inc in result.inclusion_data if inc.campaign_id is not None)
            canvas_count = sum(1 for inc in result.inclusion_data if inc.canvas_step_id is not None)
            logger.info(f"  - {campaign_count} campaign inclusions")
            logger.info(f"  - {canvas_count} canvas step inclusions")
        else:
            logger.info("Content block has no inclusions")

    @pytest.mark.asyncio
    async def test_get_content_block_info_invalid_id(self, real_context):
        """Test get_content_block_info with bogus content block ID."""
        bogus_content_block_id = "00000000-0000-0000-0000-000000000000"

        result = await get_content_block_info(real_context, content_block_id=bogus_content_block_id)

        # Should return error dict for invalid content block ID
        assert isinstance(result, dict), (
            f"Expected error dict for invalid content block ID, got {type(result)}"
        )

        # Check for error structure
        assert "error" in result, "Should contain error information"

        logger.info("Correctly handled invalid content block ID")
        logger.info(f"Error response: {result}")

    @pytest.mark.asyncio
    async def test_get_email_templates_success(self, real_context):
        """Test get_email_templates with real API call."""
        result = await get_email_templates(real_context)

        assert isinstance(result, EmailTemplatesResponse), (
            f"Expected EmailTemplatesResponse, got {type(result)}"
        )

        logger.info(f"Found {result.count} email templates in workspace")

        # Verify count matches actual items
        assert result.count == len(result.templates), (
            "Count field should match number of templates returned"
        )

    @pytest.mark.asyncio
    async def test_get_email_templates_with_limit(self, real_context):
        """Test get_email_templates with limit parameter."""
        limit = 5
        result = await get_email_templates(real_context, limit=limit)

        assert isinstance(result, EmailTemplatesResponse), (
            f"Expected EmailTemplatesResponse, got {type(result)}"
        )

        # Should return at most the limit number of items
        assert len(result.templates) <= limit, (
            f"Should return at most {limit} items, got {len(result.templates)}"
        )

        logger.info(f"Requested limit {limit}, got {len(result.templates)} email templates")

    @pytest.mark.asyncio
    async def test_get_email_templates_with_offset(self, real_context):
        """Test get_email_templates with offset parameter."""
        all_result = await get_email_templates(real_context)
        assert isinstance(all_result, EmailTemplatesResponse)

        if all_result.count <= 1:
            logger.info("Not enough email templates to test offset - skipping")
            pytest.skip("Need at least 2 email templates to test offset")

        offset = 1
        offset_result = await get_email_templates(real_context, offset=offset)

        assert isinstance(offset_result, EmailTemplatesResponse)

        all_result_ids = {template.email_template_id for template in all_result.templates}
        offset_result_ids = {template.email_template_id for template in offset_result.templates}

        # Verify that there is a difference between them (offset should skip some templates)
        assert len(all_result_ids - offset_result_ids) == 1, (
            "Offset should result in different templates being returned"
        )

        logger.info(f"All templates count: {all_result.count}")
        logger.info(f"Offset templates count: {offset_result.count}")

    @pytest.mark.asyncio
    async def test_get_email_templates_with_date_filters(self, real_context):
        """Test get_email_templates with date filter parameters."""
        # Test with a date range (last 30 days)
        from datetime import datetime, timedelta

        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        modified_after = start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        modified_before = end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        result = await get_email_templates(
            real_context, modified_after=modified_after, modified_before=modified_before
        )

        assert isinstance(result, EmailTemplatesResponse)

        logger.info(f"Found {result.count} email templates modified in last 30 days")

        if result.count > 0:
            for template in result.templates:
                # Note: This is testing that we can make calls to the API with correctly formatted timestamps,
                # not ensuring that the API correctly handles them.
                assert isinstance(template.created_at, str), "created_at should be string"
                assert isinstance(template.updated_at, str), "updated_at should be string"
                logger.info(f"Template '{template.template_name}' updated: {template.updated_at}")

    @pytest.mark.asyncio
    async def test_get_email_templates_invalid_parameters(self, real_context):
        """Test get_email_templates with invalid parameters."""
        # Test with invalid limit (too high)
        result = await get_email_templates(real_context, limit=5000)  # Max is 1000

        # Should return error dict for invalid limit
        assert isinstance(result, dict), "Expected error dict for invalid limit"

        # Check for error structure
        assert "error" in result, "Should contain error information"

        logger.info("Correctly handled invalid limit parameter")


@pytest.mark.real_api
class TestEmailTemplateInfoRealAPI:
    """Real API tests for email template info tool."""

    @pytest.mark.asyncio
    async def test_get_email_template_info_success(self, real_context):
        """Test get_email_template_info with real API call."""
        template_id = "185e087a-b1e1-48d9-9d8d-b17be8734699"
        logger.info(f"Testing email template info with ID: {template_id}")

        result = await get_email_template_info(real_context, template_id)

        assert isinstance(result, EmailTemplateInfo), (
            f"Expected EmailTemplateInfo, got {type(result)}"
        )

        # Validate the template ID matches what we requested
        assert result.email_template_id == template_id, (
            f"Expected template ID {template_id}, got {result.email_template_id}"
        )

    @pytest.mark.asyncio
    async def test_get_email_template_info_with_invalid_id(self, real_context):
        """Test get_email_template_info with a completely invalid template ID."""
        invalid_template_id = "00000000-0000-0000-0000-000000000000"

        result = await get_email_template_info(real_context, invalid_template_id)

        # Should return error dict for invalid template ID
        assert isinstance(result, dict), (
            f"Expected error dict for invalid template ID, got {type(result)}"
        )

        # Check for error structure
        assert "error" in result, "Should contain error information"

        logger.info("Correctly handled completely invalid email template ID")
        logger.info(f"Error response: {result}")
