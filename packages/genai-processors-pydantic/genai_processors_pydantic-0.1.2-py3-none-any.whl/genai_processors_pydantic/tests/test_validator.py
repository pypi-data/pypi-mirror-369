"""Tests for PydanticValidator processor."""

import json

import pytest
from genai_processors import processor
from pydantic import BaseModel, Field, ValidationError

from genai_processors_pydantic.validator import (
    PydanticValidator,
    ValidationConfig,
)

ProcessorPart = processor.ProcessorPart


# Test Pydantic models
class UserProfile(BaseModel):
    """A simple user profile model for testing."""

    user_id: int
    username: str = Field(min_length=3)
    is_active: bool = True


class Product(BaseModel):
    """A product model for testing."""

    id: int
    name: str
    price: float = Field(gt=0)
    tags: list[str] = Field(default_factory=list)


class TestPydanticValidator:
    """Test suite for PydanticValidator."""

    @pytest.mark.anyio
    async def test_successful_validation(self) -> None:
        """Test that valid data passes validation."""
        validator = PydanticValidator(UserProfile)
        valid_data = {"user_id": 123, "username": "testuser"}
        part = ProcessorPart(
            json.dumps(valid_data),
            mimetype="application/json",
        )

        results = []
        async for result_part in validator(part):
            results.append(result_part)

        # Should have: validated part + status message
        assert len(results) == 2

        validated_part = results[0]
        status_part = results[1]

        # Check validated part
        assert validated_part.metadata["validation_status"] == "success"
        assert validated_part.metadata["validated_model"] == "UserProfile"

        # The validated data should be in metadata as a dictionary
        validated_data = validated_part.metadata["validated_data"]
        assert isinstance(validated_data, dict)
        assert validated_data["user_id"] == 123
        assert validated_data["is_active"] is True  # Default value applied

        # Check status message
        assert status_part.substream_name == processor.STATUS_STREAM
        assert "Successfully validated" in status_part.text

    @pytest.mark.anyio
    async def test_failed_validation_permissive_mode(self) -> None:
        """Test invalid data fails validation gracefully in permissive mode."""
        validator = PydanticValidator(UserProfile)
        # Too short username
        invalid_data = {"user_id": "not-an-int", "username": "a"}
        part = ProcessorPart(
            json.dumps(invalid_data),
            mimetype="application/json",
        )

        results = []
        async for result_part in validator(part):
            results.append(result_part)

        # Should have: status message + failed part
        assert len(results) == 2

        status_part = results[0]
        failed_part = results[1]

        # Check status message
        assert "Validation failed" in status_part.text

        # Check failed part
        assert failed_part.metadata["validation_status"] == "failure"
        assert "validation_errors" in failed_part.metadata
        assert "original_data" in failed_part.metadata

    @pytest.mark.anyio
    async def test_failed_validation_strict_mode(self) -> None:
        """Test that validation errors are raised in fail-fast mode."""
        config = ValidationConfig(fail_on_error=True)
        validator = PydanticValidator(UserProfile, config=config)
        invalid_data = {"user_id": "not-an-int", "username": "a"}
        part = ProcessorPart(
            json.dumps(invalid_data),
            mimetype="application/json",
        )

        # Should raise ValidationError due to fail_on_error=True
        with pytest.raises(ValidationError):
            async for _ in validator(part):
                pass

    @pytest.mark.anyio
    async def test_passthrough_for_non_json_parts(self) -> None:
        """Test parts without JSON content are passed through unchanged."""
        validator = PydanticValidator(UserProfile)
        part = ProcessorPart("This is just a text part.")

        results = []
        async for result_part in validator(part):
            results.append(result_part)

        # Should just pass through the original part
        assert len(results) == 1
        result_part = results[0]
        assert "validation_status" not in result_part.metadata
        assert result_part.text == "This is just a text part."

    @pytest.mark.anyio
    async def test_strict_mode_validation(self) -> None:
        """Test strict mode validation with more rigorous type checking."""
        config = ValidationConfig(strict_mode=True)
        validator = PydanticValidator(Product, config=config)

        # Data that might pass in normal mode but fail in strict mode - strings
        loose_data = {"id": "123", "name": "Test Product", "price": "19.99"}
        part = ProcessorPart(
            json.dumps(loose_data),
            mimetype="application/json",
        )

        results = []
        async for result_part in validator(part):
            results.append(result_part)

        # In strict mode, this should fail validation
        # First result should be status, second should be failed part
        status_part = results[0]
        failed_part = results[1]
        assert "Validation failed" in status_part.text
        assert failed_part.metadata["validation_status"] == "failure"

    @pytest.mark.anyio
    async def test_strict_mode_accepts_valid_types(self) -> None:
        """Test that strict mode accepts correctly typed data."""
        config = ValidationConfig(strict_mode=True)
        validator = PydanticValidator(Product, config=config)

        # Data with correct types that should pass even in strict mode
        valid_data = {"id": 123, "name": "Test Product", "price": 19.99}
        part = ProcessorPart(
            json.dumps(valid_data),
            mimetype="application/json",
        )

        results = []
        async for result_part in validator(part):
            results.append(result_part)

        # Should have: validated part + status message
        assert len(results) == 2
        validated_part = results[0]
        status_part = results[1]

        # Check successful validation
        assert validated_part.metadata["validation_status"] == "success"
        assert "Successfully validated" in status_part.text

        # Verify the validated data as a dictionary
        validated_data = validated_part.metadata["validated_data"]
        assert isinstance(validated_data, dict)
        assert validated_data["id"] == 123
        assert validated_data["price"] == 19.99

    def test_match_function(self) -> None:
        """Test the match function correctly identifies processable parts."""
        validator = PydanticValidator(UserProfile)

        # Should match parts with JSON mimetype and text content
        json_part = ProcessorPart(
            '{"test": "data"}',
            mimetype="application/json",
        )
        assert validator.match(json_part) is True

        # Should match parts with valid JSON in text even without JSON mimetype
        json_text_part = ProcessorPart('{"user_id": 1, "username": "test"}')
        assert validator.match(json_text_part) is True

        # Should not match parts without parseable JSON
        text_part = ProcessorPart("just text")
        assert validator.match(text_part) is False

        # Should match parts with JSON mimetype even if JSON is invalid
        # (validation failure will be handled in call(), not match())
        invalid_json_part = ProcessorPart(
            "invalid json {",
            mimetype="application/json",
        )
        assert validator.match(invalid_json_part) is True

    @pytest.mark.anyio
    async def test_invalid_json_handling(self) -> None:
        """Test handling of invalid JSON in text field."""
        validator = PydanticValidator(UserProfile)
        part = ProcessorPart(
            "invalid json {",
            mimetype="application/json",
        )

        results = []
        async for result_part in validator(part):
            results.append(result_part)

        # Should just pass through the original part (no valid JSON found)
        assert len(results) == 1
        result_part = results[0]
        assert result_part.text == "invalid json {"

    def test_initialization_with_non_pydantic_model(self) -> None:
        """Test that initialization raises error for non-Pydantic models."""

        class NotAPydanticModel:
            """A dummy class that is not a Pydantic model."""

        with pytest.raises(TypeError):
            PydanticValidator(NotAPydanticModel)

    def test_key_prefix(self) -> None:
        """Test that the processor has a proper key prefix."""
        validator = PydanticValidator(UserProfile)
        assert hasattr(validator, "key_prefix")
        assert "PydanticValidator" in validator.key_prefix
