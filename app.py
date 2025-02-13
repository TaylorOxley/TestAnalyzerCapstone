from flask import Flask, request, render_template
import pandas as pd
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'test_data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            # Read CSV and validate new column order
            df = pd.read_csv(filepath)
            if 'Question' not in df.columns or 'Player' not in df.columns or 'Correct / Incorrect' not in df.columns:
                return "Invalid file format. Expected columns: 'Question', 'Player', 'Correct / Incorrect'."

            players = df['Player'].unique().tolist()
            return render_template("select_player.html", players=players, filepath=file.filename)

    return render_template("upload.html")

@app.route("/analyze", methods=["POST"])
def analyze_results():
    player_name = request.form["player"]
    filepath = os.path.join(UPLOAD_FOLDER, request.form["filepath"])

    df = pd.read_csv(filepath)
    student_data = df[df["Player"] == player_name]

    # Get lists of correct and incorrect questions
    correct_answers = student_data[student_data["Correct / Incorrect"] == "Correct"]["Question"].unique().tolist()
    incorrect_answers = student_data[student_data["Correct / Incorrect"] == "Incorrect"]["Question"].unique().tolist()

    # Calculate percentage
    total_questions = len(correct_answers) + len(incorrect_answers)
    correct_percentage = (len(correct_answers) / total_questions) * 100 if total_questions > 0 else 0

    # Assign grade based on percentage
    if correct_percentage >= 90:
        grade = "A"
    elif correct_percentage >= 80:
        grade = "B"
    elif correct_percentage >= 70:
        grade = "C"
    elif correct_percentage >= 60:
        grade = "D"
    else:
        grade = "F"

    return render_template("result.html", player=player_name, correct=correct_answers, 
                           incorrect=incorrect_answers, percentage=correct_percentage, grade=grade)


if __name__ == "__main__":
    app.run(debug=True)

    
