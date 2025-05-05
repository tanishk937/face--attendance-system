# Face Recognition Attendance System with Advanced GUI

import tkinter as tk
from ttkbootstrap.widgets import Button  
from tkinter import filedialog, messagebox
from tkinter import simpledialog
from ttkbootstrap import Style
from ttkbootstrap.constants import *
import cv2
import face_recognition
import numpy as np
import mysql.connector
import pickle
import base64
import datetime
import csv
import os
import time
from PIL import Image, ImageTk

# ==================== Database Config ====================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root937",
    "database": "face_attendance"
}

# ==================== Utility Functions ====================
def connect_to_database():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        return conn, cursor
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to connect: {err}")
        return None, None

def encode_face_encoding(face_encoding):
    try:
        pickled_encoding = pickle.dumps(face_encoding)
        encoded_data = base64.b64encode(pickled_encoding).decode('utf-8')
        return encoded_data
    except Exception as e:
        return None

def decode_face_encoding(encoding_base64):
    try:
        if encoding_base64 is None:
            return None
        missing_padding = len(encoding_base64) 
        if missing_padding:
            encoding_base64 += '=' * (4 - missing_padding)
        encoding_bytes = base64.b64decode(encoding_base64)
        return pickle.loads(encoding_bytes)
    except Exception as e:
        return None

def is_already_recorded(cursor, name, date):
    try:
        cursor.execute("SELECT COUNT(*) FROM attendance WHERE name = %s AND date = %s", (name, date))
        return cursor.fetchone()[0] > 0
    except:
        return False

# ==================== Core Functionalities ====================
def register_face(log_callback):
    conn, cursor = connect_to_database()
    if not conn:
        return

    def save_encoding(name, encoding):
        encoded_data = encode_face_encoding(encoding)
        if encoded_data:
            cursor.execute("SELECT COUNT(*) FROM users WHERE name = %s", (name,))
            if cursor.fetchone()[0] > 0:
                cursor.execute("UPDATE users SET face_encoding = %s WHERE name = %s", (encoded_data, name))
            else:
                cursor.execute("INSERT INTO users (name, face_encoding) VALUES (%s, %s)", (name, encoded_data))
            conn.commit()

    name = simpledialog.askstring("Register Face", "Enter name:")
    if not name:
        messagebox.showwarning("Invalid", "Name cannot be empty")
        conn.close()
        return

    video_capture = cv2.VideoCapture(0)
    log_callback("Webcam started. Press 'c' to capture face or 'q' to quit.")

    while True:
        ret, frame = video_capture.read()
        if not ret:
            log_callback("Failed to grab frame.")
            break
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        for top, right, bottom, left in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.imshow("Register Face - Press 'c' or 'q'", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            if len(face_locations) == 1:
                face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
                save_encoding(name, face_encoding)
                log_callback(f"Face data saved for {name}.")
                break
            else:
                log_callback("Ensure only one face is visible.")
        elif key == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    conn.close()

def run_attendance(log_callback):
    conn, cursor = connect_to_database()
    if not conn:
        return
    try:
        cursor.execute("SELECT name, face_encoding FROM users")
        stored_faces = cursor.fetchall()
    except:
        log_callback("Error loading face data.")
        return

    known_face_encodings = []
    known_face_names = []
    for name, enc in stored_faces:
        dec = decode_face_encoding(enc)
        if dec is not None:
            known_face_encodings.append(dec)
            known_face_names.append(name)

    if not known_face_encodings:
        log_callback("No valid encodings found.")
        return

    csv_filename = "attendance.csv"
    if not os.path.exists(csv_filename):
        with open(csv_filename, mode="w", newline="") as f:
            csv.writer(f).writerow(["Name", "Date", "Time"])

    video_capture = cv2.VideoCapture(0)
    last_recognized = {}
    cooldown = 5
    log_callback("Attendance started. Press 'q' to quit.")

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, face_locations)

        for enc, loc in zip(encodings, face_locations):
            matches = face_recognition.compare_faces(known_face_encodings, enc, tolerance=0.9)
            name = "Unknown"
            if True in matches:
                best_idx = np.argmin(face_recognition.face_distance(known_face_encodings, enc))
                name = known_face_names[best_idx]

                now = time.time()
                if name not in last_recognized or now - last_recognized[name] > cooldown:
                    last_recognized[name] = now
                    dt = datetime.datetime.now()
                    date, time_str = dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S")
                    if not is_already_recorded(cursor, name, date):
                        cursor.execute("INSERT INTO attendance (name, date, time) VALUES (%s, %s, %s)", (name, date, time_str))
                        conn.commit()
                        with open(csv_filename, mode="a", newline="") as f:
                            csv.writer(f).writerow([name, date, time_str])
                        log_callback(f"{name} marked present at {time_str}.")

            top, right, bottom, left = loc
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, bottom + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        cv2.imshow("Attendance", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    conn.close()

def repair_database(log_callback):
    conn, cursor = connect_to_database()
    if not conn:
        return
    cursor.execute("SELECT id, name, face_encoding FROM users")
    users = cursor.fetchall()
    for uid, name, enc in users:
        if decode_face_encoding(enc) is None:
            cursor.execute("DELETE FROM users WHERE id = %s", (uid,))
            conn.commit()
            log_callback(f"Corrupted encoding removed for {name}")
    conn.close()

def export_csv():
    try:
        os.startfile("attendance.csv")
    except:
        messagebox.showerror("Error", "CSV file not found.")

# ==================== GUI ====================
def main():
    app = tk.Tk()
    app.title("Face Recognition Attendance System")
    app.geometry("900x600")
    app.resizable(False, False)

    style = Style("cosmo")

    bg_image = None
    canvas = tk.Canvas(app, width=900, height=600)
    canvas.pack(fill="both", expand=True)

    def change_background():
        nonlocal bg_image
        file = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png")])
        if file:
            img = Image.open(file).resize((900, 600))
            bg_image = ImageTk.PhotoImage(img)
            canvas.create_image(0, 0, image=bg_image, anchor="nw")

    # Status/log box
    log_box = tk.Text(app, height=6, bg="#f0f0f0")
    log_window = canvas.create_window(20, 430, anchor="nw", window=log_box, width=860)

    def log(msg):
        log_box.insert(tk.END, msg + "\n")
        log_box.see(tk.END)

    # Buttons
    buttons = [
        ("Register Face", lambda: register_face(log)),
        ("Run Attendance", lambda: run_attendance(log)),
        ("Repair DB", lambda: repair_database(log)),
        ("Export CSV", export_csv),
        ("Change background", change_background),
        ("Exit", app.destroy)
    ]

    for i, (label, cmd) in enumerate(buttons):
        btn = Button(app, text=label, command=cmd, bootstyle=PRIMARY, width=20) 
        canvas.create_window(90 + (i % 3) * 240, 350 + (i // 3) * 50, window=btn)

    app.mainloop()

if __name__ == '__main__':
    main()