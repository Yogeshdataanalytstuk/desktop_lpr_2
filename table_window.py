import sys
import mysql.connector
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QSizePolicy
from PyQt5.QtCore import Qt


class TableWindow(QWidget):
    def __init__(self, bot_id, conn):
        super().__init__()

        self.cursor = conn.cursor()
        self.bot_id = bot_id

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Top 20 Plate Numbers")

        main_layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        title = QLabel("Top 20 Plate Numbers")
        title.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(title)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setStyleSheet("background-color: blue; color: white;")
        self.refresh_button.clicked.connect(self.load_data)
        top_layout.addWidget(self.refresh_button, alignment=Qt.AlignRight)

        main_layout.addLayout(top_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Plate Number", "Date", "Time"])
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, self.table.horizontalHeader().Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, self.table.horizontalHeader().Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, self.table.horizontalHeader().Stretch)
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

        self.load_data()

    def load_data(self):
    # Close existing cursor and connection if open
        if self.cursor:
            self.cursor.close()
        
        # Re-establish the connection and cursor
        self.conn = mysql.connector.connect(
            host='lpr-1.c7c60yyc479j.eu-west-2.rds.amazonaws.com',
            user='ndsadmin',
            passwd='ndsadmin',
            database='lprv1'
        )
        self.cursor = self.conn.cursor()

        print("Loading data...")  # Debugging statement

        query = """
        SELECT plate_number, timestamp
        FROM numberplates
        WHERE user_id = %s
        ORDER BY timestamp DESC
        LIMIT 20
        """

        self.cursor.execute(query, (self.bot_id,))
        results = self.cursor.fetchall()

        print(f"Number of records fetched: {len(results)}")  # Debugging statement

        self.table.setRowCount(len(results))
        for row_idx, (plate_number, timestamp) in enumerate(results):
            date = timestamp.strftime("%Y-%m-%d")
            time = timestamp.strftime("%H:%M:%S")
            self.table.setItem(row_idx, 0, QTableWidgetItem(plate_number))
            self.table.setItem(row_idx, 1, QTableWidgetItem(date))
            self.table.setItem(row_idx, 2, QTableWidgetItem(time))

        print("Data loaded successfully")  # Debugging statement


