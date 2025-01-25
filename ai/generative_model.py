import openai
import os

def init_openai():
    """
    Initializes the OpenAI SDK by reading the API key from the environment variable.
    Raises ValueError if the key is missing.
    """
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    if not openai.api_key:
        raise ValueError(
            "Missing OPENAI_API_KEY environment variable. Please set it before running the app."
        )

def call_openai_model(
    prompt: str,
    max_tokens: int = 150,
    temperature: float = 0.7,
    model: str = "gpt-3.5-turbo"
) -> str:
    """
    Calls an OpenAI model (specified by 'model') with the given prompt.
    Returns the text generated by the model.
    """
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        # Extract the assistant's text from the response
        return response.choices[0].message["content"].strip()
    except Exception as e:
        raise RuntimeError(f"OpenAI API call failed: {str(e)}")
