from flask import Flask, request,jsonify, render_template, redirect, url_for, Response
from ultralytics import YOLO
import cv2
import cvzone
import torch
import os
import math
from image_to_text import predict_number_plate
from paddleocr import PaddleOCR 
import mysql.connector
from notification import send_email_notification
from database import get_email,insert_with_helmet,insert_without_helmet,init_db

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'

# Initialize the YOLO model and other global variables
model = YOLO("./runs/detect/train13/weights/best.pt")
device = torch.device("cpu")
classNames = ["with helmet", "without helmet", "rider", "number plate"]
ocr = PaddleOCR(use_angle_cls=True, lang='en')
alerted_vehicle_numbers = set()

db_config = {
    'user': 'root',
    'password': 'Your_password',
    'host': 'localhost',
    'database': 'vehicle_db'
}

# Function to process video and send email notifications
def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.mp4')
    output = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    while True:
        success, img = cap.read()
        if not success:
            break

        new_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = model(new_img, stream=True, device="cpu")

        for r in results:
            boxes = r.boxes
            li = dict()
            rider_box = list()
            xy = boxes.xyxy
            confidences = boxes.conf
            classes = boxes.cls
            new_boxes = torch.cat((xy.to(device), confidences.unsqueeze(1).to(device), classes.unsqueeze(1).to(device)), 1)
        
            try:
                new_boxes = new_boxes[new_boxes[:, -1].sort()[1]]
                indices = torch.where(new_boxes[:, -1] == 2)
                rows = new_boxes[indices]
            
                for box in rows:
                    x1, y1, x2, y2 = box[0], box[1], box[2], box[3]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    rider_box.append((x1, y1, x2, y2))
        
            except:
                pass

            for i, box in enumerate(new_boxes):
                x1, y1, x2, y2 = box[0], box[1], box[2], box[3]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                w, h = x2 - x1, y2 - y1
                conf = math.ceil((box[4] * 100)) / 100
                cls = int(box[5])
            
                if classNames[cls] == "without helmet" and conf >= 0.5 or classNames[cls] == "rider" and conf >= 0.45 or \
                    classNames[cls] == "number plate" and conf >= 0.5:
                
                    if classNames[cls] == "rider":
                        rider_box.append((x1, y1, x2, y2))
                
                    if rider_box:
                        for j, rider in enumerate(rider_box):
                            if x1 + 10 >= rider_box[j][0] and y1 + 10 >= rider_box[j][1] and x2 <= rider_box[j][2] and \
                                y2 <= rider_box[j][3]:
                            
                                cvzone.cornerRect(img, (x1, y1, w, h), l=15, rt=5, colorR=(255, 0, 0))
                                cvzone.putTextRect(img, f"{classNames[cls].upper()}", (x1 + 10, y1 - 10), scale=1.5,
                                           offset=10, thickness=2, colorT=(39, 40, 41), colorR=(248, 222, 34))
                            
                                li.setdefault(f"rider{j}", [])
                                li[f"rider{j}"].append(classNames[cls])
                            
                                if classNames[cls] == "number plate":
                                    npx, npy, npw, nph, npconf = x1, y1, w, h, conf
                                    crop = img[npy:npy + h, npx:npx + w]
                        
                            if li:
                                for key, value in li.items():
                                    if key == f"rider{j}":
                                        if len(list(set(li[f"rider{j}"]))) == 3:
                                            try:
                                                vehicle_number, conf = predict_number_plate(crop, ocr)
                                            
                                                if vehicle_number and conf:
                                                    cvzone.putTextRect(img, f"{vehicle_number} {round(conf*100, 2)}%",
                                                               (x1, y1 - 50), scale=1.5, offset=10,
                                                               thickness=2, colorT=(39, 40, 41),
                                                               colorR=(105, 255, 255))
                                                
                                                    if vehicle_number not in alerted_vehicle_numbers:
                                                        email = get_email(vehicle_number)
                                                    
                                                        if email:
                                                            message = f"Alert: Your vehicle ({vehicle_number}) rider is detected without a helmet."
                                                        
                                                            if send_email_notification(email, message):
                                                                print(f"Email notification sent successfully to {email}")
                                                            else:
                                                                print("Failed to send email notification.")
                                                    
                                                        # Insert into respective tables
                                                        if "without helmet" in li[f"rider{j}"]:
                                                            insert_without_helmet(vehicle_number)
                                                        else:
                                                            insert_with_helmet(vehicle_number)

                                                        alerted_vehicle_numbers.add(vehicle_number)
                                                
                                            except Exception as e:
                                                print(e)
    
        # Write frame to output video
        output.write(img)
        # Encode image as JPG and yield it for Flask to display
        ret, jpeg = cv2.imencode('.jpg', img)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()
    cv2.destroyAllWindows()

# Route to upload form
@app.route('/')
def upload_form():
    return render_template('upload.html')

# Route to handle video upload and processing
@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return 'No file part'
    
    file = request.files['video']
    
    if file.filename == '':
        return 'No selected file'
    
    if file:
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(video_path)
        return Response(process_video(video_path), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/add_owner', methods=['GET', 'POST'])
def add_owner():
    if request.method == 'POST':
        vehicle_number = request.form['vehicle_number']
        owner_name = request.form['owner_name']
        email = request.form['email']
        phone_number = request.form['phone_number']

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = '''
            INSERT INTO vehicle_owners_list (vehicle_number, owner_name, email, phone_number)
            VALUES (%s, %s, %s, %s)
        '''
        cursor.execute(query, (vehicle_number, owner_name, email, phone_number))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('upload_form'))
    return render_template('add_owner.html')

@app.route('/search_details', methods=['GET'])
def search_details():
    vehicle_number = request.args.get('vehicle_number')
    email = request.args.get('email')

    if not vehicle_number or not email:
        return jsonify({'error': 'Vehicle number and email are required'}), 400

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = '''
            SELECT vehicle_number, owner_name, email, phone_number
            FROM vehicle_owners_list
            WHERE vehicle_number = %s OR email = %s
        '''
        cursor.execute(query, (vehicle_number, email))
        row = cursor.fetchone()
        print(vehicle_number)
        print(email)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({'error': str(err)}), 500

    finally:
        cursor.close()
        conn.close()

    if row:
        return jsonify({
            'found': True,
            'vehicle_number': row[0],
            'owner_name': row[1],
            'email': row[2],
            'phone_number': row[3]
        })
    else:
        return jsonify({'found': False})
    
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
