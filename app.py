from flask import Flask, request, render_template, send_file
import pandas as pd
import os
from flask_mail import Mail, Message

app = Flask(__name__)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # Change this
app.config['MAIL_PASSWORD'] = 'your_password'         # Change this
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

mail = Mail(app)

UPLOAD_FOLDER = 'test_data'
REPORT_FOLDER = 'reports'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            missed_questions = analyze_file(filepath)

            return render_template("result.html", missed_questions=missed_questions)
    return render_template("upload.html")

def analyze_file(filepath):
    df = pd.read_excel(filepath)
    
    if 'Question' not in df.columns or 'Correct' not in df.columns:
        return "Invalid file format. Columns 'Question' and 'Correct' expected."

    missed = df[df["Correct"] == 0]["Question"].value_counts()
    return missed.to_dict()

@app.route("/send_report", methods=["POST"])
def send_report():
    email = request.form["email"]
    missed_questions = request.form["missed_questions"]
    
    # Generate a report
    report_path = os.path.join(REPORT_FOLDER, f"report_{email}.txt")
    with open(report_path, "w") as f:
        f.write("Missed Questions Report\n\n")
        for question, count in eval(missed_questions).items():
            f.write(f"{question} - Missed {count} times\n")
            f.write(f"Explanation: [Provide explanation here]\n\n")
    
    # Send email
    msg = Message("Your Missed Questions Report", recipients=[email])
    msg.body = "Please find your missed questions report attached."
    with app.open_resource(report_path) as fp:
        msg.attach("Missed_Questions_Report.txt", "text/plain", fp.read())

    mail.send(msg)
    return "Report sent successfully!"

if __name__ == "__main__":
    app.run(debug=True)

