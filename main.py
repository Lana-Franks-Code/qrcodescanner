#PYTHON
# Python code to update attendance and calculate total attendance for a specific date

import requests
from datetime import datetime, date
import cv2
from pyzbar.pyzbar import decode
import time
import threading
import csv
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Global variables
scanning_active = False
message = ""
SHEET_API_ENDPOINT = "https://api.sheety.co/26113d198eae07110dcfedb4c19c8dd1/attendance/sheet1"
CSV_FILE = "participants.csv"

# Function to fetch the total attendance for the current date
def fetch_total_attendance_for_today():
    try:
        today = date.today().strftime("%Y-%m-%d")
        response = requests.get(SHEET_API_ENDPOINT)
        response.raise_for_status()
        data = response.json()

        if not data:  # Check if data is empty
            return 0

        total_attendance_today = sum(1 for entry in data['sheet1'] if entry['date'] == today)
        return total_attendance_today
    except requests.exceptions.RequestException as e:
        print(f"Error fetching total attendance: {e}")
        return 0

# Function to read participant details from the CSV file
def read_participant_details():
    participant_details = {}
    with open(CSV_FILE, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader)  # Skip the header row
        for row in reader:
            name, region = row
            participant_details[name] = region
    return participant_details

# Global variable to store participant details
participant_details = read_participant_details()

# Function to check and update attendance in Google Sheet
def update_attendance(name):
    global participant_details
    try:
        response = requests.get(SHEET_API_ENDPOINT)
        response.raise_for_status()
        data = response.json()

        for entry in data['sheet1']:
            if entry['fullName'] == name:
                return "Already Logged"

        if name in participant_details:
            region = participant_details[name]
            new_entry = {
                "sheet1": {
                    "fullName": name,
                    "region": region,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "time": datetime.now().strftime("%H:%M:%S")
                }
            }
            response = requests.post(SHEET_API_ENDPOINT, json=new_entry)
            response.raise_for_status()

            return f"Welcome {name}"
        else:
            return f"Participant {name} not found in the participant details."
    except requests.exceptions.RequestException as e:
        print(f"Error updating attendance: {e}")
        return None

# Function to continuously scan for QR codes
def scan_qr():
    global scanning_active, message
    cap = cv2.VideoCapture(0)
    while scanning_active:
        ret, frame = cap.read()
        decoded_objects = decode(frame)
        if decoded_objects:
            name = decoded_objects[0].data.decode('utf-8')
            message = update_attendance(name)
            print(f"Decoded QR code: {name}")
            print(f"Attendance update message: {message}")
            time.sleep(2)  # Delay between scans
        else:
            message = "No QR code detected"
            print(message)
        time.sleep(0.1)  # Optional: Add a small delay to reduce CPU usage

# Flask routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start_scan")
def start_scan():
    global scanning_active
    scanning_active = True
    thread = threading.Thread(target=scan_qr)
    thread.daemon = True
    thread.start()
    return "Scanning started"

@app.route("/stop_scan")
def stop_scan():
    global scanning_active
    scanning_active = False
    return "Scanning stopped"

@app.route("/get_message")
def get_message():
    global message
    return message

@app.route("/get_total_attendance")
def get_total_attendance():
    total_attendance = fetch_total_attendance_for_today()
    return jsonify({"totalAttendance": total_attendance})

if __name__ == "__main__":
    app.run(debug=True)
