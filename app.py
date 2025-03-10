from flask import Flask, request, render_template, redirect, url_for, flash
import pandas as pd
import os
import smtplib

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for flashing messages

UPLOAD_FOLDER = 'test_data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            # Read CSV and validate columns
            df = pd.read_csv(filepath)
            expected_columns = {'Question', 'Correct Answers', 'Player', 'Correct / Incorrect'}
            if not expected_columns.issubset(set(df.columns)):
                return f"Invalid file format. Expected columns: {expected_columns}"

            players = df['Player'].unique().tolist()
            return render_template("select_player.html", players=players, filepath=file.filename)

    return render_template("upload.html")

@app.route("/analyze", methods=["POST"])
def analyze_results():
    player_name = request.form["player"]
    filepath = os.path.join(UPLOAD_FOLDER, request.form["filepath"])

    df = pd.read_csv(filepath)
    student_data = df[df["Player"] == player_name]

    # Get correct questions along with their correct answers
    correct_rows = student_data[student_data["Correct / Incorrect"] == "Correct"]
    correct_answers = [
        {"question": row["Question"], "correct_answer": row["Correct Answers"]}
        for _, row in correct_rows.iterrows()
    ]

    # Get incorrect questions along with their correct answers
    incorrect_rows = student_data[student_data["Correct / Incorrect"] == "Incorrect"]
    incorrect_answers = [
        {"question": row["Question"], "correct_answer": row["Correct Answers"]}
        for _, row in incorrect_rows.iterrows()
    ]

    # Calculate percentage and grade
    total_questions = len(correct_answers) + len(incorrect_answers)
    correct_percentage = (len(correct_answers) / total_questions) * 100 if total_questions > 0 else 0

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

    return render_template(
        "result.html",
        player=player_name,
        correct=correct_answers,
        incorrect=incorrect_answers,
        percentage=correct_percentage,
        grade=grade
    )

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
        server.login(sender_email, "vphkegrbwhpntqeo")  # Use App Passwords
        server.sendmail(sender_email, receiver_email, email_text)
        server.quit()

        # Redirect to confirmation page after successful email
        return redirect(url_for("email_confirmation", receiver_email=receiver_email))

    except Exception as e:
        flash(f"Error sending email: {e}", "danger")
        return redirect(url_for("upload_file"))

@app.route("/email_confirmation")
def email_confirmation():
    receiver_email = request.args.get("receiver_email", "No email provided")
    return render_template("confirmation.html", receiver_email=receiver_email)

if __name__ == "__main__":
    app.run(debug=True)
