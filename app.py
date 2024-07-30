from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QFrame, \
    QSpacerItem, QSizePolicy, QMenuBar, QMenu, QAction, QGridLayout, QLineEdit, QTabWidget, QTextEdit, QMessageBox

from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QFont, QPalette, QColor, QMovie
import sys
import os
import threading
import queue
import requests
import cv2
import numpy as np
import mysql.connector
from app_support_model import DetectionPipeline
from profile_window import ProfileWindow 
from network_window import NetworkWindow 
from table_window import TableWindow 
from webuser_window import WebuserWindow 


def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
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
                        frame = cv2.resize(frame, (1920, 1080))
                        if self.count % 2 == 0:
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
    def __init__(self, ip_address, bot_id, username):
        super().__init__()
        self.stream_handler = VideoStreamHandler(ip_address, bot_id, username)
        self.bot_id=bot_id
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Video Stream')
        self.setGeometry(500, 500, 800, 600)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

        # Main video tab
        self.video_tab = QWidget()
        
        self.initVideoTab()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def initVideoTab(self):
        main_layout = QVBoxLayout()

        menubar = QMenuBar(self)
        file_menu = QMenu('Settings', self)
        profile_action = QAction('Profile', self)
        Network_action = QAction('Network', self)
        webuser_action = QAction('Web User Management', self)
        logout_action = QAction('Logout', self)

        profile_action.triggered.connect(self.show_profile)
        Network_action.triggered.connect(self.network)
        webuser_action.triggered.connect(self.webuser)
        logout_action.triggered.connect(self.logout)
        
        file_menu.addAction(profile_action)
        file_menu.addAction(Network_action)
        file_menu.addAction(webuser_action)
        file_menu.addAction(logout_action)

        


        menubar.addMenu(file_menu)


        analytics_menu = QMenu('Analytics', self)
        view_analytics_action = QAction('Data Table', self)
        

        view_analytics_action.triggered.connect(self.view_analytics)
        

        analytics_menu.addAction(view_analytics_action)
        

        menubar.addMenu(analytics_menu)
        main_layout.addWidget(menubar)
        main_layout.setMenuBar(menubar)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        main_layout.addItem(spacer)

        self.image_label = QLabel(self)
        main_layout.addWidget(self.image_label)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        self.tab_widget.addTab(main_widget, 'Video Stream')

    def update_frame(self):
        frame = self.stream_handler.get_frame()
        if frame is not None:
            display_frame = cv2.resize(frame, (800, 450))
            display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            image = QImage(display_frame.data, display_frame.shape[1], display_frame.shape[0], display_frame.strides[0], QImage.Format_RGB888)
            self.image_label.setPixmap(QPixmap.fromImage(image))

    def closeEvent(self, event):
        self.stream_handler.stop()

    def logout(self):
        self.stream_handler.stop()
        self.close()
        QApplication.quit()

    def show_profile(self):
        
        profile_window = ProfileWindow(self.bot_id,conn2)  
        self.tab_widget.addTab(profile_window, 'Profile')


    def network(self):
        network_window = NetworkWindow(self.bot_id,conn3)
        self.tab_widget.addTab(network_window,'Network')

    def view_analytics(self):
        network_window = TableWindow(self.bot_id,conn4)
        self.tab_widget.addTab(network_window,'Table')
    def webuser(self):
        webuser_window= WebuserWindow(self.bot_id,conn5)
        self.tab_widget.addTab(webuser_window,'Web Login Crentails')


    def close_tab(self, index):
        if index != 0:  # Ensure we don't close the Video Stream tab by mistake
            widget = self.tab_widget.widget(index)
            if widget:
                widget.deleteLater()
                self.tab_widget.removeTab(index)
    
    






class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.session = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('ND SPECTRA LPR(License Plate Recognition)')
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
        self.username_entry.setMinimumWidth(50)
        self.username_entry.setFixedSize(200, 30)
        self.username_entry.setStyleSheet("border-radius: 5px; padding: 5px;")
        layout.addWidget(self.username_entry, 0, 2)

        self.password_label = QLabel('Password:', self)
        self.password_label.setFont(label_font)
        self.password_label.setStyleSheet("color: black;")
        layout.addWidget(self.password_label, 1, 1)
        self.password_entry = QLineEdit(self)
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.setMinimumHeight(30)
        self.password_entry.setMinimumWidth(50)
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
        layout.addWidget(login_button, 2, 0, 1, 4, alignment=Qt.AlignCenter)

        layout.setRowStretch(3, 1)

        gif_label = QLabel(self)
        movie = QMovie(resource_path('resources/logo.gif'))
        movie.setScaledSize(QSize(100, 60))
        gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(gif_label, 4, 3, Qt.AlignRight | Qt.AlignBottom)

        self.setLayout(layout)

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))
        self.setPalette(palette)

    def verify_login(self):
        username = self.username_entry.text()
        password = self.password_entry.text()
        try:
            cursor2.execute("SELECT * FROM dappusers WHERE username=%s AND password=%s", (username, password))
            user = cursor2.fetchone()
            if user:
                if user[4]==1:
                    
                    ip_address = user[3]
                    bot_id = user[0]
                    cursor.execute("SELECT * FROM webusers WHERE id_number=%s", (bot_id,))
                    rows = cursor.fetchall()
                    if rows:
                        user_data = rows[0]
                        username_from_db = user_data[1]
                        password_from_db = user_data[2]
                        self.open_video_window(ip_address, bot_id, username_from_db)
                    else:
                        QMessageBox.critical(self, 'Login Failed', 'User with provided ID not found. Contact ND-SPECTRA')
                else:
                    
                    usr=user[5]
                    pwd=user[6]
                    ip=user[7]
                    path=user[8]
                    scheme='rtsp'
                    

                    ip_address = f'{scheme}://{usr}:{pwd}@{ip}/{path}'
                    bot_id = user[0]
                    cursor.execute("SELECT * FROM webusers WHERE id_number=%s", (bot_id,))
                    rows = cursor.fetchall()
                    if rows:
                        user_data = rows[0]
                        username_from_db = user_data[1]
                        password_from_db = user_data[2]
                        self.open_video_window(ip_address, bot_id, username_from_db)
                    else:
                        QMessageBox.critical(self, 'Login Failed', 'User with provided ID not found. Contact ND-SPECTRA')

            else:
                QMessageBox.critical(self, 'Login Failed', 'Invalid Username or Password')
        except mysql.connector.Error as e:
            QMessageBox.critical(self, 'Login Failed', f'Database error: {str(e)}')
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, 'Login Failed', f'Request error: {str(e)}')

    def open_video_window(self, ip_address, bot_id, username_from_db):
        self.video_window = VideoWindow(ip_address, bot_id, username_from_db)
        self.video_window.show()
        self.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    conn = create_db_connection()
    conn2=create_db_connection()
    conn3=create_db_connection()
    conn4=create_db_connection()
    conn5=create_db_connection()
    cursor = conn.cursor()
    cursor2 = conn.cursor()
    
    
    pipeline = DetectionPipeline()
    ex = LoginWindow()
    ex.show()
    sys.exit(app.exec_())
