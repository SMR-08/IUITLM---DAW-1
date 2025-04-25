import json
from typing import Dict, Any, List

class AIResponseParsingError(Exception):
    """Custom exception for errors during AI response parsing."""
    def __init__(self, message, raw_text=None, cleaned_text=None, original_error=None):
        super().__init__(message)
        self.raw_text = raw_text
        self.cleaned_text = cleaned_text
        self.original_error = original_error

def parse_gemini_chat_response(raw_text: str) -> Dict[str, Any]:
    """
    Parses the raw text response from the Gemini chat model,
    attempting to extract the JSON object while handling potential formatting issues.

    Args:
        raw_text: The raw string received directly from the AI response.text.

    Returns:
        A dictionary representing the parsed JSON object.

    Raises:
        AIResponseParsingError: If the text cannot be parsed into a valid JSON
                                object according to the expected structure.
    """
    if not raw_text:
        raise AIResponseParsingError("Empty response received from AI.", raw_text=raw_text)

    # Step 1: Attempt to clean known markdown formatting (like ```json)
    cleaned_text = raw_text.strip()
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[len("```json"):].strip()
    if cleaned_text.endswith("```"):
        # This is safe even if the opening ```json wasn't present,
        # as long as we strip from the end.
        cleaned_text = cleaned_text[:-len("```")].strip()

    # Step 2: Add more robust cleaning if needed (e.g., remove trailing text)
    # This part could be enhanced if you observe specific patterns of failure.
    # For now, the markdown strip is often sufficient for models *trying* to comply.

    # Step 3: Attempt to parse the cleaned text as JSON
    try:
        data = json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        # If JSON decoding fails, raise a specific parsing error
        raise AIResponseParsingError(
            "Failed to decode JSON.",
            raw_text=raw_text,
            cleaned_text=cleaned_text,
            original_error=e # Include the original JSON error for debugging
        )
    except Exception as e:
         # Catch any other unexpected errors during basic parsing
         raise AIResponseParsingError(
            f"Unexpected error during JSON parsing: {e}",
            raw_text=raw_text,
            cleaned_text=cleaned_text,
            original_error=e
         )


    # Step 4: Basic validation of the expected JSON structure
    # Ensure the top-level keys are present (optional but good practice)
    expected_keys = ["chat_reply", "mermaid_code", "suggested_responses"]
    if not all(key in data for key in expected_keys):
        # You could make this more specific, e.g., check types, but simple key presence is a start
        raise AIResponseParsingError(
            f"Parsed JSON is missing expected keys ({', '.join(expected_keys)}).",
            raw_text=raw_text,
            cleaned_text=cleaned_text,
            original_error="Structure validation failed"
        )

    # Step 5: Return the parsed data
    return data