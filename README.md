# ATTANDANCE-AND-PROXY-ELIMENTATION
# 🧑‍🏫 Face Recognition Attendance System

A real-time face recognition-based attendance system using **OpenCV** and **DeepFace**. It captures live webcam feeds, detects faces, matches them with known dataset embeddings using **Facenet**, logs attendance, and sends the final CSV report via email.

---

## 📌 Features

- 📸 Real-time face detection and recognition (Facenet-based)
- 🧠 Embedding generation for each registered user
- 📊 Automatic attendance logging and classification:
  - **Present** (detected ≥6 times)
  - **Early Left** (detected 1-4 times)
  - **Late Comer** (detected only in later captures)
  - **Absent**
- 📨 Sends attendance CSV summary via Gmail
- ✅ Save all captured faces for traceability
- ⏱️ Timed captures (default: 10 captures, 3 seconds apart)

---

## 🧰 Tech Stack

- Python
- OpenCV
- DeepFace (Facenet model)
- Pandas
- SciPy (cosine similarity)
- smtplib (for sending emails)

---

## 🗂 Folder Structure

project/
│
├── dataset/ # Registered student face folders
│ └── JohnDoe/
│ └── image1.jpg
│
├── captures/ # Temp folder for captured face images
├── attendance/ # Output CSV files with attendance
├── main.py # Main Python script
