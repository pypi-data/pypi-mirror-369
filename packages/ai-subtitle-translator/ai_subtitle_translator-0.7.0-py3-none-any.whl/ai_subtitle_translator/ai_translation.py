#!/usr/bin/env python3
"""
This module provides a functional, registry-based architecture for translating text
using different LLM providers and prompt templates. It is designed to be reusable,
extensible, and easy to maintain.

Key Components:
- Provider Registry: A dictionary (`TRANSLATION_PROVIDERS`) that maps provider names
  (e.g., "openai") to their corresponding translation functions.
- Prompt Registry: A dictionary (`PROMPT_TEMPLATES`) that maps prompt template names
  (e.g., "selective") to functions that generate the final prompt string.
- Public API: A single function, `translate_batch`, serves as the entry point. It
  dynamically selects the provider and prompt template based on its arguments.

This design avoids inheritance and complex object-oriented patterns in favor of
a more straightforward, data-driven approach.
"""

import os
import time
from collections.abc import Callable

import json_repair
import openai
from google import genai
from openai import OpenAI
from pydantic import BaseModel, Field

DEFAULT_OPENAI_MODEL = "gpt-5-mini"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
DEFAULT_DEEPSEEK_MODEL = "deepseek-chat"


# --- Structured Output Schema for OpenAI ---
def create_translation_response_schema(expected_count: int):
    """
    Create a dynamic Pydantic schema for translation responses.

    Args:
        expected_count: Number of expected translations

    Returns:
        Pydantic model class for the response
    """

    class TranslationResponse(BaseModel):
        # Define exact array length in schema - OpenAI will enforce this
        translations: list[str] = Field(
            min_length=expected_count,
            max_length=expected_count,
            description=f"Exactly {expected_count} translation strings",
        )

    return TranslationResponse


# --- Prompt Template Generation ---


def _create_full_text_prompt(text_lines: list[str], media_info: str) -> str:
    """
    Creates a prompt to translate subtitle lines using array format.

    Args:
        text_lines: A list of subtitle text strings to be translated.
        media_info: A string providing context about the media (e.g., title, year).

    Returns:
        A formatted string to be used as the prompt for the LLM.
    """
    prompt_text = "\n".join([f'"{text}"' for text in text_lines])

    return f"""Translate the following batch of subtitles to Chinese for the media: {media_info}

The input is an array of English subtitle lines, each line corresponding to a single subtitle entry in a larger file.

CRITICAL: Return exactly {len(text_lines)} translations in a JSON array. The input contains {len(text_lines)} lines, so your output must contain exactly {len(text_lines)} strings.

Each output string must correspond to the same position in the input array (i.e., the nth output is the translation of the nth input).

If you cannot confidently translate a line, return an empty string "" at that position.

Use official or widely-accepted Chinese translations for names, terms, or catchphrases if you recognize the media.

Retain any special formatting (e.g., italics, emphasis) from the input.

If a line contains wordplay, rare cultural references, or untranslatable terms, provide a brief note in parentheses after the translation.

If a sentence or phrase is split across multiple lines, translate naturally, even if the split does not perfectly match the original.

Input ({len(text_lines)} lines):
{prompt_text}

Output format:
Return a JSON array of exactly {len(text_lines)} strings, with each string being the translation for the corresponding input line.

Example:
Input: ["Hello world", "How are you?", "I want to go to", "the store today."]
Output: ["你好，世界", "你好吗？", "我今天想", "去商店。"]
"""


def _create_selective_difficulty_prompt(text_lines: list[str], media_info: str) -> str:
    """
    Creates a prompt that asks the AI to selectively translate only difficult
    or complex phrases, slang, or cultural references using array format.

    Args:
        text_lines: A list of subtitle text strings to be analyzed.
        media_info: A string providing context about the media.

    Returns:
        A formatted string to be used as the prompt for the LLM.
    """
    prompt_text = "\n".join([f'"{text}"' for text in text_lines])

    return f"""You are assisting a Chinese audience in watching: {media_info}

You are processing a batch of subtitles from a larger file. The viewer understands basic English.
Your task is to provide brief notes or translations for lines in this batch that contain:
• Uncommon or advanced vocabulary and phrases
• Idioms, slang, or cultural references
• Names of people, organizations, or brands that are well-known in China
• Long or complex sentence structures

For simple lines that are fully understandable, return an empty string.

CRITICAL: Return exactly {len(text_lines)} responses in a JSON array. The input contains {len(text_lines)} lines, so your output must contain exactly {len(text_lines)} strings.

Input ({len(text_lines)} lines):
{prompt_text}

Output format:
Return a JSON array of exactly {len(text_lines)} strings, where each element is either:
- A translation/note for complex lines
- An empty string "" for simple lines that don't need translation

Example:
Input: ["Hello", "I need a subpoena", "How are you?"]
Output: ["", "我需要传票 (subpoena: legal document)", ""]
"""


# --- Provider-Specific Translation Functions ---


def _translate_openai(prompt: str, model: str, expected_count: int) -> list[str]:
    """
    Sends a prompt to the OpenAI API using structured outputs for reliable response format.

    Args:
        prompt: The prompt to send to the model.
        model: The specific OpenAI model to use.
        expected_count: Number of expected translations (required).

    Returns:
        A list of translated strings in the same order as input.
    """

    client = OpenAI()
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            # Use OpenAI's structured outputs with Pydantic schema
            ResponseSchema = create_translation_response_schema(expected_count)

            response = client.responses.parse(
                model=model,
                input=[{"role": "user", "content": prompt}],
                text_format=ResponseSchema,
            )

            parsed_response = response.output_parsed
            if parsed_response:
                print(
                    f"✅ Structured output: received exactly {len(parsed_response.translations)} translations"
                )
                return parsed_response.translations
            else:
                print("⚠️ Failed to parse structured response")
                return []

        except openai.RateLimitError:
            print(f"Rate limited. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            retry_delay *= 2
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                return []
    return []


def _translate_deepseek(prompt: str, model: str) -> list[str]:
    """
    Sends a prompt to the DeepSeek API using the OpenAI-compatible client.

    Args:
        prompt: The prompt to send to the model.
        model: The specific DeepSeek model to use.

    Returns:
        A list of translated strings in the same order as input.
    """
    # DeepSeek uses the OpenAI client
    if not os.environ.get("DEEPSEEK_API_KEY"):
        raise ValueError("DEEPSEEK_API_KEY environment variable is not set.")

    client = OpenAI(
        api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com/v1"
    )
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            response_config = {
                "temperature": 0.0,
                "response_format": {"type": "json_object"},
            }

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                **response_config,
            )
            content = response.choices[0].message.content

            try:
                result = json_repair.loads(content)
                # Handle different response formats
                if isinstance(result, list):
                    return result
                elif isinstance(result, dict) and len(result) == 1:
                    # Single-key dict, extract the value regardless of key name
                    key, value = next(iter(result.items()))
                    if isinstance(value, list):
                        print(f"Extracted array from key '{key}'")
                        return value
                    else:
                        print(
                            f"⚠️ Single-key dict but value is not array: {key}={value}"
                        )
                        return []
                else:
                    print(f"⚠️ Unexpected response format: {result}")
                    return []
            except Exception as e:
                print(f"⚠️ JSON parsing failed: {e}")
                print(f"Response length: {len(content)} characters")
                if len(content) > 10000:
                    print(
                        "⚠️ Very large response detected, consider reducing batch size"
                    )
                return []

        except openai.RateLimitError:
            print(f"Rate limited. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            retry_delay *= 2
        except Exception as e:
            print(f"Error calling DeepSeek API: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                return []
    return []


def _translate_gemini(prompt: str, model: str, expected_count: int) -> list[str]:
    """
    Sends a prompt to the Google Gemini API using the new google-genai client with JSON schema support.

    Args:
        prompt: The prompt to send to the model.
        model: The specific Gemini model to use.
        expected_count: Number of expected translations (required).

    Returns:
        A list of translated strings in the same order as input.
    """
    # The client gets the API key from the environment variable `GEMINI_API_KEY`
    client = genai.Client()
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            # Use JSON schema with Gemini
            TranslationSchema = create_translation_response_schema(expected_count)

            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": TranslationSchema,
                    "temperature": 0.0,
                },
            )

            # Parse the structured response directly
            parsed_response = response.parsed
            if parsed_response:
                # Extract translations from the parsed response object
                translations = parsed_response.translations
                print(
                    f"✅ Structured schema: received exactly {len(translations)} translations"
                )
                return translations
            else:
                print("⚠️ Failed to parse structured response")
                return []

        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                return []
    return []


# --- Registries ---

PROMPT_TEMPLATES: dict[str, Callable] = {
    "full_text": _create_full_text_prompt,
    "selective_difficulty": _create_selective_difficulty_prompt,
}

TRANSLATION_PROVIDERS: dict[str, Callable] = {
    "openai": _translate_openai,
    "gemini": _translate_gemini,
    "deepseek": _translate_deepseek,
}

# --- Helper Functions ---


def _execute_single_translation(
    provider: str,
    prompt: str,
    model: str,
    expected_count: int,
) -> list[str]:
    """
    Execute translation for a single provider.

    Args:
        provider: The provider name to use.
        prompt: The formatted prompt to send.
        model: The model to use.
        expected_count: Number of expected translations.

    Returns:
        List of translation strings.
    """
    provider_function = TRANSLATION_PROVIDERS.get(provider)
    if not provider_function:
        raise ValueError(
            f"Unsupported provider: '{provider}'. Supported: {list(TRANSLATION_PROVIDERS.keys())}"
        )

    if provider in ["openai", "gemini"]:
        # Pass expected_count for structured outputs/JSON schema
        return provider_function(prompt, model, expected_count)
    else:
        # Other providers don't support structured outputs yet
        return provider_function(prompt, model)


def _is_response_valid(translation_array: list[str], expected_length: int) -> bool:
    """
    Check if the translation response has the correct length.

    Args:
        translation_array: The translation result array.
        expected_length: Expected number of translations.

    Returns:
        True if response length matches expected length.
    """
    actual_length = len(translation_array) if translation_array else 0
    return actual_length == expected_length


def _handle_invalid_response(
    translation_array: list[str],
    expected_length: int,
) -> list[str]:
    """
    Handle invalid response by padding or truncating.

    Args:
        translation_array: The translation result array.
        expected_length: Expected number of translations.

    Returns:
        Processed translation array.
    """
    actual_length = len(translation_array) if translation_array else 0

    if actual_length == 0:
        print("⚠️  Empty response, returning empty array")
        return []

    elif actual_length > expected_length:
        print(f"⚠️  Truncating response from {actual_length} to {expected_length}")
        return translation_array[:expected_length]

    else:  # actual_length < expected_length
        print(
            f"⚠️  Padding response from {actual_length} to {expected_length} with empty strings"
        )
        padded_array = translation_array + [""] * (expected_length - actual_length)
        return padded_array


# --- Public API ---


def translate_batch(
    provider: str,
    prompt_template: str,
    text_lines: list[str],
    media_info: str,
    model: str | None = None,
    fallback_provider: str | None = None,
) -> tuple[list[str], dict | None]:
    """
    Translates a batch of subtitle text using array-based approach to avoid index shifting.

    Args:
        provider: The name of the translation provider (e.g., "openai").
        prompt_template: The name of the prompt template to use (e.g., "selective").
        text_lines: The list of subtitle text strings to translate.
        media_info: Contextual information about the media.
        model: The specific model to use (optional).
        fallback_provider: Fallback provider to use if primary fails (optional).

    Returns:
        A tuple of (translated_strings, fallback_info):
        - translated_strings: List of translated strings in the same order as input
        - fallback_info: Dict with fallback usage info or None if no fallback used

    Raises:
        ValueError: If the specified provider or prompt template is not supported.
    """
    # 1. Select the prompt generation function from the registry
    prompt_function = PROMPT_TEMPLATES.get(prompt_template)
    if not prompt_function:
        supported_templates = list(PROMPT_TEMPLATES.keys())
        raise ValueError(
            f"Unsupported prompt template: '{prompt_template}'. "
            f"Supported: {supported_templates}"
        )

    # 2. Select the translation function from the registry
    provider_function = TRANSLATION_PROVIDERS.get(provider)
    if not provider_function:
        raise ValueError(
            f"Unsupported provider: '{provider}'. Supported: {list(TRANSLATION_PROVIDERS.keys())}"
        )

    # 3. Determine the model to use
    if not model:
        if provider == "openai":
            model = DEFAULT_OPENAI_MODEL
        elif provider == "gemini":
            model = DEFAULT_GEMINI_MODEL
        elif provider == "deepseek":
            model = DEFAULT_DEEPSEEK_MODEL

    # 4. Generate the prompt
    prompt = prompt_function(text_lines, media_info)

    # 5. Execute translation with fallback support
    expected_length = len(text_lines)

    # Try primary provider
    print(f"Using provider: {provider}, model: {model}, prompt: {prompt_template}")
    translation_array = _execute_single_translation(
        provider, prompt, model, expected_length
    )

    # Check if response is valid
    if _is_response_valid(translation_array, expected_length):
        print(f"✅ Received expected {expected_length} translations")
        return translation_array, None  # No fallback used

    # Try fallback provider if available and primary failed
    if fallback_provider and fallback_provider != provider:
        received_size = len(translation_array) if translation_array else 0
        print(
            f"⚠️ Primary provider '{provider}' returned incorrect size: expected {expected_length}, got {received_size}. Trying fallback provider '{fallback_provider}'"
        )

        # Determine fallback model - always use provider defaults for reliability
        if fallback_provider == "openai":
            fallback_model = DEFAULT_OPENAI_MODEL
        elif fallback_provider == "gemini":
            fallback_model = DEFAULT_GEMINI_MODEL
        elif fallback_provider == "deepseek":
            fallback_model = DEFAULT_DEEPSEEK_MODEL
        else:
            fallback_model = None  # Shouldn't happen with current validation

        print(f"Using fallback: {fallback_provider}, model: {fallback_model}")
        fallback_translation_array = _execute_single_translation(
            fallback_provider, prompt, fallback_model, expected_length
        )

        # Check if fallback response is valid
        if _is_response_valid(fallback_translation_array, expected_length):
            print(
                f"✅ Fallback provider '{fallback_provider}' succeeded with {expected_length} translations"
            )
            fallback_info = {"provider": fallback_provider, "count": expected_length}
            return fallback_translation_array, fallback_info
        else:
            print(
                f"⚠️ Fallback provider '{fallback_provider}' also failed. Using primary result with padding/truncation."
            )
            # Fall through to use primary result with padding/truncation

    # Handle invalid response using current logic (padding/truncation)
    return _handle_invalid_response(translation_array, expected_length), None
