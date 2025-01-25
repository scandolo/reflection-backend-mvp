import sys
from ai.analyzer import analyze_text
from ai.question_generation import generate_question
from utils.data_utils import (
    load_session_data,
    save_session_data,
    append_training_data
)
from ai.generative_model import init_openai


def read_multiline_input(prompt: str) -> str:
    """
    Reads multiple lines from the user until they press ENTER on an empty line,
    or type '/exit' to end the entire session immediately.
    Returns the full string of user input (with line breaks).
    """
    print(prompt)
    print("(Press ENTER on an empty line to finish. Type '/exit' to quit immediately.)")
    lines = []
    while True:
        line = input()
        # If user types '/exit', we end the entire session
        if line.strip().lower() == "/exit":
            return "/exit"
        # If user pressed ENTER on an empty line, stop reading
        if line.strip() == "":
            break
        lines.append(line)
    # Join everything with line breaks
    return "\n".join(lines)


def run_cli():
    """
    Main loop of the Reflective MVP Tool (Terminal Version).
    Uses multiline input and no repeated (y/n) prompt.
    """
    # Initialize OpenAI at the very start
    init_openai()

    print("Welcome to the Reflective MVP Tool (Terminal Version).")

    # Load or initialize session data
    session_data = load_session_data()

    # First, ask the user about what brings them here
    raw_input_text = read_multiline_input("\nWhat brings you here today?")
    if raw_input_text.strip().lower() == "/exit":
        print("Exiting the session.")
        sys.exit(0)

    # Analyze and save initial user input
    try:
        current_metrics = analyze_text(raw_input_text)
    except Exception as e:
        print(f"[ERROR] Could not analyze text. Reason: {str(e)}")
        current_metrics = {}

    session_data["interactions"].append({
        "user_text": raw_input_text,
        "metrics": current_metrics,
        "generated_question": None
    })
    save_session_data(session_data)

    while True:
        # Generate a question based on current metrics
        try:
            question = generate_question(current_metrics, raw_input_text)
        except Exception as e:
            print(f"[ERROR] Could not generate a question. Reason: {str(e)}")
            question = "We encountered an error generating a question. Try again."
        print("\nQuestion for you:\n", question)

        # Read multiline user reflection
        user_answer = read_multiline_input("\nYour reflection:")
        if user_answer.strip().lower() == "/exit":
            print("Exiting the session.")
            break
        if not user_answer.strip():
            # If user pressed ENTER on an empty line right away => done
            print("No reflection provided. Ending session.")
            break

        # Analyze the new reflection
        try:
            current_metrics = analyze_text(user_answer)
        except Exception as e:
            print(f"[ERROR] Could not analyze text. Reason: {str(e)}")
            current_metrics = {}

        # Save interaction (question, user answer, new metrics)
        session_data["interactions"].append({
            "user_text": user_answer,
            "metrics": current_metrics,
            "generated_question": question
        })
        save_session_data(session_data)

        # Append training data for potential model finetuning
        append_training_data(user_answer, current_metrics)

        # Update raw_input_text for next question generation
        raw_input_text = user_answer

    print("Thank you for using the Reflective MVP Tool. Goodbye!")


if __name__ == "__main__":
    try:
        run_cli()
    except KeyboardInterrupt:
        print("\n[INFO] Exiting the application. Goodbye!")
        sys.exit(0)
