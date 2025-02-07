import openai  # Ensure you install OpenAI's package: pip install openai
from flask import Flask, request, render_template
import pandas as pd
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'test_data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Replace with your OpenAI API Key
OPENAI_API_KEY = "your_openai_api_key"

def get_explanation(question):
    """Fetches an explanation for a given question using OpenAI's API."""
    openai.api_key = OPENAI_API_KEY
    
    prompt = f"Explain why the following question is commonly answered incorrectly and provide a simple explanation: {question}"
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an educational assistant providing clear explanations."},
                  {"role": "user", "content": prompt}],
        max_tokens=100
    )
    
    return response["choices"][0]["message"]["content"].strip()

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            df = pd.read_csv(filepath)
            expected_columns = {"Player", "Question", "Correct Answers", "Correct", "Incorrect"}
            if not expected_columns.issubset(df.columns):
                return "Invalid file format. Expected columns: 'player', 'Question', 'Correct Answers', 'Correct', and 'Incorrect'.", 400

            players = df["Player"].unique().tolist()
            return render_template("select_player.html", players=players, filepath=file.filename)

    return render_template("upload.html")

@app.route("/analyze", methods=["POST"])
def analyze_results():
    player_name = request.form.get("player")
    filepath = request.form.get("filepath")

    print(f"DEBUG: Player selected: {player_name}")
    print(f"DEBUG: Filepath received: {filepath}")

    if not player_name or not filepath:
        return "Error: Missing player selection or file path.", 400  # More graceful error message

    filepath = os.path.join(UPLOAD_FOLDER, filepath)

    if not os.path.exists(filepath):
        return "Error: File not found on the server.", 400

    df = pd.read_csv(filepath)
    student_data = df[df["player"] == player_name]

    correct_questions = student_data[student_data["Correct"] == 1]["Question"].unique().tolist()

    incorrect_questions = []
    for _, row in student_data[student_data["Incorrect"] == 1].iterrows():
        question = row["Question"]
        correct_answer = row["Correct Answers"]
        explanation = get_explanation(question)  # Fetch explanation from GPT
        incorrect_questions.append({"Question": question, "Correct Answer": correct_answer, "Explanation": explanation})

    return render_template("results.html", player=player_name, correct=correct_questions, incorrect=incorrect_questions)

if __name__ == "__main__":
    app.run(debug=True)
