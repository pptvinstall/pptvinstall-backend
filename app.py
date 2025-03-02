from flask import Flask, request, jsonify
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Database Setup
def init_db():
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT,
                    phone TEXT,
                    service TEXT,
                    appointment_time TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Function to send email
SMTP_SERVER = "smtp.gmail.com"  # Change if using another provider
SMTP_PORT = 587
EMAIL_SENDER = "pptvinstall@gmail.com"  # Change to your actual email
EMAIL_PASSWORD = "qpnp bplj rmxx rqkg"  # Store securely!

def send_email(customer_email, customer_name, service, appointment_time):
    subject = "Booking Confirmation - Picture Perfect TV Install"
    body = f"Hello {customer_name},\n\nYour booking for {service} on {appointment_time} has been confirmed.\n\nThank you!\nPicture Perfect TV Install"
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = customer_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, customer_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print("Error sending email:", str(e))

# Homepage Route
@app.route('/')
def home():
    return "Welcome to Picture Perfect TV Install API! Everything is running smoothly."

# API Endpoint to book an appointment
@app.route('/book', methods=['POST'])
def book_appointment():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    service = data.get('service')
    appointment_time = data.get('appointment_time')
    
    if not all([name, email, phone, service, appointment_time]):
        return jsonify({"error": "Missing required fields"}), 400
    
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute("INSERT INTO bookings (name, email, phone, service, appointment_time) VALUES (?, ?, ?, ?, ?)",
              (name, email, phone, service, appointment_time))
    conn.commit()
    conn.close()
    
    send_email(email, name, service, appointment_time)
    
    return jsonify({"message": "Booking confirmed! Email sent."}), 200

# Function to auto-delete the earliest booking if database is full
@app.route('/cleanup', methods=['POST'])
def cleanup_appointments():
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM bookings")
    count = c.fetchone()[0]
    
    MAX_BOOKINGS = 100  # Adjust based on needs
    if count >= MAX_BOOKINGS:
        c.execute("DELETE FROM bookings WHERE id = (SELECT MIN(id) FROM bookings)")
        conn.commit()
        print("Oldest booking removed due to capacity limit.")
    
    conn.close()
    return jsonify({"message": "Cleanup check completed."}), 200

if __name__ == '__main__':
    app.run(debug=True)
