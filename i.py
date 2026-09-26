import cv2
import os
output_folder = "my frame"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

cap = cv2.VideoCapture(0)



if not cap.isOpened():
    print("Camera not found")
    exit()
print("Camera is open")
name = ""
is_typing = False

cv2.namedWindow("My frame", cv2.WINDOW_AUTOSIZE)# my frame enn paranna window ino enn check cheyyunnu close cheyyan

while True:
    ret,frame = cap.read()
    if not ret:
        print("frame not readed")
        break
    orginal_frame = frame.copy()
    if not is_typing:
       display_text = "Press 'S' to Save and enter student name| Press 'Q' to quit"
       color = (0, 255, 255) #cyan
    else:
       display_text = f"Enter Student Name: {name}_"
       color = (255, 255, 0)# yellow
    cv2.putText(
       frame,
       display_text,
       (20, 40),
       cv2.FONT_HERSHEY_SIMPLEX,
       0.6,
       color,
       2
    )
    

    cv2.imshow("My frame", frame)

    key = cv2.waitKey(1) & 0xFF 
    if key != 255:
     if key == ord('q') and not is_typing:
      break 

    if cv2.getWindowProperty("My frame", cv2.WND_PROP_VISIBLE) < 1:
      break 
     
     #'s' nekkumpol camera screenil name type cheyyan start cheyyum
    elif key == ord('s') and not is_typing:
        is_typing = True
        name =""
        # 'Enter' press cheyth kayinj ath save aakanulla code
    elif is_typing:
         #'Enter' keyudey key code (13) aan
         if key == 13:
            clean_name = name.strip()
            if clean_name:
               image_path = os.path.join(output_folder, f"{clean_name}.jpg")
               
               count = 1
               while os.path.exists(image_path):
                  image_path = os.path.join(output_folder, f"{clean_name}_{count}.jpg")
                  count += 1

               cv2.imwrite(image_path, orginal_frame)
               print(f"Saved: {image_path}")
            is_typing = False
            name = ""

            #'Backspace' adikkanulla key code aan (8)

         elif key == 8:
             name = name[:-1]
           #ESCAPE key use akkunnath atha save akkeet ath vend ennan enkil esc adich cancel cheyyaam esc key code(27)
         elif key == 27:
            is_typing = False
            name = ""
         #key boardileyy ella aksharangalum type cheyyan
         elif 32 <= key <= 126:
            name += chr(key)
               
     
     
cap.release()
cv2.destroyAllWindows()