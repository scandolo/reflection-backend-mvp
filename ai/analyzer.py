import json
from ai.generative_model import call_openai_model

def analyze_text(user_text: str) -> dict:
    """
    Uses a cheap LLM (e.g. 4o-mini) to extract emotional/cognitive metrics
    from the user_text. Returns a dictionary like:
    {
      "anxiety": 7,
      "clarity": 3,
      "motivation": 5,
      "selfAwareness": 4
    }
    Range: 0-10
    """

    # Base prompt for state analysis:
    prompt = f"""
        You are a specialized model for analyzing the user's text and extracting key mental metrics.
        Please read the following text and assign the following metrics on a scale from 0 to 10:

        - Anxiety
        - Clarity
        - Motivation
        - SelfAwareness

        Return ONLY a JSON object in the following format (no additional text or explanation):
        {{
        "anxiety": number,
        "clarity": number,
        "motivation": number,
        "selfAwareness": number
        }}

        User text:
        \"\"\"{user_text}\"\"\"

        Now produce your JSON response:
        """

    try:
        # We can use a cheaper or faster model for analysis if desired:
       response = call_openai_model(
            prompt=prompt,
            max_tokens=100,
            temperature=0.0,
            model="gpt-3.5-turbo"  # or your preferred cheaper model
        )
    except Exception as e:
        raise RuntimeError(f"LLM call failed in analyze_text: {str(e)}")

    # Parse JSON received in response from the LLM
    parsed_metrics = _parse_json_metrics(response)
    return parsed_metrics


#defining the "_parse_json_metrics" function, that is called inside of the "analyze_text" function
def _parse_json_metrics(response_text: str) -> dict:
    """
    Safely parse the JSON string returned by the LLM.
    If there's any formatting error, raise an exception.
    """
    try:
        data = json.loads(response_text.strip())
    except json.JSONDecodeError as e:
        # in the case where the model returned a response that has the wrong format
        raise ValueError(f"Invalid JSON format from analyzer: {response_text}")

    # Minimal checks in the JSON keys
    required_keys = ["anxiety", "clarity", "motivation", "selfAwareness"]
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing key '{key}' in LLM response: {data}")
        # Check if Values for each key are numbers
        if not isinstance(data[key], (int, float)):
            raise ValueError(f"Metric '{key}' must be a number. Got: {data[key]}")

    return data
