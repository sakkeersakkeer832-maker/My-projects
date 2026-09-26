from flask import Flask, render_template_string, request, jsonify, send_file
import cv2
import numpy as np
import base64
import openpyxl
import os
from datetime import datetime

app = Flask(__name__)

EXCEL_FILE = "Today attendance.xlsx"
CASCADE_FILE = "haarcascade_frontalface_default.xml"

# Excel file illenkil auto create cheyyan
def init_excel():
    if not os.path.exists(EXCEL_FILE):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Attendance"
        ws.append(["ID/Name", "Time", "Date"])
        wb.save(EXCEL_FILE)

init_excel()

HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Attendance System</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            margin: 0;
            padding: 20px 0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background-image: url('/static/m.jpg');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            font-family: 'Poppins', sans-serif;
            color: white;
        }

        h1 {
            color: #b5f3f4;
            font-size: 2.2rem;
            font-weight: 700;
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.7);
            margin-bottom: 15px;
            text-align: center;
        }

        .camera-card {
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(8px);
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-bottom: 20px;
        }

        video {
            width: 320px;
            height: 240px;
            border-radius: 8px;
            border: 2px solid #b5f3f4;
            background-color: #000;
            object-fit: cover;
        }

        .container {
            display: flex;
            flex-direction: column;
            gap: 15px;
            width: 290px;
        }

        .btn {
            padding: 12px;
            font-size: 15px;
            font-weight: 600;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            font-family: 'Poppins', sans-serif;
            text-decoration: none;
            text-align: center;
            box-sizing: border-box;
            display: block;
        }

        .btn-register { background-color: #28a745; }
        .btn-register:hover { background-color: #218838; }

        .btn-scan { background-color: #007bff; }
        .btn-scan:hover { background-color: #0056b3; }

        .btn-report { background-color: #17a2b8; }
        .btn-report:hover { background-color: #138496; }

        #status-box {
            margin-top: 10px;
            font-size: 14px;
            font-weight: 600;
            padding: 8px 12px;
            border-radius: 6px;
            background: rgba(0, 0, 0, 0.7);
            color: #ffeb3b;
            text-align: center;
            width: 280px;
        }
    </style>
</head>
<body>
    <h1>Student Attendance System</h1>

    <div class="camera-card">
        <!-- Live Browser Camera View -->
        <video id="webcam" autoplay playsinline></video>
        <canvas id="canvas" style="display:none;"></canvas>
        <div id="status-box">Camera Initializing...</div>
    </div>

    <div class="container">
      <!-- Button 1: Mark Attendance (Scan Face) -->
      <button onclick="captureAndDetect()" class="btn btn-scan">Attendance Mark (Scan)</button>

      <!-- Button 2: Registration Info -->
      <button onclick="registerInfo()" class="btn btn-register">Register Student</button>

      <!-- Button 3: Download Excel Sheet -->
      <a href="/open-excel" class="btn btn-report">Get Today Attendance</a>
    </div>

    <script>
        const video = document.getElementById('webcam');
        const canvas = document.getElementById('canvas');
        const statusBox = document.getElementById('status-box');

        // Browser Camera Start
        navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } })
            .then(stream => { 
                video.srcObject = stream;
                statusBox.innerText = "Camera Ready. Press 'Attendance Mark'";
                statusBox.style.color = "#28a745";
            })
            .catch(err => { 
                statusBox.innerText = "Camera Permission Denied!";
                statusBox.style.color = "#dc3545";
            });

        // Face Detection Trigger
        function captureAndDetect() {
            statusBox.innerText = "Scanning Face...";
            statusBox.style.color = "#ffeb3b";
            
            const context = canvas.getContext('2d');
            canvas.width = video.videoWidth || 320;
            canvas.height = video.videoHeight || 240;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);

            const imageData = canvas.toDataURL('image/jpeg');

            fetch('/detect-face', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: imageData })
            })
            .then(res => res.json())
            .then(data => {
                statusBox.innerText = data.message;
                if(data.status === 'success'){
                    statusBox.style.color = "#28a745";
                } else {
                    statusBox.style.color = "#dc3545";
                }
            })
            .catch(err => {
                statusBox.innerText = "Error Connecting to Server!";
                statusBox.style.color = "#dc3545";
            });
        }

        function registerInfo() {
            alert("Look at the camera and click 'Attendance Mark' to detect face!");
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_LAYOUT)

# Browser Image Processing Route
@app.route('/detect-face', methods=['POST'])
def detect_face():
    try:
        data = request.get_json()
        if 'image' not in data:
            return jsonify({"status": "error", "message": "No image data received!"})

        image_data = data['image'].split(',')[1]
        nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Haar Cascade Load
        if not os.path.exists(CASCADE_FILE):
            return jsonify({"status": "error", "message": "Haar Cascade XML File Missing!"})

        face_cascade = cv2.CascadeClassifier(CASCADE_FILE)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) > 0:
            now = datetime.now()
            time_str = now.strftime("%H:%M:%S")
            date_str = now.strftime("%Y-%m-%d")

            wb = openpyxl.load_workbook(EXCEL_FILE)
            ws = wb.active
            ws.append(["Student Detected", time_str, date_str])
            wb.save(EXCEL_FILE)

            return jsonify({"status": "success", "message": f"Face Detected! Attendance Marked at {time_str}"})
        else:
            return jsonify({"status": "failed", "message": "No Face Detected! Look at Camera."})

    except Exception as e:
        return jsonify({"status": "error", "message": f"Server Error: {str(e)}"})

# Excel File Download
@app.route('/open-excel', methods=['GET'])
def open_excel():
    if os.path.exists(EXCEL_FILE):
        return send_file(EXCEL_FILE, as_attachment=True)
    return "<h3>Excel File Not Found</h3>", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)