import cv2
import os
import time
import mysql.connector
from deepface import DeepFace
from scipy.spatial.distance import cosine
from cryptography.fernet import Fernet

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from pypdf import PdfReader, PdfWriter

import smtplib
from email.message import EmailMessage

# ======================================================
# 🔐 ENCRYPTION SETUP
# ======================================================
with open("secret.key", "rb") as f:
    key = f.read()

cipher = Fernet(key)

def encrypt_data(data: str) -> str:
    return cipher.encrypt(data.encode()).decode()

def decrypt_data(data: str) -> str:
    return cipher.decrypt(data.encode()).decode()

# ======================================================
# 🗄️ DATABASE CONFIG
# ======================================================
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="face_attendance",
    autocommit=True
)
cursor = db.cursor()

# ======================================================
# 📁 PATHS
# ======================================================
dataset_path = r"D:\university stuff\4 SEMESTER\PROG FOR AI\Project\dataset"
temp_dir = "temp_faces"
os.makedirs(temp_dir, exist_ok=True)

# ======================================================
# 🧑‍🎓 REGISTER STUDENTS
# ======================================================
def register_students():
    for folder in os.listdir(dataset_path):
        path = os.path.join(dataset_path, folder)
        if not os.path.isdir(path):
            continue

        if "_" in folder:
            roll, name = folder.split("_", 1)
        else:
            roll = folder
            name = folder

        images = os.listdir(path)
        if not images:
            continue

        image_path = os.path.join(path, images[0])
        enc_name = encrypt_data(name)

        cursor.execute("""
            INSERT INTO students (roll_no, name, section, department, image_path)
            VALUES (%s,%s,'A','CS',%s)
            ON DUPLICATE KEY UPDATE name=VALUES(name), image_path=VALUES(image_path)
        """, (roll, enc_name, image_path))

        print(f"✅ Registered: {roll}")

# ======================================================
# 🧠 LOAD EMBEDDINGS
# ======================================================
def load_embeddings():
    embeddings = {}
    for folder in os.listdir(dataset_path):
        path = os.path.join(dataset_path, folder)
        if not os.path.isdir(path):
            continue

        for img in os.listdir(path):
            try:
                img_path = os.path.join(path, img)
                emb = DeepFace.represent(
                    img_path=img_path,
                    model_name="Facenet",
                    enforce_detection=False
                )[0]["embedding"]
                embeddings[folder] = emb
                break
            except:
                pass
    return embeddings

# ======================================================
# 👁️ FACE RECOGNITION
# ======================================================
def recognize_face(face_img, embeddings):
    try:
        emb = DeepFace.represent(
            img_path=face_img,
            model_name="Facenet",
            enforce_detection=False
        )[0]["embedding"]
    except:
        return "Unknown"

    min_dist = 1
    identity = "Unknown"

    for name, ref in embeddings.items():
        dist = cosine(emb, ref)
        if dist < 0.4 and dist < min_dist:
            min_dist = dist
            identity = name

    return identity

# ======================================================
# 📝 MARK ATTENDANCE
# ======================================================
def mark_attendance(roll):
    cursor.execute("""
        SELECT * FROM attendance
        WHERE roll_no=%s AND date=CURDATE()
    """, (roll,))

    if cursor.fetchone():
        return

    cursor.execute("""
        INSERT INTO attendance (roll_no, date, time, status)
        VALUES (%s, CURDATE(), CURTIME(), 'Present')
    """, (roll,))

    print(f"✅ Attendance marked: {roll}")

# ======================================================
# 🔐 PDF PASSWORD FUNCTION
# ======================================================
def password_protect_pdf(input_pdf, output_pdf, password):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(password)

    with open(output_pdf, "wb") as f:
        writer.write(f)

# ======================================================
# 🎥 CAMERA (10 SECONDS)
# ======================================================
print("🔄 Loading embeddings...")
embeddings = load_embeddings()

print("🔐 Registering students...")
register_students()

cap = cv2.VideoCapture(0)
face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

print("🎥 Camera ON for 30 seconds...")
start_time = time.time()
RUN_TIME = 30

while True:
    if time.time() - start_time > RUN_TIME:
        break

    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        face_img = frame[y:y+h, x:x+w]
        temp_path = os.path.join(temp_dir, "temp.jpg")
        cv2.imwrite(temp_path, face_img)

        identity = recognize_face(temp_path, embeddings)
        color = (0, 255, 0) if identity != "Unknown" else (0, 0, 255)

        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, identity, (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        if identity != "Unknown":
            roll = identity.split("_")[0]
            mark_attendance(roll)

    cv2.imshow("Secure Face Attendance", frame)
    cv2.waitKey(1)

cap.release()
cv2.destroyAllWindows()

print("✅ Attendance captured")

# ======================================================
# 📄 GENERATE & PROTECT PDF
# ======================================================
cursor.execute("""
    SELECT s.roll_no, s.name, a.date, a.time, a.status
    FROM attendance a
    JOIN students s ON a.roll_no = s.roll_no
    ORDER BY a.date DESC
""")

records = cursor.fetchall()

pdf_name = "Attendance_Report.pdf"
protected_pdf = "Attendance_Report_Protected.pdf"
PDF_PASSWORD = "1234"

doc = SimpleDocTemplate(pdf_name, pagesize=A4)
styles = getSampleStyleSheet()
elements = []

elements.append(Paragraph("Attendance Report (Decrypted)", styles["Title"]))

table_data = [["Roll No", "Name", "Date", "Time", "Status"]]

for roll, enc_name, date, time_, status in records:
    name = decrypt_data(enc_name)
    table_data.append([roll, name, str(date), str(time_), status])

table = Table(table_data)
table.setStyle(TableStyle([
    ("GRID", (0,0), (-1,-1), 1, colors.black),
    ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ("FONT", (0,0), (-1,0), "Helvetica-Bold")
]))

elements.append(table)
doc.build(elements)

password_protect_pdf(pdf_name, protected_pdf, PDF_PASSWORD)
print("🔐 PDF protected with password")

# ======================================================
# 📧 EMAIL PDF
# ======================================================
EMAIL_SENDER = "uniquetrekk@gmail.com"
EMAIL_PASSWORD = "fvel fvad wvkk tpbh"
EMAIL_RECEIVER = "huzafa117@gmail.com"

msg = EmailMessage()
msg["Subject"] = "Secure Attendance Report (Password Protected)"
msg["From"] = EMAIL_SENDER
msg["To"] = EMAIL_RECEIVER
msg.set_content(
    "Attached is the password-protected attendance report.\n\nPDF"
)

with open(protected_pdf, "rb") as f:
    msg.add_attachment(
        f.read(),
        maintype="application",
        subtype="pdf",
        filename=protected_pdf
    )

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    server.send_message(msg)

print("📧 Email sent successfully")
print("✅ SYSTEM FINISHED")