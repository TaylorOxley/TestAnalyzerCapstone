from flask import Flask, render_template, request
import pandas as pd
import smtplib

app = Flask(__name__)

# Store uploaded file path
uploaded_file_path = None

@app.route("/", methods=["GET", "POST"])
def upload_file():
    global uploaded_file_path
    if request.method == "POST":
        file = request.files["file"]
        if file:
            uploaded_file_path = "uploaded_file.csv"
            file.save(uploaded_file_path)

            # Redirect to select player page after file is uploaded
            return select_player()
    return render_template("upload.html")

@app.route("/select_player")
def select_player():
    if not uploaded_file_path:
        return render_template("upload.html")

    df = pd.read_csv(uploaded_file_path)
    players = df["Player"].unique().tolist()  # Extract unique players
    return render_template("select_player.html", players=players)

@app.route("/analyze_results", methods=["GET", "POST"])
def analyze_results():
    if not uploaded_file_path:
        return render_template("upload.html")

    df = pd.read_csv(uploaded_file_path)

    results = {}

    for player in df["Player"].unique():
        player_df = df[df["Player"] == player]

        correct_answers = []
        incorrect_answers = []

        for _, row in player_df.iterrows():
            question = row["Question"]
            correct_answer = row["Correct Answers"]
            is_correct = row["Correct / Incorrect"]

            if is_correct.strip().lower() == "correct":
                correct_answers.append((question, correct_answer))
            elif is_correct.strip().lower() == "incorrect":
                incorrect_answers.append((question, correct_answer))

        total_questions = len(correct_answers) + len(incorrect_answers)
        percentage = (len(correct_answers) / total_questions) * 100 if total_questions > 0 else 0

        # Assign grade based on percentage
        if percentage >= 90:
            grade = "A"
        elif percentage >= 80:
            grade = "B"
        elif percentage >= 70:
            grade = "C"
        elif percentage >= 60:
            grade = "D"
        else:
            grade = "F"

        results[player] = {
            "correct": correct_answers,
            "incorrect": incorrect_answers,
            "percentage": round(percentage, 2),
            "grade": grade
        }

    return render_template("result.html", results=results)



@app.route("/send_email", methods=["POST"])
def send_email():
    sender_email = request.form["sender_email"]
    receiver_email = request.form["receiver_email"]
    subject = request.form["subject"]
    message = request.form["message"]

    email_text = f"Subject: {subject}\n\n{message}"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, "kvnrwezgvridcixy")
        server.sendmail(sender_email, receiver_email, email_text)
        server.quit()
        return render_template("confirmation.html", receiver_email=receiver_email)
    except Exception as e:
        return f"Error sending email: {e}"

if __name__ == "__main__":
    app.run(debug=True)