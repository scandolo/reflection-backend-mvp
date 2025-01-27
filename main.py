from flask import Flask, render_template, request, jsonify, session
import sys
from ai.analyzer import analyze_text
from ai.question_generation import generate_question
from utils.data_utils import (
    load_session_data,
    save_session_data,
    append_training_data
)
from ai.generative_model import init_openai

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session handling

# Initialize OpenAI when the app starts
init_openai()

@app.route('/')
def home():
    # Initialize or reset session data for new visits
    if 'session_id' not in session:
        session['session_id'] = str(hash(str(request.remote_addr) + str(request.user_agent)))
        # Load or initialize session data
        session_data = load_session_data()
        session_data["interactions"] = []  # Reset interactions for new session
        save_session_data(session_data)

    return render_template('index.html')

@app.route('/generate_question', methods=['POST'])
def get_reflection_question():
    data = request.json
    raw_input_text = data.get('text', '')
    is_initial = data.get('is_initial', False)  # To identify if this is the first interaction

    if not raw_input_text:
        return jsonify({"error": "No text provided", "success": False}), 400

    try:
        # Load existing session data
        session_data = load_session_data()

        # Analyze user input
        try:
            current_metrics = analyze_text(raw_input_text)
        except Exception as e:
            print(f"[ERROR] Could not analyze text. Reason: {str(e)}")
            current_metrics = {}

        # Generate question based on current metrics and context
        try:
            question = generate_question(current_metrics, raw_input_text)
        except Exception as e:
            print(f"[ERROR] Could not generate question. Reason: {str(e)}")
            question = "We encountered an error generating a question. Please try again."
            return jsonify({"error": str(e), "success": False}), 500

        # Save interaction
        session_data["interactions"].append({
            "user_text": raw_input_text,
            "metrics": current_metrics,
            "generated_question": question if not is_initial else None
        })
        save_session_data(session_data)

        # Save for training
        append_training_data(raw_input_text, current_metrics)

        return jsonify({
            "question": question,
            "success": True,
            "metrics": current_metrics  # Optionally return metrics if you want to display them
        })

    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/end_session', methods=['POST'])
def end_session():
    try:
        # Save final state of session data
        session_data = load_session_data()
        session_data["completed"] = True
        save_session_data(session_data)

        # Clear flask session
        session.clear()

        return jsonify({"success": True, "message": "Session ended successfully"})
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

def run_cli():
    """
    Original CLI version of the tool - kept for backwards compatibility
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

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        try:
            run_cli()
        except KeyboardInterrupt:
            print("\n[INFO] Exiting the application. Goodbye!")
            sys.exit(0)
    else:
        app.run(debug=True)
