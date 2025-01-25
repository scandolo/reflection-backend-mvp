import os
import json

SESSION_DATA_FILE = os.path.join("data", "session_data.json")
TRAINING_DATA_FILE = os.path.join("data", "training_data.json")

def load_session_data() -> dict:
    """
    Load the session data from the JSON file.
    If it doesn't exist, returns an initialized dict structure.
    """
    if not os.path.exists(SESSION_DATA_FILE):
        return {"interactions": []}

    with open(SESSION_DATA_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {"interactions": []}
    return data

def save_session_data(data: dict) -> None:
    """
    Save the session data to the JSON file.
    """
    os.makedirs("data", exist_ok=True)
    with open(SESSION_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def append_training_data(user_text: str, metrics: dict):
    """
    Appends a new record to the training_data.json file.
    This data can be used later to train a specialized model for metric extraction.
    """
    os.makedirs("data", exist_ok=True)
    # Carichiamo i dati esistenti
    if not os.path.exists(TRAINING_DATA_FILE):
        training_data = []
    else:
        with open(TRAINING_DATA_FILE, "r", encoding="utf-8") as f:
            try:
                training_data = json.load(f)
            except json.JSONDecodeError:
                training_data = []

    # Aggiungiamo il nuovo record
    record = {
        "user_text": user_text,
        "metrics": metrics
    }
    training_data.append(record)

    # Salviamo
    with open(TRAINING_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(training_data, f, ensure_ascii=False, indent=2)
