from flask import Flask, render_template_string, redirect, send_file
import subprocess
import os

app = Flask(__name__)
app.secret_key = "secret_key_for_flask" # Flash messages-inulla key
#ividenn run cheyyanolla file name kodukkunnu

REGISTER_FILE ="i.py"
ATTENDANCE_FILE ="i2.py"
EXCEL_FILE ="Today attendance.xlsx"



HTML_LAYOUT ="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Attendance System</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
       body {
           margin: 0;
           padding: 0;
           height: 100vh;
           display: flex;
           flex-direction: column;
           justify-content: center;
           align-items: center;
           background-image: url('/static/m.jpg');
           background-size: cover;
           background-position: center;
           background-repeat: no-repeat;
           background-attachment: fixed;
           font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
       }

       h1, .heading {
            color:#b5f3f4; /* pure white heading*/
            font-size: 2.5rem;
            font-weight: 700;
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.7);
            margin-bottom: 20px;
            text-align: center;

       }
       .container {
           display: flex;
           flex-direction: column;
           gap: 20px;
           width: 280px;
       }

       .btn {
           padding: 15px;
           font-size: 16px;
           font-weight: 600;
           color: white;
           border: none;
           border-radius: 8px;
           cursor: pointer;
           transition: background-color 0.3s ease;
           width: 100%;
           font-family: 'Poppins', sans-serif;

       }
       .btn-register {
           background-color: #28a745;
       }
       .btn-register:hover {
           background-color: #218838;
       }

       .btn-scan{
           background-color: #007bff;
       }
       .btn-scan:hover{
           background-color: #0056b3;
       }
       .btn-report{
           background-color: #17a2b8;

       }
       .btn-report:hover {
           background-color: #138496;

       }
   </style>
</head>
<body>
    <!--HEADING-->
    <h1>Student Fa Attendance System</h1>

    <div class="container">
      <!-- Button 1: Register Student -->
      <form action="/run-reg" method="POST">
        <button type="submit" class="btn btn-register">Register student</button>
      </form>

      <!-- Button 2: Attendance Mark -->
       <form action="/run-att" method="POST">
        <button type="submit" class="btn btn-scan">Attendance mark</button>
       </form>
 
       <!-- Button 3: Get today attendance (open excel file0) -->
        <form action="/open-excel" method="POST">
          <button type="submit" class="btn btn-report">Get today attendance</button>
        </form>
    </div>
  </body>
  </html>
"""
#main home page run cheyyan
@app.route('/')
def home():
    return render_template_string(HTML_LAYOUT)

#student register file run cheyyaanulla code
@app.route('/run-reg', methods=['POST'])
def run_reg():
    if os.path.exists(REGISTER_FILE):
        try:
           subprocess.Popen(["python", REGISTER_FILE])
        except Exception as e:
            print(f"Error executing {REGISTER_FILE}: {e}")
    else:
        print(f"Error: {REGISTER_FILE} not found!")
    return redirect('/')


    #attendance marking file run aavunna code ividenn
@app.route('/run-att', methods=['POST'])
def run_att():
    if os.path.exists(ATTENDANCE_FILE):
        try:
          subprocess.Popen(["python", ATTENDANCE_FILE])
        except Exception as e:
            print(f"Error executing {ATTENDANCE_FILE}: {e}")
    else:
        print(f"Error: {ATTENDANCE_FILE} not found!")
    return redirect('/')

    #excel file cloud il download aayi kittaan ulla code
@app.route('/open-excel', methods=["GET"])
def open_excel():
    if os.path.exists(EXCEL_FILE):
        #CLOUD serveril (Linux) os.startfile work aakilla, so user-inu direct file download aakum
        return send_file(EXCEL_FILE, as_attachment=True)
    else:
      return f"<h3>Error: {EXCEL_FILE} not found on server!</h3>", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
