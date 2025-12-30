📘 ATTENDANCE AND PROXY ELIMINATION SYSTEM
🧠 Overview

This project is a secure, AI-powered attendance system that uses Face Recognition (DeepFace + OpenCV) to automatically mark attendance, prevent proxy attendance, and generate encrypted attendance reports. The system captures live webcam footage, identifies registered students, stores attendance securely in a database, and emails password-protected reports.

🔍 Key Features

✅ Real-Time Face Recognition using DeepFace (FaceNet)
✅ Automatic Attendance Marking
✅ Proxy Detection & Elimination
✅ Encrypted Student Data (Fernet Encryption)
✅ MySQL Database Integration
✅ PDF Attendance Report Generation
✅ Password-Protected PDF Reports
✅ Automated Email Delivery
✅ Face Capture & Verification Logging

🧠 System Workflow

Load student dataset (face images).

Generate facial embeddings using FaceNet.

Capture live camera feed.

Detect and recognize faces in real time.

Mark attendance automatically.

Store attendance in MySQL database.

Generate encrypted PDF report.

Email report to authorized recipient.

🧰 Technologies Used
Category	Tools
Programming	Python
Computer Vision	OpenCV, DeepFace
Database	MySQL
Encryption	Fernet (Cryptography)
PDF Handling	ReportLab, PyPDF
Email	smtplib
Face Detection	Haar Cascade
OS	Windows / Linux
📁 Project Structure
ATTENDANCE-AND-PROXY-ELIMINATION/
│
├── dataset/
│   ├── student1/
│   │   ├── img1.jpg
│   ├── student2/
│
├── temp_faces/
├── attendance/
├── main.py
├── secret.key
├── requirements.txt
└── README.md

🔐 Security Features

AES-based encryption using Fernet

Password-protected PDF reports

Encrypted student names in database

Secure email transmission