# SPDX-License-Identifier: Apache-2.0
"""Tests for LLMChatWithParsingRetryBlock composite block."""

# Standard
from unittest.mock import MagicMock, patch

# Third Party
from datasets import Dataset

# First Party
from sdg_hub.core.blocks.llm import LLMChatWithParsingRetryBlock
from sdg_hub.core.blocks.llm.llm_chat_with_parsing_retry_block import (
    MaxRetriesExceededError,
)
from sdg_hub.core.utils.error_handling import BlockValidationError
import pytest


@pytest.fixture
def mock_litellm_completion():
    """Mock LiteLLM completion function for successful responses."""
    with patch("sdg_hub.core.blocks.llm.client_manager.completion") as mock_completion:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "<answer>Test response</answer>"
        mock_completion.return_value = mock_response
        yield mock_completion


@pytest.fixture
def mock_litellm_completion_multiple():
    """Mock LiteLLM completion function for multiple responses (n > 1)."""
    with patch("sdg_hub.core.blocks.llm.client_manager.completion") as mock_completion:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(), MagicMock(), MagicMock()]
        mock_response.choices[0].message.content = "<answer>Response 1</answer>"
        mock_response.choices[1].message.content = "<answer>Response 2</answer>"
        mock_response.choices[2].message.content = "<answer>Response 3</answer>"
        mock_completion.return_value = mock_response
        yield mock_completion


@pytest.fixture
def mock_litellm_completion_partial():
    """Mock LiteLLM completion that returns some parseable and some unparseable responses."""
    with patch("sdg_hub.core.blocks.llm.client_manager.completion") as mock_completion:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(), MagicMock()]
        mock_response.choices[0].message.content = "<answer>Good response</answer>"
        mock_response.choices[1].message.content = "Unparseable response"
        mock_completion.return_value = mock_response
        yield mock_completion


@pytest.fixture
def mock_litellm_completion_unparseable():
    """Mock LiteLLM completion that always returns unparseable responses."""
    with patch("sdg_hub.core.blocks.llm.client_manager.completion") as mock_completion:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "No tags in this response"
        mock_completion.return_value = mock_response
        yield mock_completion


@pytest.fixture
def sample_messages():
    """Sample messages in OpenAI format."""
    return [
        [{"role": "user", "content": "Please provide an answer in <answer> tags."}],
        [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "What is 2+2? Use <answer> tags."},
        ],
    ]


@pytest.fixture
def sample_dataset(sample_messages):
    """Create a sample dataset with messages."""
    return Dataset.from_dict({"messages": sample_messages})


class TestLLMChatWithParsingRetryBlockInitialization:
    """Test block initialization and configuration validation."""

    def test_basic_initialization_tag_parsing(self, mock_litellm_completion):
        """Test basic initialization with tag-based parsing."""
        block = LLMChatWithParsingRetryBlock(
            block_name="test_retry_block",
            input_cols="messages",
            output_cols="parsed_answer",
            model="openai/gpt-4",
            start_tags=["<answer>"],
            end_tags=["</answer>"],
            parsing_max_retries=3,
        )

        assert block.block_name == "test_retry_block"
        assert block.input_cols == ["messages"]
        assert block.output_cols == ["parsed_answer"]
        assert block.llm_params["model"] == "openai/gpt-4"
        assert block.parsing_max_retries == 3
        assert block.parser_params["start_tags"] == ["<answer>"]
        assert block.parser_params["end_tags"] == ["</answer>"]

        # Check internal blocks are created
        assert block.llm_chat is not None
        assert block.text_parser is not None
        assert block.llm_chat.block_name == "test_retry_block_llm_chat"
        assert block.text_parser.block_name == "test_retry_block_text_parser"

    def test_initialization_regex_parsing(self, mock_litellm_completion):
        """Test initialization with regex-based parsing."""
        block = LLMChatWithParsingRetryBlock(
            block_name="test_regex_retry",
            input_cols="messages",
            output_cols="result",
            model="anthropic/claude-3-sonnet-20240229",
            parsing_pattern=r'"result":\s*"([^"]*)"',
            parsing_max_retries=5,
        )

        assert block.parser_params["parsing_pattern"] == r'"result":\s*"([^"]*)"'
        assert block.parsing_max_retries == 5
        assert block.text_parser.parsing_pattern == r'"result":\s*"([^"]*)"'

    def test_initialization_multiple_output_columns(self, mock_litellm_completion):
        """Test initialization with multiple output columns."""
        block = LLMChatWithParsingRetryBlock(
            block_name="test_multi_output",
            input_cols="messages",
            output_cols=["explanation", "answer"],
            model="openai/gpt-4",
            start_tags=["<explanation>", "<answer>"],
            end_tags=["</explanation>", "</answer>"],
        )

        assert len(block.output_cols) == 2
        assert block.output_cols == ["explanation", "answer"]
        assert len(block.parser_params["start_tags"]) == 2
        assert len(block.parser_params["end_tags"]) == 2

    def test_initialization_all_llm_parameters(self, mock_litellm_completion):
        """Test initialization with all LLM generation parameters."""
        block = LLMChatWithParsingRetryBlock(
            block_name="test_all_params",
            input_cols="messages",
            output_cols="response",
            model="openai/gpt-4",
            api_key="test-key",
            api_base="https://api.openai.com/v1",
            temperature=0.8,
            max_tokens=150,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.2,
            stop=["END"],
            seed=42,
            n=2,
            start_tags=["<response>"],
            end_tags=["</response>"],
            parsing_max_retries=4,
        )

        # Check that parameters are passed to internal LLM block
        assert block.llm_chat.temperature == 0.8
        assert block.llm_chat.max_tokens == 150
        assert block.llm_chat.top_p == 0.9
        assert block.llm_chat.n == 2
        assert block.llm_chat.seed == 42

    def test_input_column_validation(self):
        """Test validation of input columns."""
        # Multiple input columns should raise error
        with pytest.raises(ValueError, match="exactly one input column"):
            LLMChatWithParsingRetryBlock(
                block_name="test_invalid",
                input_cols=["messages1", "messages2"],
                output_cols="response",
                model="openai/gpt-4",
                start_tags=["<answer>"],
                end_tags=["</answer>"],
            )

    def test_parsing_max_retries_validation(self):
        """Test validation of parsing_max_retries parameter."""
        # Negative retries should raise error
        with pytest.raises(ValueError, match="parsing_max_retries must be at least 1"):
            LLMChatWithParsingRetryBlock(
                block_name="test_invalid",
                input_cols="messages",
                output_cols="response",
                model="openai/gpt-4",
                parsing_max_retries=0,
                start_tags=["<answer>"],
                end_tags=["</answer>"],
            )

    def test_parsing_configuration_validation(self):
        """Test validation of parsing configuration."""
        # No parsing method should raise error
        with pytest.raises(ValueError, match="at least one parsing method"):
            LLMChatWithParsingRetryBlock(
                block_name="test_invalid",
                input_cols="messages",
                output_cols="response",
                model="openai/gpt-4",
                # No parsing_pattern, start_tags, or end_tags
            )

    def test_model_configuration_requirement(self, mock_litellm_completion):
        """Test that model configuration is required for generation."""
        # Create block without model
        block = LLMChatWithParsingRetryBlock(
            block_name="test_no_model",
            input_cols="messages",
            output_cols="response",
            start_tags=["<answer>"],
            end_tags=["</answer>"],
            # No model specified
        )

        dataset = Dataset.from_dict(
            {"messages": [[{"role": "user", "content": "test"}]]}
        )

        # Should raise BlockValidationError when trying to generate
        with pytest.raises(BlockValidationError, match="Model not configured"):
            block.generate(dataset)


class TestLLMChatWithParsingRetryBlockSuccessfulGeneration:
    """Test successful parsing scenarios with retry logic."""

    def test_successful_generation_first_attempt(
        self, mock_litellm_completion, sample_dataset
    ):
        """Test successful generation on first attempt."""
        block = LLMChatWithParsingRetryBlock(
            block_name="test_success",
            input_cols="messages",
            output_cols="answer",
            model="openai/gpt-4",
            start_tags=["<answer>"],
            end_tags=["</answer>"],
            parsing_max_retries=3,
        )

        result = block.generate(sample_dataset)

        # Should succeed on first attempt
        assert len(result) == 2  # Two input samples
        assert all("answer" in row for row in result)
        assert all(row["answer"] == "Test response" for row in result)

        # LLM should be called once per sample (no retries needed)
        assert mock_litellm_completion.call_count == 2

    def test_successful_generation_with_n_parameter(
        self, mock_litellm_completion_multiple, sample_dataset
    ):
        """Test successful generation with n > 1."""
        block = LLMChatWithParsingRetryBlock(
            block_name="test_multiple",
            input_cols="messages",
            output_cols="answer",
            model="openai/gpt-4",
            start_tags=["<answer>"],
            end_tags=["</answer>"],
            n=3,  # Generate 3 responses per sample
            parsing_max_retries=2,
        )

        result = block.generate(sample_dataset)

        # Should generate 3 responses per input sample = 6 total
        assert len(result) == 6
        expected_responses = ["Response 1", "Response 2", "Response 3"] * 2
        actual_responses = [row["answer"] for row in result]
        assert actual_responses == expected_responses

    def test_successful_generation_multiple_output_columns(
        self, mock_litellm_completion, sample_dataset
    ):
        """Test successful generation with multiple output columns."""
        # Mock response with multiple tags
        mock_litellm_completion.return_value.choices[
            0
        ].message.content = (
            "<explanation>This is an explanation</explanation><answer>42</answer>"
        )

        block = LLMChatWithParsingRetryBlock(
            block_name="test_multi_cols",
            input_cols="messages",
            output_cols=["explanation", "answer"],
            model="openai/gpt-4",
            start_tags=["<explanation>", "<answer>"],
            end_tags=["</explanation>", "</answer>"],
            parsing_max_retries=3,
        )

        result = block.generate(sample_dataset)

        assert len(result) == 2
        for row in result:
            assert row["explanation"] == "This is an explanation"
            assert row["answer"] == "42"

    def test_successful_generation_after_retry(self, sample_dataset):
        """Test successful generation after initial parsing failures."""
        with patch(
            "sdg_hub.core.blocks.llm.client_manager.completion"
        ) as mock_completion:
            # First call returns unparseable, second returns parseable
            mock_response_bad = MagicMock()
            mock_response_bad.choices = [MagicMock()]
            mock_response_bad.choices[0].message.content = "No tags here"

            mock_response_good = MagicMock()
            mock_response_good.choices = [MagicMock()]
            mock_response_good.choices[
                0
            ].message.content = "<answer>Good response</answer>"

            # Alternate between bad and good responses
            mock_completion.side_effect = [
                mock_response_bad,
                mock_response_good,  # For first sample
                mock_response_bad,
                mock_response_good,  # For second sample
            ]

            block = LLMChatWithParsingRetryBlock(
                block_name="test_retry_success",
                input_cols="messages",
                output_cols="answer",
                model="openai/gpt-4",
                start_tags=["<answer>"],
                end_tags=["</answer>"],
                parsing_max_retries=3,
            )

            result = block.generate(sample_dataset)

            # Should succeed after retry
            assert len(result) == 2
            assert all(row["answer"] == "Good response" for row in result)

            # Should have called LLM twice per sample (1 retry each)
            assert mock_completion.call_count == 4

    def test_partial_success_accumulation(self, sample_dataset):
        """Test accumulation of partial successes across retries."""
        with patch(
            "sdg_hub.core.blocks.llm.client_manager.completion"
        ) as mock_completion:
            # First call returns 1 parseable out of 2, second call returns 1 more
            mock_response_1 = MagicMock()
            mock_response_1.choices = [MagicMock(), MagicMock()]
            mock_response_1.choices[0].message.content = "<answer>First good</answer>"
            mock_response_1.choices[1].message.content = "Unparseable"

            mock_response_2 = MagicMock()
            mock_response_2.choices = [MagicMock(), MagicMock()]
            mock_response_2.choices[0].message.content = "<answer>Second good</answer>"
            mock_response_2.choices[1].message.content = "Also unparseable"

            mock_completion.side_effect = [mock_response_1, mock_response_2] * 2

            block = LLMChatWithParsingRetryBlock(
                block_name="test_accumulate",
                input_cols="messages",
                output_cols="answer",
                model="openai/gpt-4",
                start_tags=["<answer>"],
                end_tags=["</answer>"],
                n=2,  # Want 2 responses per sample
                parsing_max_retries=3,
            )

            result = block.generate(sample_dataset)

            # Should accumulate 2 responses per sample = 4 total
            assert len(result) == 4
            expected_answers = ["First good", "Second good"] * 2
            actual_answers = [row["answer"] for row in result]
            assert actual_answers == expected_answers

    def test_excess_results_trimming(self, sample_dataset):
        """Test trimming results when exceeding target count."""
        with patch(
            "sdg_hub.core.blocks.llm.client_manager.completion"
        ) as mock_completion:
            # Return 3 parseable responses when only 2 are needed
            mock_response = MagicMock()
            mock_response.choices = [MagicMock(), MagicMock(), MagicMock()]
            mock_response.choices[0].message.content = "<answer>Response 1</answer>"
            mock_response.choices[1].message.content = "<answer>Response 2</answer>"
            mock_response.choices[2].message.content = "<answer>Response 3</answer>"
            mock_completion.return_value = mock_response

            block = LLMChatWithParsingRetryBlock(
                block_name="test_trim",
                input_cols="messages",
                output_cols="answer",
                model="openai/gpt-4",
                start_tags=["<answer>"],
                end_tags=["</answer>"],
                n=2,  # Only want 2 responses
                parsing_max_retries=3,
            )

            result = block.generate(sample_dataset)

            # Should trim to exactly 2 responses per sample = 4 total
            assert len(result) == 4
            expected_answers = ["Response 1", "Response 2"] * 2
            actual_answers = [row["answer"] for row in result]
            assert actual_answers == expected_answers


class TestLLMChatWithParsingRetryBlockMaxRetriesExceeded:
    """Test MaxRetriesExceededError scenarios."""

    def test_max_retries_exceeded_no_successful_parses(
        self, mock_litellm_completion_unparseable, sample_dataset
    ):
        """Test MaxRetriesExceededError when no responses can be parsed."""
        block = LLMChatWithParsingRetryBlock(
            block_name="test_max_retries",
            input_cols="messages",
            output_cols="answer",
            model="openai/gpt-4",
            start_tags=["<answer>"],
            end_tags=["</answer>"],
            parsing_max_retries=2,
        )

        # Create single sample dataset to test specific error message
        single_dataset = Dataset.from_dict(
            {"messages": [sample_dataset["messages"][0]]}
        )

        with pytest.raises(MaxRetriesExceededError) as exc_info:
            block.generate(single_dataset)

        error = exc_info.value
        assert error.target_count == 1
        assert error.actual_count == 0
        assert error.max_retries == 2
        assert "Failed to achieve target count 1 after 2 retries" in str(error)

    def test_max_retries_exceeded_partial_success(self, sample_dataset):
        """Test MaxRetriesExceededError when some but not all responses are parsed."""
        with patch(
            "sdg_hub.core.blocks.llm.client_manager.completion"
        ) as mock_completion:
            # Always return 1 parseable out of 3 needed
            mock_response = MagicMock()
            mock_response.choices = [MagicMock(), MagicMock(), MagicMock()]
            mock_response.choices[0].message.content = "<answer>Only one good</answer>"
            mock_response.choices[1].message.content = "Unparseable"
            mock_response.choices[2].message.content = "Also unparseable"
            mock_completion.return_value = mock_response

            block = LLMChatWithParsingRetryBlock(
                block_name="test_partial_failure",
                input_cols="messages",
                output_cols="answer",
                model="openai/gpt-4",
                start_tags=["<answer>"],
                end_tags=["</answer>"],
                n=3,  # Need 3 responses
                parsing_max_retries=2,
            )

            # Test with single sample for clearer error checking
            single_dataset = Dataset.from_dict(
                {"messages": [sample_dataset["messages"][0]]}
            )

            with pytest.raises(MaxRetriesExceededError) as exc_info:
                block.generate(single_dataset)

            error = exc_info.value
            assert error.target_count == 3
            assert error.actual_count == 2  # Got 1 per retry attempt × 2 attempts
            assert error.max_retries == 2

    def test_max_retries_exceeded_error_details(
        self, mock_litellm_completion_unparseable, sample_dataset
    ):
        """Test detailed error information in MaxRetriesExceededError."""
        block = LLMChatWithParsingRetryBlock(
            block_name="test_error_details",
            input_cols="messages",
            output_cols="answer",
            model="openai/gpt-4",
            start_tags=["<answer>"],
            end_tags=["</answer>"],
            n=5,  # High target to test error details
            parsing_max_retries=3,
        )

        single_dataset = Dataset.from_dict(
            {"messages": [sample_dataset["messages"][0]]}
        )

        with pytest.raises(MaxRetriesExceededError) as exc_info:
            block.generate(single_dataset)

        error = exc_info.value
        assert hasattr(error, "target_count")
        assert hasattr(error, "actual_count")
        assert hasattr(error, "max_retries")
        assert error.target_count == 5
        assert error.actual_count == 0
        assert error.max_retries == 3

    def test_different_target_counts_per_sample(self, sample_dataset):
        """Test retry logic with runtime n parameter override."""
        with patch(
            "sdg_hub.core.blocks.llm.client_manager.completion"
        ) as mock_completion:
            # Return 1 parseable response per call
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[
                0
            ].message.content = "<answer>Single response</answer>"
            mock_completion.return_value = mock_response

            block = LLMChatWithParsingRetryBlock(
                block_name="test_override_n",
                input_cols="messages",
                output_cols="answer",
                model="openai/gpt-4",
                start_tags=["<answer>"],
                end_tags=["</answer>"],
                n=1,  # Default to 1
                parsing_max_retries=2,
            )

            # Override n to 2 at runtime
            result = block.generate(sample_dataset, n=2)

            # Should successfully get 2 responses per sample = 4 total
            assert len(result) == 4
            # Should have called LLM twice per sample to get 2 responses each
            assert mock_completion.call_count == 4


class TestLLMChatWithParsingRetryBlockEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_dataset(self, mock_litellm_completion):
        """Test handling of empty datasets."""
        block = LLMChatWithParsingRetryBlock(
            block_name="test_empty",
            input_cols="messages",
            output_cols="answer",
            model="openai/gpt-4",
            start_tags=["<answer>"],
            end_tags=["</answer>"],
        )

        empty_dataset = Dataset.from_dict({"messages": []})
        result = block.generate(empty_dataset)

        assert len(result) == 0
        assert mock_litellm_completion.call_count == 0

    def test_llm_generation_error_handling(self, sample_dataset):
        """Test handling of LLM generation errors."""
        with patch(
            "sdg_hub.core.blocks.llm.client_manager.completion"
        ) as mock_completion:
            # First call raises exception, continue to next attempt
            mock_completion.side_effect = [
                Exception("Network error"),
                Exception("Another error"),
                Exception("Final error"),
            ]

            block = LLMChatWithParsingRetryBlock(
                block_name="test_llm_error",
                input_cols="messages",
                output_cols="answer",
                model="openai/gpt-4",
                start_tags=["<answer>"],
                end_tags=["</answer>"],
                parsing_max_retries=3,
            )

            single_dataset = Dataset.from_dict(
                {"messages": [sample_dataset["messages"][0]]}
            )

            # Should eventually raise MaxRetriesExceededError after exhausting attempts
            with pytest.raises(MaxRetriesExceededError):
                block.generate(single_dataset)

    def test_mixed_success_failure_across_attempts(self, sample_dataset):
        """Test mixed success/failure scenarios across retry attempts."""
        with patch(
            "sdg_hub.core.blocks.llm.client_manager.completion"
        ) as mock_completion:
            # Simulate pattern: error, success, error, success
            mock_response_good = MagicMock()
            mock_response_good.choices = [MagicMock()]
            mock_response_good.choices[0].message.content = "<answer>Success</answer>"

            mock_completion.side_effect = [
                Exception("First error"),
                mock_response_good,
                Exception("Second error"),
                mock_response_good,
            ]

            block = LLMChatWithParsingRetryBlock(
                block_name="test_mixed",
                input_cols="messages",
                output_cols="answer",
                model="openai/gpt-4",
                start_tags=["<answer>"],
                end_tags=["</answer>"],
                parsing_max_retries=4,
            )

            result = block.generate(sample_dataset)

            # Should get 1 successful response per sample = 2 total
            assert len(result) == 2
            assert all(row["answer"] == "Success" for row in result)

    def test_internal_block_validation(self, mock_litellm_completion):
        """Test validation of internal blocks."""
        block = LLMChatWithParsingRetryBlock(
            block_name="test_validation",
            input_cols="messages",
            output_cols="answer",
            model="openai/gpt-4",
            start_tags=["<answer>"],
            end_tags=["</answer>"],
        )

        # Valid dataset should pass validation
        valid_dataset = Dataset.from_dict(
            {"messages": [[{"role": "user", "content": "test"}]]}
        )

        # Should not raise exception
        block._validate_custom(valid_dataset)

        # Invalid dataset should fail validation
        invalid_dataset = Dataset.from_dict({"wrong_column": ["test"]})

        with pytest.raises(ValueError, match="Required input column"):
            block._validate_custom(invalid_dataset)

    def test_get_internal_blocks_info(self, mock_litellm_completion):
        """Test getting information about internal blocks."""
        block = LLMChatWithParsingRetryBlock(
            block_name="test_info",
            input_cols="messages",
            output_cols="answer",
            model="openai/gpt-4",
            start_tags=["<answer>"],
            end_tags=["</answer>"],
        )

        info = block.get_internal_blocks_info()

        assert "llm_chat" in info
        assert "text_parser" in info
        assert info["llm_chat"] is not None
        assert info["text_parser"] is not None

    def test_repr_string(self, mock_litellm_completion):
        """Test string representation of the block."""
        block = LLMChatWithParsingRetryBlock(
            block_name="test_repr",
            input_cols="messages",
            output_cols="answer",
            model="openai/gpt-4",
            start_tags=["<answer>"],
            end_tags=["</answer>"],
            parsing_max_retries=5,
        )

        repr_str = repr(block)
        assert "LLMChatWithParsingRetryBlock" in repr_str
        assert "test_repr" in repr_str
        assert "openai/gpt-4" in repr_str
        assert "parsing_max_retries=5" in repr_str

    def test_client_manager_reinitialization(self, mock_litellm_completion):
        """Test reinitializing client manager after model config changes."""
        block = LLMChatWithParsingRetryBlock(
            block_name="test_reinit",
            input_cols="messages",
            output_cols="answer",
            model="openai/gpt-4",
            start_tags=["<answer>"],
            end_tags=["</answer>"],
        )

        # Change model configuration
        block.llm_params["model"] = "anthropic/claude-3-sonnet-20240229"
        block.llm_params["api_key"] = "new-api-key"

        # Reinitialize client manager
        block._reinitialize_client_manager()

        # Verify internal LLM chat block was updated
        assert block.llm_chat.model == "anthropic/claude-3-sonnet-20240229"
        assert block.llm_chat.api_key == "new-api-key"

    def test_regex_parsing_configuration(self, mock_litellm_completion, sample_dataset):
        """Test regex-based parsing configuration and execution."""
        # Mock JSON-like response
        mock_litellm_completion.return_value.choices[
            0
        ].message.content = 'Here is the result: "answer": "42" and more text'

        block = LLMChatWithParsingRetryBlock(
            block_name="test_regex",
            input_cols="messages",
            output_cols="result",
            model="openai/gpt-4",
            parsing_pattern=r'"answer":\s*"([^"]*)"',
            parsing_max_retries=2,
        )

        result = block.generate(sample_dataset)

        assert len(result) == 2
        assert all(row["result"] == "42" for row in result)

    def test_async_mode_configuration(self, mock_litellm_completion):
        """Test async mode configuration passed to internal blocks."""
        block = LLMChatWithParsingRetryBlock(
            block_name="test_async",
            input_cols="messages",
            output_cols="answer",
            model="openai/gpt-4",
            start_tags=["<answer>"],
            end_tags=["</answer>"],
            async_mode=True,
        )

        # Verify async mode is passed to internal LLM block
        assert block.llm_chat.async_mode is True
        assert block.llm_params["async_mode"] is True


class TestLLMChatWithParsingRetryBlockRegistration:
    """Test block registration."""

    def test_block_registered(self):
        """Test that LLMChatWithParsingRetryBlock is properly registered."""
        from sdg_hub import BlockRegistry

        assert "LLMChatWithParsingRetryBlock" in BlockRegistry._metadata
        assert (
            BlockRegistry._metadata["LLMChatWithParsingRetryBlock"].block_class
            == LLMChatWithParsingRetryBlock
        )


class TestLLMChatWithParsingRetryBlockIntegration:
    """Integration tests with real internal block behavior."""

    def test_full_pipeline_integration(self, mock_litellm_completion, sample_dataset):
        """Test full pipeline integration between LLM and parser blocks."""
        # Configure complex response that tests both blocks
        mock_litellm_completion.return_value.choices[0].message.content = (
            "Here's my analysis:\n"
            "<explanation>This is a detailed explanation of the problem.</explanation>\n"
            "<answer>The final answer is 42.</answer>\n"
            "Additional text that should be ignored."
        )

        block = LLMChatWithParsingRetryBlock(
            block_name="test_integration",
            input_cols="messages",
            output_cols=["explanation", "answer"],
            model="openai/gpt-4",
            api_key="test-key",
            start_tags=["<explanation>", "<answer>"],
            end_tags=["</explanation>", "</answer>"],
            temperature=0.7,
            max_tokens=200,
            parsing_max_retries=3,
        )

        result = block.generate(sample_dataset)

        # Verify complete pipeline works
        assert len(result) == 2
        for row in result:
            assert (
                row["explanation"] == "This is a detailed explanation of the problem."
            )
            assert row["answer"] == "The final answer is 42."
            # Original message data should be preserved
            assert "messages" in row

        # Verify LLM was called with correct parameters
        call_kwargs = mock_litellm_completion.call_args[1]
        assert call_kwargs["temperature"] == 0.7
        assert call_kwargs["max_tokens"] == 200

    def test_cleanup_tags_integration(self, mock_litellm_completion, sample_dataset):
        """Test integration with parser cleanup tags using regex parsing."""
        # Use regex parsing since cleanup tags only work with regex, not tag parsing
        mock_litellm_completion.return_value.choices[
            0
        ].message.content = "Answer: This has <br>line breaks</br> to clean"

        block = LLMChatWithParsingRetryBlock(
            block_name="test_cleanup",
            input_cols="messages",
            output_cols="clean_answer",
            model="openai/gpt-4",
            api_key="test-key",
            parsing_pattern=r"Answer: (.*?)(?:\n|$)",
            parser_cleanup_tags=["<br>", "</br>"],
        )

        result = block.generate(sample_dataset)

        assert len(result) == 2
        # The cleanup should remove <br> and </br> tags from regex parsing
        assert all(
            row["clean_answer"] == "This has line breaks to clean" for row in result
        )

    def test_error_propagation_from_internal_blocks(self, sample_dataset):
        """Test that errors from internal blocks are properly propagated."""
        with patch(
            "sdg_hub.core.blocks.llm.client_manager.completion"
        ) as mock_completion:
            # Make LLM block raise a specific error
            from sdg_hub.core.blocks.llm.error_handler import AuthenticationError

            mock_completion.side_effect = AuthenticationError(
                "Invalid API key", llm_provider="openai", model="gpt-4"
            )

            block = LLMChatWithParsingRetryBlock(
                block_name="test_error_prop",
                input_cols="messages",
                output_cols="answer",
                model="openai/gpt-4",
                start_tags=["<answer>"],
                end_tags=["</answer>"],
            )

            single_dataset = Dataset.from_dict(
                {"messages": [sample_dataset["messages"][0]]}
            )

            # Error should propagate through and eventually cause MaxRetriesExceededError
            with pytest.raises(MaxRetriesExceededError):
                block.generate(single_dataset)
