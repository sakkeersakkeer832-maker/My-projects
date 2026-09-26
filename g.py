import cv2
import os
import numpy as np
import urllib.request
import time
from datetime import datetime
#pdf undaakkan venda librarkal
import pandas as pd
#attendance data store cheyyanulla variable
marked_students = set() #oru vettam attendance edutha aalk pinney edukkaathirikkaan
attendance_list = [["Name", "Date", "Time"]]#pdf ready aakkanulla list





xml_file = "haarcascade_frontalface_default.xml"
if not os.path.exists(xml_file):
    print("Downloading face detection model file...")
    url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
    urllib.request.urlretrieve(url, xml_file)
    print("Download complete!")

face_cascade = cv2.CascadeClassifier(xml_file)

    #'My frame' folderil ninn image edukkunnu train cheyikkunnu
dataset_folder = "my frame"
recognizer = cv2.face.LBPHFaceRecognizer_create()

face = []
labels = []
name_mapping = {} # id -> name
current_id = 0

print("Training faces from 'my frame' folder...")

if not os.path.exists(dataset_folder):
        print(f"Error: '{dataset_folder}' folder not found!!")
        exit()

for filename in os.listdir(dataset_folder):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        img_path = os.path.join(dataset_folder, filename)


            #file il ninn student name sepparate cheyyan \|/
        person_name = filename.split('.')[0].split('_')[0]

        if person_name not in name_mapping.values():
                 name_mapping[current_id] = person_name
                 label_id = current_id
                 current_id += 1
        else:
            for k, v in name_mapping.items():
                if v == person_name:
                    label_id = k
                    break


        image = cv2.imread(img_path)
        if image is None:
             continue

        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)       # folderil ninn rgb image ineyy black and white aakki maattum athan computerin manassilaakkan eluppam
        detected_faces = face_cascade.detectMultiScale(gray_image,
                                                        1.1,
                                                          4,
                                                        minSize=(100, 100)
                                                      )


        for (x, y, w, h) in detected_faces:
                 face_roi = gray_image[y:y+h, x:x+w] # roi means 'Region of Interest'
                 face_roi = cv2.resize(face_roi, (200, 200))
                 face.append(face_roi)
                 labels.append(label_id)

if len(face) == 0:
     print("No faces detected in the saved photos!! Please run File 1 and save proper images.")
     exit()


        # Model Training
recognizer.train(face, np.array(labels))
print("Training completed successfully!\nStarting Face Recognition Camera...")


        #camera open aayi live aayi face detect cheyyunnu
cap = cv2.VideoCapture(0)

# my frame enn paranna window ino enn check cheyyunnu close cheyyan
cv2.namedWindow("Student Face Recognition System", cv2.WINDOW_AUTOSIZE)



face_detection_timers = {} # ororutharudem face kandu enn track cheyyaan
HOLD_DURATION = 2.0

while True:
    ret, frame = cap.read()
    if not ret:
            print("Camera frame not available")
            break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # live camerayiley light correct aaakkunnu
    gray_equalized = cv2.equalizeHist(gray)
    # face detection kooduthal sheriyaakkan
    detected_faces = face_cascade.detectMultiScale(gray_equalized, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))


    #AAREYUM kandillenkil reset aavum
    if len(detected_faces) == 0:
        current_detected_user = None

    for (x, y, w, h) in detected_faces:
          face_roi = gray[y:y+h, x:x+w]

          label_id, confidence = recognizer.predict(face_roi)



    current_frame_recognized_names = set()

    for (x, y, w, h) in detected_faces:
            face_roi = gray[y:y+h, x:x+w]
              # camerayiley frame 200x200 aakkunnu
            face_roi = cv2.resize(face_roi, (200, 200))
                #face recognition cheyyunnu

            label_id, confidence = recognizer.predict(face_roi)

            display_text = "Unknown"
            color = (0, 0, 255)  # Red
    
                #image folderil save cheyyunna name anusarich filter cheyyunnu
            if confidence < 65:
                    student_name = name_mapping.get(label_id, "Unknown")

                    if student_name != "Unknown":
                         current_frame_recognized_names.add(student_name)
                     

                         #nerthey attendance mark cheythaal Marked enn kaanikkum
                         if student_name in marked_students:
                               display_text = f"{student_name} (Marked)"
                               color = (0, 255, 0) #green
                    
                         else:
                               #first knda udan time save cheyyunnu
                               if student_name not in face_detection_timers:
                                     face_detection_timers[student_name] = time.time()
                            
                               #knda samayam kaanikkunnu
                               elapsed_time = time.time() - face_detection_timers[student_name]


                               #2 second thudarchayaayi detect cheythaaley attendance mark cheyyu
                               if elapsed_time >= HOLD_DURATION:
                                     marked_students.add(student_name)
                                     now = datetime.now()
                                     date_str = now.strftime("%Y-%m-%d")
                                     time_str = now.strftime("%H:%M:%S")


                                     attendance_list.append([student_name, date_str, time_str])
                                     print(f"Attendance Marked (Verified 2s): {student_name} at {time_str}")

                                     display_text = f"{student_name} (Marked!)"
                                     color = (0, 255, 0)#green

                               else:
                                     #2 sec aavunnath vareyy visual cound kaanikkunnuu
                                     display_text = f"Scanning {student_name}... ({elapsed_time:.1f}s)"
                                     color = (0, 255, 255)# yellow

                   

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, display_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                                     
                        # ക്യാമറയിൽ ഫെയ്സ് കൃത്യമായി തുടർച്ചയായി ലഭിക്കാതിരുന്നാൽ ടൈമർ ക്ലിയർ ചെയ്യും
            for name in list(face_detection_timers.keys()):
                     if name not in current_frame_recognized_names and name not in marked_students:
                       del face_detection_timers[name]

    cv2.imshow("Student Face Recognition System", frame)



                    #ividayaanu attendance list add cheyyunney

            

                 #focus box varakkunnu
  

                # name screenil ezhuthunnu
    cv2.imshow("Student Face Recognition System", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
          break
    if cv2.getWindowProperty("Student Face Recognition System", cv2.WND_PROP_VISIBLE) < 1:
          print('Closed The Detection.....')
          break
    
cap.release()
cv2.destroyAllWindows() 
                    
if len(attendance_list) > 1:
    excel_filename = "attendance.xlsx"
    
    # List-നെ Pandas DataFrame ആക്കി മാറ്റുന്നു
    df = pd.DataFrame(attendance_list[1:], columns=attendance_list[0])
    
    # Excel ഫയലിലേക്ക് സേവ് ചെയ്യുന്നു
    df.to_excel(excel_filename, index=False)
    print(f"\n✅ Excel File Generated Successfully: {excel_filename}")
else:
    print("\nNo attendance recorded to generate Excel File.")


