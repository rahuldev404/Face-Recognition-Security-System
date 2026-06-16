from http import server
import cv2
import os
import requests
import pickle
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import getpass
import sqlite3
import subprocess
import random
import numpy as np
from datetime import datetime
from email.message import EmailMessage
from deepface import DeepFace


# Configuration
KNOWN_DIR = "Uploaded_Images_In_JPG"
INTRUDER_DIR = "Intruders"
CACHE_FILE = "Face_embeddings.pkl"
DB_FILE = "security_logs.db"

# 0.35 is the perfect threshold for Facenet + opencv combo
THRESHOLD = 0.35
MAX_PASSWORD_TRIES = 3
MAX_OTP_TRIES = 3
OTP_EXPIRE_SECONDS = 120

SENDER_EMAIL = "xxxxxxxxxxx@gmail.com"# your Sender email address
RECEIVER_EMAIL = "xxxxxxxxxxxx@gmail.com"#uour receiver emial address
EMAIL_PASSWORD = "xxxxxxxxxxxxxx" # use app password for gamil #Note aap pahle 2verification on karna hoga 
SEND_USER_GMAIL_OTP = "xxxxxxxxxxxxx@gmail.com"#jis par aap otp bhejna chate hai 

def send_otp_to_user_gmail(otp_code):
    try:
        msg = MIMEMultipart()
        msg['from'] = SENDER_EMAIL
        msg['to'] = SEND_USER_GMAIL_OTP
        msg['Subject'] = "Your OTP Code for Mac Security System"
        
        body = f"Hello,\n\nYour OTP for Verification is: {otp_code}\nThis code is valid for 2 minutes.\n\nIf you did not request the OTP, please secure your account time immediately"
        msg.attach(MIMEText(body, 'plain'))

        #server connection
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
        server.sendmail(SENDER_EMAIL, SEND_USER_GMAIL_OTP, msg.as_string())
        server.quit()
        
        print("📩 OTP email dispatched successfully.")
    except Exception as e:
        print(f"❌ Failed to send OTP email: {e}")


os.makedirs(KNOWN_DIR, exist_ok=True)
os.makedirs(INTRUDER_DIR, exist_ok=True)


def init_db():
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            status TEXT,
            distance REAL,
            photo TEXT
        )
    """)
    con.commit()
    con.close()


def save_log(status, distance=None, photo=None):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute(
        "INSERT INTO logs(time, status, distance, photo) VALUES (?, ?, ?, ?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), status, distance, photo)
    )
    con.commit()
    con.close()


def get_embedding(img_input):
    # FIXED: Reverted back to built-in Facenet and opencv to avoid any stuck downloads
    result = DeepFace.represent(
        img_path=img_input,
        model_name="ArcFace",        
        detector_backend="yunet",  
        enforce_detection=False,  
        align=True
    )
    if not result or len(result) == 0:
        return None
    return result[0]["embedding"]


def load_embeddings():
    image_files = [f for f in os.listdir(KNOWN_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    
    if os.path.exists(CACHE_FILE):
        print("✅ Loading embeddings from cache...")
        with open(CACHE_FILE, "rb") as f:
            return pickle.load(f)

    print("🔄 Generating fresh embeddings cache...")
    embeddings = []

    for file in image_files:
        path = os.path.join(KNOWN_DIR, file)
        print(f"Processing training image: {path}")
        try:
            emb = get_embedding(path)
            if emb is not None:
                embeddings.append(emb)
        except Exception as e:
            print(f"⚠️ Could not process reference image {file}: {e}")

    if not embeddings:
        print(f"❌ Put reference photos in the '{KNOWN_DIR}' folder and restart.")
        exit()

    with open(CACHE_FILE, "wb") as f:
        pickle.dump(embeddings, f)

    return embeddings


def cosine_distance(a, b):
    a = np.array(a)
    b = np.array(b)
    return 1 - (np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def save_intruder_photo(frame):
    filename = datetime.now().strftime("unknown_%Y-%m-%d_%H-%M-%S.jpg")
    path = os.path.join(INTRUDER_DIR, filename)
    cv2.imwrite(path, frame)
    return path

import os
import smtplib
import requests
from datetime import datetime
from email.message import EmailMessage

# 1️⃣ Core Mac Frameworks ko globally sahi se import karna (Isse saari yellow lines hatengi)
try:
    from CoreLocation import CLLocationManager, CLGeocoder
    from PyObjCTools import AppHelper
except ImportError:
    CLLocationManager = None
    CLGeocoder = None
    AppHelper = None

def get_exact_mac_gps():
    if not CLLocationManager or not AppHelper:
        return None, None, "Unknown", "Unknown"
    
    class LocationDelegate:
        def __init__(self):
            self.lat = None
            self.lon = None
            self.city = "Exact GPS Location"
            self.region = "Verified via Mac Hardware"
            
        def locationManager_didUpdateLocations_(self, manager, locations):
            if locations:
                loc = locations[-1]
                self.lat = loc.coordinate().latitude
                self.lon = loc.coordinate().longitude
                
                try:
                    geocoder = CLGeocoder.alloc().init()
                    
                    def completion_handler(placemarks, error):
                        if placemarks and len(placemarks) > 0:
                            place = placemarks[0]
                            self.city = place.locality() if place.locality() else "Local Area"
                            self.region = place.administrativeArea() if place.administrativeArea() else "Mac Hardware"
                        AppHelper.stopEventLoop()
                        
                    geocoder.reverseGeocodeLocation_completionHandler_(loc, completion_handler)
                except Exception:
                    AppHelper.stopEventLoop()
                    
        def locationManager_didFailWithError_(self, manager, error):
            AppHelper.stopEventLoop()

    # Spacing fixed inside the function
    manager = CLLocationManager.alloc().init()
    delegate = LocationDelegate()
    manager.setDelegate_(delegate)
    manager.startUpdatingLocation()
    
    try:
        AppHelper.runConsoleEventLoop(argv=None, timeout=2.5)
    except Exception:
        try:
            AppHelper.runConsoleEventLoop(argv=None)
        except Exception:
            pass
        
    manager.stopUpdatingLocation()
    return delegate.lat, delegate.lon, delegate.city, delegate.region


def send_gmail(photo_path, distance=None, reason="Unknown User Detected"):
    if not EMAIL_PASSWORD:
        print("❌ Error: EMAIL_PASSWORD missing!")
        return

    # Default values setup (Offline setup)
    public_ip = "Offline (No Internet)"
    city = "Unknown"
    region = "Unknown"
    maps_link = "Not Available Offline"
    internet_working = False

    # 1️⃣ APPLE HARDWARE LEVEL TRACKING
    try:
        lat, lon, hw_city, hw_region = get_exact_mac_gps()
        if lat and lon:
            city = hw_city       
            region = hw_region   
            maps_link = f"https://www.google.com/maps?q={lat},{lon}"
    except Exception as gps_err:
        print(f"⚠️ Hardware GPS Failure: {gps_err}")
        lat = lon = None

    # 2️⃣ AGAR INTERNET HAI, TOH PUBLIC IP BHI FETCH KAREIN
    try:
        geo_response = requests.get('http://ip-api.com/json/', timeout=3)
        geo_data = geo_response.json()
        if geo_data.get('status') == 'success':
            public_ip = geo_data.get('query', 'Unknown')
            if city == "Unknown" or city == "Exact GPS Location":
                city = geo_data.get('city', 'Unknown')
                region = geo_data.get('regionName', 'Unknown')
            internet_working = True
    except Exception:
        internet_working = False

    # Data block content creation
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_content = f"""Mac Security System Notification.

Time: {current_time}
Event Details: {reason}
Distance Matrix Score: {distance if distance else "N/A"}
Device Name: Rahul's MacBook

🚨 INTRUDER TRACKING INFO:
📍 Public IP: {public_ip}
📍 Location: {city}, {region}
🌍 Live Map Link: {maps_link}
"""

    # 3️⃣ CONDITION A: LAPTOP OFFLINE HAI
    if not internet_working:
        print("⚠️ Internet offline hai! Saving accurate info locally...")
        offline_log_path = os.path.join(INTRUDER_DIR, "offline_logs.txt")
        with open(offline_log_path, "a") as log_file:
            log_file.write(f"\n{'='*40}\n{report_content}\nPhoto Saved At: {photo_path}\n{'='*40}\n")
        print(f"✅ Intruder report locally save ho gayi hai: {offline_log_path}")
        return

    # 4️⃣ CONDITION B: LAPTOP ONLINE HAI (Email send karein)
    try:
        msg = EmailMessage()
        msg["Subject"] = f"⚠️ Mac Security Alert: {reason}"
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL
        msg.set_content(report_content)

        if photo_path and os.path.exists(photo_path):
            with open(photo_path, "rb") as f:
                img = f.read()
            msg.add_attachment(img, maintype="image", subtype="jpeg", filename=os.path.basename(photo_path))

        # Live SMTP Send
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("📩 Security email dispatched with 100% accurate info and photo!")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")

def alarm():
    subprocess.Popen(["say", "Security breach. Access denied."])


def lock_mac():
    print("🔒 Locking MacBook monitor display immediately...")
    os.system("pmset displaysleepnow")


def check_system_password():
    username = getpass.getuser()
    for i in range(MAX_PASSWORD_TRIES):
        password = getpass.getpass(f"Enter Mac Password [{i+1}/{MAX_PASSWORD_TRIES}]: ")
        result = subprocess.run(
            ["dscl", ".", "-authonly", username, password],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if result.returncode == 0:
            return True
        print("❌ Invalid password.")
    return False


def generate_otp():
    return str(random.randint(100000, 999999))


def ask_otp():
    otp = generate_otp()
    print("\n-------------------------------------------")
    print(f"🔑 [LOCAL SECURITY 2FA] Your OTP is: {otp}")
    print("Valid for 2 minutes.")
    print("-------------------------------------------\n")
    #Gmail per OTP bhejne ke liye function call
    send_otp_to_user_gmail(otp)


    start_time = time.time()
    for i in range(MAX_OTP_TRIES):
        entered = input(f"Enter OTP [{i+1}/{MAX_OTP_TRIES}]: ")
        if time.time() - start_time > OTP_EXPIRE_SECONDS:
            print("⏰ Security challenge failed: OTP expired.")
            return False
        if entered == otp:
            return True
        print("❌ Incorrect verification code.")
    return False


def run_hybrid_security_check():
    init_db()
    print("⚡ Fetching primary biometric profiles...")
    known_embeddings = load_embeddings()

    # Silent background capture
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("❌ Cannot initialize connection to internal webcam.")
        return

    time.sleep(0.5)  
    ret, frame = cam.read()
    cam.release()  # Turn off camera immediately

    if not ret:
        print("❌ Failed to grab image frame.")
        return

    print("🔍 Analyzing background snapshot for biometric identity verification...")
    
    is_matched = False
    best_distance = None

    try:
        current_emb = get_embedding(frame)
        
        if current_emb is None:
            raise ValueError("No clear face structure found.")

        distances = [cosine_distance(known, current_emb) for known in known_embeddings]
        best_distance = min(distances)
        print(f"Analysis update -> Current Distance: {best_distance:.4f}")

        if best_distance <= THRESHOLD:
            print("✅ Face match verified. Welcome back, Rahul.")
            save_log("Rahul detected", best_distance, None)
            is_matched = True
            return

    except Exception as e:
        print(f"🔍 System scanning... Face not clearly read. Defaulting to fallback security protocols.")

    # FALLBACK ENGINE INITIALIZATION
    if not is_matched:
        print("❌ Identity mismatch detected!")
        
        # Step 1: Instantly save photo and dispatch to Gmail
        photo_path = save_intruder_photo(frame)
        save_log("Unknown Face Detected - Alert Sent", best_distance, photo_path)
        print("📧 Sending unknown user snapshot to your Gmail account...")
        send_gmail(photo_path, best_distance, reason="Unknown user sitting at your machine")

        # Step 2: Initialize 3-Times Local Password Challenge
        print("\n🔐 Launching fallback access console.")
        if check_system_password():
            print("✅ Credentials verified. Access granted.")
            save_log("System password correct after unknown face match failure", best_distance, None)
            return

        # Step 3: Initialize 2FA Local OTP Verification Layer
        print("⚠️ Three incorrect password updates recorded. Escalating to 2-Factor challenge...")
        if ask_otp():
            print("🔐 Two-Factor verification code match. Access granted.")
            save_log("Local OTP correct after wrong passwords", best_distance, None)
            return

        # Final Enforcement Breach Block
        print("🚨 Authorization parameters failed. Triggering containment actions.")
        save_log("Lockdown - Face, Passwords, and OTP all failed", best_distance, photo_path)
        alarm()
        lock_mac()


if __name__ == "__main__":
    run_hybrid_security_check()
