
# 🔐 Face Recognition Security System

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?logo=opencv&logoColor=white)
![DeepFace](https://img.shields.io/badge/DeepFace-AI-orange)
![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey?logo=apple)
![Status](https://img.shields.io/badge/Status-Active-success)

A Python-based desktop security application that uses facial recognition to verify authorized users and detect unknown individuals. The system is designed to provide an additional layer of security by combining computer vision with AI-based face recognition.

## 📖 Overview

This project was developed to explore the practical use of Artificial Intelligence and Computer Vision in security systems. It identifies authorized users through facial recognition and can capture evidence when an unknown person attempts to access the system.

The project demonstrates how AI can be integrated into real-world desktop security applications using Python.

---

## ✨ Key Features

* AI-powered face authentication
* Detects authorized and unauthorized users
* Captures images of unknown individuals
* Maintains security logs
* Fast facial recognition using DeepFace
* Simple project structure for easy customization

---

## 🛠 Technologies Used

| Technology | Purpose                            |
| ---------- | ---------------------------------- |
| Python     | Core programming language          |
| OpenCV     | Camera access and image processing |
| DeepFace   | Face recognition engine            |
| NumPy      | Numerical operations               |
| SQLite     | Security log storage               |

---

## 📂 Project Structure

```text
Face-Recognition-Security-System/
│
├── face.py
├── Faces/
├── Intruders/
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/rahuldev404/Face-Recognition-Security-System.git
```

### 2. Open the project

```bash
cd Face-Recognition-Security-System
```

### 3. Install the required packages

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python face.py
```

---

## ⚙ How It Works

1. Load authorized face images.
2. Start the webcam.
3. Detect the face in real time.
4. Generate facial embeddings using DeepFace.
5. Compare the detected face with authorized embeddings.
6. Grant access if a match is found.
7. If the face is unknown, capture the image and record the event.

---

## 📸 Screenshots
<img width="1710" height="1112" alt="Screenshot 2026-06-16 at 2 58 07 PM" src="https://github.com/user-attachments/assets/7a8345fc-2411-46ea-8032-73b60dc8a077" />
Loctaion of Intruder <img width="806" height="898" alt="Screenshot 2026-06-19 at 4 49 33 PM" src="https://github.com/user-attachments/assets/d2992387-04e9-4003-9f79-1f3632545f4d" />


---

## 🎥 Demo

A complete demonstration video will be uploaded soon.

---

## 🚧 Future Improvements 

* Voice authentication
* Multi-user support
* Real-time dashboard
* Better UI
* Mobile notifications

---

## ⚠ Disclaimer

This project was created for educational and portfolio purposes. It is intended to demonstrate AI and computer vision concepts and should not be considered a complete commercial security solution.

---

## 👨‍💻 Developer

**Rahul Yadav**

B.Tech Student | AI • Cybersecurity • Computer Vision

If you found this project useful, consider giving it a ⭐ on GitHub.
