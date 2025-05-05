🎯 Face Recognition Attendance System with Advanced GUI
A Python-based face recognition attendance system with a modern GUI built using Tkinter and ttkbootstrap, supporting MySQL database integration, CSV export, and webcam-based attendance marking with face recognition. This system is designed for both individual and institutional use, offering simplicity, reliability, and real-time logging.

📦 Features
     ✅ Face Registration via Webcam
     ✅ Live Face Recognition Attendance
     ✅ MySQL Database Integration
     ✅ Automatic CSV Export
     ✅ Advanced Tkinter GUI with Custom Background Support
     ✅ Corrupted Data Repair (Face Encoding)
     ✅ Real-Time Logging Panel
     ✅ One-Click Background Image Change
     ✅ Cross-Platform Support (Windows, macOS, Linux)

🛠️ Tech Stack
     Python 3
     OpenCV
     face_recognition
     Tkinter + ttkbootstrap
     MySQL Connector for Python
     Pillow (PIL)

🗃️ Database Schema
        Database Name: face_attendance

        users Table
        Column	                   Type
        id                     	  INT, AUTO_INCREMENT, PRIMARY KEY
        name      	                  VARCHAR(255)
        face_encoding	          LONGTEXT

         attendance Table
         Column	                   Type
         id                           	INT, AUTO_INCREMENT, PRIMARY KEY
         name	                 VARCHAR(255)
         date                  	 DATE
         time	                 TIME

🚀 Getting Started
1. Clone the Repository
      git clone https://github.com/tanishk937/face-attendance-system.git
      cd face-attendance-system
2. Install Dependencies
      pip install -r requirements.txt
      If you don't have requirements.txt, install manually:
      pip install opencv-python face_recognition numpy mysql-connector-python ttkbootstrap pillow
3. Set Up the MySQL Database :-

     CREATE DATABASE face_attendance;
     USE face_attendance;
     CREATE TABLE users (
         id INT AUTO_INCREMENT PRIMARY KEY,
         name VARCHAR(255),
         face_encoding LONGTEXT
         );

     CREATE TABLE attendance (
         id INT AUTO_INCREMENT PRIMARY KEY,
         name VARCHAR(255),
         date DATE,
         time TIME
         );
🔑 Update your database credentials in the script (DB_CONFIG section).


💡 How to Use
        Run the code :python yourscript.py
        Register Face: Click "Register Face" and enter a name. Stand in front of your webcam and press c to capture.
        Run Attendance: Click "Run Attendance". Your face will be recognized and attendance recorded.
        View Logs: All events are shown in the log panel.
        Export CSV: Opens the attendance.csv file with attendance records.
        Repair DB: Removes corrupted face encodings from the database.
        Change Background: Customize your app background using an image file.


📁 Output
       attendance.csv: Contains all attendance entries with name, date, and time.
       MySQL DB: Stores user face encodings and historical attendance logs.


📷 Screenshots
      1.  ![Image](https://github.com/user-attachments/assets/87c8198f-87e0-4df0-96d4-410780068b2a)
      2.  ![Image](https://github.com/user-attachments/assets/13509637-68c4-41e2-a51d-9eed3b8c7990)
      3.  ![Image](https://github.com/user-attachments/assets/3b65bf89-3126-48ee-93b1-0b618399e324)
      4.  ![Image](https://github.com/user-attachments/assets/b65b76d4-e42f-4aa5-94a1-3a3768b92eee)

🧩 Limitations
       Works best under good lighting and with one face visible during registration.
       Requires a working webcam and MySQL server.

🤝 Contributing
       Feel free to fork the repository and submit a pull request for enhancements. Bug reports, feature requests, and improvements are welcome!

📜 License
       MIT License — use freely, contribute respectfully.

🧠 Credits
      Developed using [face_recognition](https://github.com/ageitgey/face_recognition)
      GUI styled with [ttkbootstrap](https://ttkbootstrap.readthedocs.io/)
