from ai.generative_model import call_openai_model

def generate_question(current_metrics: dict, user_text: str) -> str:
    """
    Generates a single introspective question based on the current metrics
    and the user's text. Returns the question as a string.
    """

    # Opzionale: se il testo utente è molto lungo, potresti riassumerlo con un LLM
    #   e passare il riassunto. Esempio:
    # if len(user_text) > 500:
    #     user_text = summarize_text(user_text)

    # Decidiamo la tipologia di domanda (es. se anxiety > 7, ecc.)
    question_type = _classify_question_type(current_metrics)

    # Costruiamo il prompt in inglese, rispettando i 5 principi (no contenuti esterni, verità, ecc.)
    prompt = f"""
        You are an AI whose sole purpose is to ask deep, probing questions for self-reflection,
        strictly following these principles:
        1. Raw Reflection: The user's input is unfiltered and authentic.
        2. Truth-Seeking: Prioritize uncovering pure truths over superficial or entertaining content.
        3. Probing Questions: Provide a single, deep question for the user to explore their own mind.
        4. Mental Exploration: Reveal hidden aspects of the mind through introspective questioning.
        5. Independence from External Content: Avoid referencing external facts, examples, or stories.

        User's current metrics:
        - Anxiety: {current_metrics.get('anxiety', 0)}
        - Clarity: {current_metrics.get('clarity', 0)}
        - Motivation: {current_metrics.get('motivation', 0)}
        - SelfAwareness: {current_metrics.get('selfAwareness', 0)}

        Question type (internal hint for you): {question_type}

        User's most recent text:
        \"\"\"{user_text}\"\"\"

        Task: Generate ONE single question (no additional explanation, no external references).
        Output ONLY the question in plain text.
    """

    try:
        # We can use a more capable model for question generation, for now just testing:
        response = call_openai_model(
            prompt=prompt,
            #max_tokens=100,
            #temperature=0.7,
           model="gpt-3.5-turbo"
        )
    except Exception as e:
        raise RuntimeError(f"LLM call failed in generate_question: {str(e)}")

    # In caso il modello restituisca più di una frase, estrapoliamo la prima?
    # Oppure ci fidiamo che risponda con una sola?
    # Se serve, si può implementare una logica di post-processing qui.
    question = response.strip()
    return question

def _classify_question_type(current_metrics: dict) -> str:
    """
    Example logic: Returns a short string describing the style of question
    based on the metrics. In an MVP, it's just a set of if/else conditions.
    """
    anxiety = current_metrics.get("anxiety", 0)
    clarity = current_metrics.get("clarity", 0)

    if anxiety > 7:
        return "Focus on reducing internal tension"
    elif clarity < 3:
        return "Focus on clarifying confusion"
    else:
        return "General deep introspection"
