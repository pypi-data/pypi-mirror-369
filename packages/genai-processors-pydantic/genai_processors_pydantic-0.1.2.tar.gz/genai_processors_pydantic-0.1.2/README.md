# genai-processors-pydantic

[![PyPI version](https://img.shields.io/pypi/v/genai-processors-pydantic.svg)](https://pypi.org/project/genai-processors-pydantic/)
[![Validation](https://github.com/mbeacom/genai-processors-pydantic/actions/workflows/validate.yml/badge.svg)](https://github.com/mbeacom/genai-processors-pydantic/actions/workflows/validate.yml)
[![codecov](https://codecov.io/github/mbeacom/pydantic-gemini-processor/graph/badge.svg?token=9Ue94I4FEw)](https://codecov.io/github/mbeacom/pydantic-gemini-processor)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

A Pydantic validator processor for Google's [genai-processors](https://github.com/google-gemini/genai-processors) framework.

**Note:** This is an independent contrib processor that extends the genai-processors ecosystem.

## ⚠️ Important: Current Limitations & Roadmap

This processor was developed based on feedback from the genai-processors maintainers. While functional and tested, it has known limitations in certain scenarios. See [MAINTAINER_FEEDBACK.md](MAINTAINER_FEEDBACK.md) for detailed analysis and our roadmap to address these challenges:

* **Streaming**: Currently works best with complete JSON in single Parts
* **Tool Integration**: Planned support for `genai_types.ToolResponse` Parts
* **Multi-Model Validation**: Single-model design; multi-model support planned
* **MIME Type Independence**: ✅ Already handles unmarked JSON Parts

We're committed to addressing these limitations while maintaining a stable API.

## PydanticValidator

The PydanticValidator is a PartProcessor that validates the JSON content of a ProcessorPart against a specified [Pydantic](https://docs.pydantic.dev/latest/) model. It provides a simple, declarative way to enforce data schemas and improve the robustness of your AI pipelines.

## Motivation

In many AI applications, processors ingest data from external sources like user inputs or API calls. This data can be unpredictable or malformed. The PydanticValidator solves this by:

* **Preventing Errors:** It catches invalid data early, before it can cause errors in downstream processors like a GenaiModel or a database writer.
* **Ensuring Structure:** It guarantees that any data moving forward in the pipeline conforms to a reliable, expected structure.
* **Simplifying Logic:** It allows other processors to focus on their core tasks without being cluttered with boilerplate data validation code.

## Installation

Install the package from PyPI:

```bash
pip install genai-processors-pydantic
```

Or with uv:

```bash
uv add genai-processors-pydantic
```

This will automatically install the required dependencies:

* `genai-processors>=1.0.4`
* `pydantic>=2.0`

## Configuration

You can customize the validator's behavior by passing a ValidationConfig object during initialization.

```python
from genai_processors_pydantic import PydanticValidator, ValidationConfig

config = ValidationConfig(fail_on_error=True, strict_mode=True)
validator = PydanticValidator(MyModel, config=config)
```

### ValidationConfig Parameters

* fail_on_error (bool, default: False):
  * If False, the processor will catch ValidationErrors, add error details to the part's metadata, and allow the stream to continue.
  * If True, the processor will re-raise the ValidationError, stopping the stream immediately. This is useful for "fail-fast" scenarios.
* strict_mode (bool, default: False):
  * If False, Pydantic will attempt to coerce types where possible (e.g., converting the string "123" to the integer 123).
  * If True, Pydantic will enforce strict type matching and will not perform type coercion.

## Behavior and Metadata

The PydanticValidator processes parts that contain valid JSON in their text field. For each part it processes, it yields one or more new parts:

1. **The Result Part:** The original part, now with added metadata.
2. **A Status Part:** A message sent to the STATUS_STREAM indicating the outcome.

### On Successful Validation

* The yielded part's metadata['validation_status'] is set to 'success'.
* The metadata['validated_data'] contains the serialized dictionary representation of the validated data (ensuring ProcessorParts remain serializable).
* The part's text is updated to be the formatted JSON representation of the validated data.
* A processor.status() message like ✅ Successfully validated... is yielded.

### On Failed Validation

* The yielded part's metadata['validation_status'] is set to 'failure'.
* metadata['validation_errors'] contains a structured list of validation errors.
* metadata['original_data'] contains the raw data that failed validation.
* A processor.status() message like ❌ Validation failed... is yielded.

## Practical Demonstration: Building a Robust Pipeline

A common use case is to validate a stream of user data and route valid and invalid items to different downstream processors.
This example shows how to create a filter to separate the stream after validation.

### Example

```python
import asyncio
import json

from genai_processors import streams, processor
from genai_processors_pydantic import PydanticValidator
from pydantic import BaseModel, Field


# 1. Define the data schema.
class UserEvent(BaseModel):
    user_id: int
    event_name: str = Field(min_length=3)


# 2. Create the validator.
validator = PydanticValidator(model=UserEvent)

# 3. Define downstream processors for success and failure cases.
class DatabaseWriter(processor.PartProcessor):
    async def call(self, part: processor.ProcessorPart):
        validated_data = part.metadata['validated_data']
        print(
            f"DATABASE: Writing event '{validated_data['event_name']}' "
            f"for user {validated_data['user_id']}"
        )
        yield part


class ErrorLogger(processor.PartProcessor):
    async def call(self, part: processor.ProcessorPart):
        errors = part.metadata['validation_errors']
        print(f"ERROR_LOG: Found {len(errors)} validation errors.")
        yield part


# 4. Create a stream with mixed-quality data.
input_stream = streams.stream_content([
    # Valid example
    processor.ProcessorPart(json.dumps({"user_id": 101, "event_name": "login"})),
    # Invalid user_id
    processor.ProcessorPart(json.dumps({"user_id": "102", "event_name": "logout"})),
    # Invalid event_name
    processor.ProcessorPart(json.dumps({"user_id": 103, "event_name": "up"})),
    # Ignore this part
    processor.ProcessorPart("This is not a JSON part and will be ignored."),
])


# 5. Build and run the pipeline.
async def main():
    print("--- Running Validation Pipeline ---")

    # Process each input part through the validator as it arrives
    # This avoids buffering the entire stream in memory
    valid_parts = []
    invalid_parts = []

    async for input_part in input_stream:
        async for validated_part in validator(input_part):
            # Filter based on validation status (skip status messages)
            status = validated_part.metadata.get("validation_status")
            if status == "success":
                valid_parts.append(validated_part)
            elif status == "failure":
                invalid_parts.append(validated_part)

    # Create streams from the filtered parts
    valid_stream = streams.stream_content(valid_parts)
    invalid_stream = streams.stream_content(invalid_parts)

    # Create processor instances
    db_writer = DatabaseWriter()
    error_logger = ErrorLogger()

    # Process both streams concurrently
    async def process_valid():
        async for part in valid_stream:
            async for result in db_writer(part):
                pass  # Results are printed in the processor

    async def process_invalid():
        async for part in invalid_stream:
            async for result in error_logger(part):
                pass  # Results are printed in the processor

    # Run both processing pipelines concurrently
    await asyncio.gather(process_valid(), process_invalid())
    print("--- Pipeline Finished ---")


if __name__ == "__main__":
    asyncio.run(main())


# Expected Output:
# --- Running Validation Pipeline ---
# DATABASE: Writing event 'login' for user 101
# ERROR_LOG: Found 1 validation errors.
# ERROR_LOG: Found 1 validation errors.
# --- Pipeline Finished ---
```
