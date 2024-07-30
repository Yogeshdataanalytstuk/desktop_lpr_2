import sys
import os
import threading
import queue
import requests
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QSpacerItem, QSizePolicy, QGridLayout
from PyQt6.QtCore import QTimer, Qt, QSize
from PyQt6.QtGui import QImage, QPixmap, QFont, QPalette, QColor, QMovie
from app_support_model import DetectionPipeline
import mysql.connector

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def create_db_connection():
    return mysql.connector.connect(
        host='lpr-1.c7c60yyc479j.eu-west-2.rds.amazonaws.com',
        user='ndsadmin',
        passwd='ndsadmin',
        database='lprv1'
    )

class VideoStreamHandler:
    def __init__(self, ip_address, username, password):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.cap = cv2.VideoCapture(self.ip_address)
        self.frame_queue = queue.Queue(maxsize=10)
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.capture_frames)
        self.thread.start()
        self.count = 0

    def capture_frames(self):
        while not self.stop_event.is_set():
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    try:
                        self.count += 1
                        frame = cv2.resize(frame, (1920, 720))
                        if self.count % 7 == 0:
                            print(self.count, self.username, self.password)
                            pipeline.add_frame(frame, self.count, self.username, self.password)
                        if not self.frame_queue.full():
                            self.frame_queue.put(frame)
                        else:
                            print("Dropping frame to catch up...")
                    except cv2.error as e:
                        print(f"Error processing frame: {e}")
                else:
                    print("Failed to read frame, reconnecting...")
                    self.reconnect_stream()
            else:
                print("Reconnecting...")
                self.reconnect_stream()

    def get_frame(self):
        if not self.frame_queue.empty():
            return self.frame_queue.get()
        return None

    def reconnect_stream(self):
        self.cap.release()
        self.cap = cv2.VideoCapture(self.ip_address)

    def stop(self):
        self.stop_event.set()
        self.thread.join()
        if self.cap:
            self.cap.release()

class VideoWindow(QWidget):
    def __init__(self, ip_address, username, password):
        super().__init__()
        self.stream_handler = VideoStreamHandler(ip_address, username, password)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Video Stream')
        self.setGeometry(500, 500, 800, 600)
        self.image_label = QLabel(self)
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        self.logout_button = QPushButton('Logout', self)
        self.logout_button.clicked.connect(self.logout)
        layout.addWidget(self.logout_button)
        self.setLayout(layout)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        frame = self.stream_handler.get_frame()
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format.Format_RGB888)
            self.image_label.setPixmap(QPixmap.fromImage(image))

    def closeEvent(self, event):
        self.stream_handler.stop()

    def logout(self):
        self.stream_handler.stop()
        self.close()

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.session = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('ND SPECTRA LPR (License Plate Recognition)')
        self.setGeometry(325, 325, 600, 400)
        layout = QGridLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        label_font = QFont()
        label_font.setPointSize(12)
        label_font.setBold(True)
        self.username_label = QLabel('Username:', self)
        self.username_label.setFont(label_font)
        self.username_label.setStyleSheet("color: black;")
        layout.addWidget(self.username_label, 0, 1)
        self.username_entry = QLineEdit(self)
        self.username_entry.setMinimumHeight(30)
        self.username_entry.setFixedSize(200, 30)
        self.username_entry.setStyleSheet("border-radius: 5px; padding: 5px;")
        layout.addWidget(self.username_entry, 0, 2)
        self.password_label = QLabel('Password:', self)
        self.password_label.setFont(label_font)
        self.password_label.setStyleSheet("color: black;")
        layout.addWidget(self.password_label, 1, 1)
        self.password_entry = QLineEdit(self)
        self.password_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_entry.setMinimumHeight(30)
        self.password_entry.setFixedSize(200, 30)
        self.password_entry.setStyleSheet("border-radius: 5px; padding: 5px;")
        layout.addWidget(self.password_entry, 1, 2)
        login_button = QPushButton('Login', self)
        login_button.setFont(QFont('Arial', 12))
        login_button.setMinimumHeight(40)
        login_button.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: darkred;
            }
        """)
        login_button.clicked.connect(self.verify_login)
        layout.addWidget(login_button, 2, 0, 1, 4, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.setRowStretch(3, 1)
        gif_label = QLabel(self)
        movie = QMovie(resource_path('resources/logo.gif'))
        movie.setScaledSize(QSize(100, 60))
        gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(gif_label, 4, 3, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self.setLayout(layout)
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
        self.setPalette(palette)

    def verify_login(self):
        username = self.username_entry.text()
        password = self.password_entry.text()
        try:
            cursor2.execute("SELECT * FROM dappusers WHERE username=%s AND password=%s", (username, password))
            user = cursor2.fetchone()
            if user:
                ip_address = user[3]
                bot_id = user[0]
                cursor.execute("SELECT * FROM webusers WHERE id_number=%s", (bot_id,))
                rows = cursor.fetchall()
                if rows:
                    user_data = rows[0]
                    username_from_db = user_data[1]
                    password_from_db = user_data[2]
                    login_data = {'username': username_from_db, 'password': password_from_db}
                    if self.session is None:
                        login_url = 'http://3.10.140.34/login'
                        session = requests.Session()
                        self.session = session
                        response = session.post(login_url, data=login_data)
                        if response.status_code == 200:
                            self.open_video_window(ip_address, username, password)
                        else:
                            QMessageBox.critical(self, 'Login Failed', 'Unable to login to remote service')
                    else:
                        QMessageBox.critical(self, 'Login Failed', 'Session already exists')
                else:
                    QMessageBox.critical(self, 'Login Failed', 'User with provided ID not found. Contact ND-SPECTRA')
            else:
                QMessageBox.critical(self, 'Login Failed', 'Invalid Username or Password')
        except mysql.connector.Error as e:
            QMessageBox.critical(self, 'Login Failed', f'Database error: {str(e)}')
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, 'Login Failed', f'Request error: {str(e)}')

    def open_video_window(self, ip_address, username, password):
        self.video_window = VideoWindow(ip_address, username, password)
        self.video_window.show()
        self.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    conn = create_db_connection()
    cursor = conn.cursor()
    cursor2 = conn.cursor()
    pipeline = DetectionPipeline()
    ex = LoginWindow()
    ex.show()
    sys.exit(app.exec())
