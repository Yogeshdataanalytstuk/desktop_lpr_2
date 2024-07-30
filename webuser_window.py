from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFormLayout, QTextEdit, QLabel, QLineEdit, QPushButton, QMessageBox, QInputDialog, QListWidget, QHBoxLayout
from PyQt5.QtCore import Qt
import sys
from werkzeug.security import generate_password_hash, check_password_hash

class WebuserWindow(QWidget):
    def __init__(self, bot_id, conn2):
        super().__init__()
        
        self.cursor = conn2.cursor()
        self.connection = conn2
        self.bot_id = bot_id
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Edit Site Details")

        # Main layout
        self.main_layout = QVBoxLayout()

        # List widget to display all users
        self.user_list = QListWidget()
        self.user_list.itemClicked.connect(self.load_profile)
        self.main_layout.addWidget(self.user_list)

        # Form layout for profile details
        self.form_layout = QFormLayout()

        self.username_edit = QLineEdit()
        self.username_edit.setEnabled(False)  # Initially disabled
        self.form_layout.addRow(QLabel("Username:"), self.username_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setEnabled(False)  # Initially disabled
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.form_layout.addRow(QLabel("Password:"), self.password_edit)

        self.id_number_edit = QLineEdit()
        self.id_number_edit.setEnabled(False)  # Initially disabled
        self.form_layout.addRow(QLabel("ID Number:"), self.id_number_edit)


        self.id_edit = QLineEdit()
        self.id_edit.setEnabled(False)  # Initially disabled
        self.form_layout.addRow(QLabel("ID :"), self.id_edit)
        # Buttons layout
        self.button_layout = QHBoxLayout()
        
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.toggle_edit_mode)
        self.button_layout.addWidget(self.edit_button)

        self.save_button = QPushButton("Save")
        self.save_button.setEnabled(False)  # Initially disabled
        self.save_button.clicked.connect(self.save_profile)
        self.button_layout.addWidget(self.save_button)

        self.add_button = QPushButton("Add User")
        self.add_button.clicked.connect(self.add_user_dialog)  # Connect to dialog method
        self.button_layout.addWidget(self.add_button)

        self.delete_button = QPushButton("Delete User")
        self.delete_button.clicked.connect(self.delete_user)  # Connect delete_user method here
        self.button_layout.addWidget(self.delete_button)

        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addLayout(self.button_layout)

        self.setLayout(self.main_layout)

        # Load users list on initialization
        self.load_users_list()

    def load_users_list(self):
        query = "SELECT id_number, username ,id FROM webusers WHERE id_number = %s"
        self.cursor.execute(query, (self.bot_id,))
        users = self.cursor.fetchall()

        self.user_list.clear()
        for user in users:
            id_number, username,id = user
            self.user_list.addItem(f"{username} (ID: {id})")

    def load_profile(self, item):
        user_info = item.text()
        id = user_info.split("(ID: ")[1][:-1]
        
        query = "SELECT username, password, id_number ,id FROM webusers WHERE id = %s"
        self.cursor.execute(query, (id,))
        
        # Fetch the result immediately after executing the query
        profile_info = self.cursor.fetchone()

        # Clear any unread results if present
        self.cursor.fetchall()

        if profile_info:
            username, password, id_number ,id= profile_info
            self.username_edit.setText(username if username else "")
            self.password_edit.setText("*****")
            self.id_number_edit.setText(id_number if id_number else "")
            self.id_edit.setText(str(id) if id else "")
        else:
            QMessageBox.warning(self, "Error", "Profile not found.")

    def toggle_edit_mode(self):
        password, ok = QInputDialog.getText(self, 'Password Required', 'Enter password:', QLineEdit.Password)
        
        if ok:
            query = "SELECT password FROM dappusers WHERE id = %s"
            self.cursor.execute(query, (self.bot_id,))
            
            fetched_password = self.cursor.fetchone()
            
            # Clear any unread results if present
            self.cursor.fetchall()
            
            if fetched_password:
                db_password = fetched_password[0]

                if password.strip() == db_password:
                    self.username_edit.setEnabled(True)
                    self.password_edit.setEnabled(True)
                    self.id_number_edit.setEnabled(True)
                    self.save_button.setEnabled(True)
                else:
                    QMessageBox.warning(self, "Access Denied", "Incorrect password.")
                    self.username_edit.setEnabled(False)
                    self.password_edit.setEnabled(False)
                    self.id_number_edit.setEnabled(False)
                    self.save_button.setEnabled(False)
            else:
                QMessageBox.warning(self, "Error", "User not found.")

    def save_profile(self):
        try:
            username = self.username_edit.text().strip()
            password = self.password_edit.text().strip()
            id_number = self.id_number_edit.text().strip()
            id = self.id_edit.text().strip()
            

            if not username or not id_number:
                QMessageBox.warning(self, "Warning", "All fields except password must be filled.")
                return

            if password != "*****":
                confirm_password, ok = QInputDialog.getText(self, 'Confirm Password', 'Re-enter new password:', QLineEdit.Password)
                
                if ok and password == confirm_password:
                    password_hash = generate_password_hash(password, method='pbkdf2:sha256')
                else:
                    QMessageBox.warning(self, "Warning", "Passwords do not match.")
                    return
            else:
                query = "SELECT password FROM webusers WHERE id_number = %s"
                self.cursor.execute(query, (id_number,))
                password_hash = self.cursor.fetchone()[0]

            query = """
                UPDATE webusers
                SET username = %s, password = %s
                WHERE id_number = %s AND id = %s
            """
            self.cursor.execute(query, (username, password_hash, id_number,id ))
            self.connection.commit()

            QMessageBox.information(self, "Success", "Profile updated successfully!")

            self.username_edit.setEnabled(False)
            self.password_edit.setEnabled(False)
            self.id_number_edit.setEnabled(False)
            self.save_button.setEnabled(False)

            self.load_users_list()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving: {e}")

    def add_user_dialog(self):
        username, ok = QInputDialog.getText(self, 'Add User', 'Enter username:')
        if ok and username:
            username = username.strip()
            if not username:
                QMessageBox.warning(self, "Warning", "Username cannot be empty.")
                return

            password, ok = QInputDialog.getText(self, 'Add User', 'Enter password:', QLineEdit.Password)
            if ok and password:
                confirm_password, ok = QInputDialog.getText(self, 'Add User', 'Re-enter password:', QLineEdit.Password)
                if ok and password == confirm_password:
                    password_hash = generate_password_hash(password, method='pbkdf2:sha256')

                    query = "INSERT INTO webusers (username, password, id_number) VALUES (%s, %s, %s)"
                    self.cursor.execute(query, (username, password_hash, self.bot_id))
                    self.connection.commit()

                    QMessageBox.information(self, "Success", "User added successfully!")
                    self.load_users_list()
                else:
                    QMessageBox.warning(self, "Warning", "Passwords do not match.")
        else:
            QMessageBox.warning(self, "Warning", "Username cannot be empty.")

    def delete_user(self):
        current_item = self.user_list.currentItem()
        if current_item:
            user_info = current_item.text()
            id = user_info.split("(ID: ")[1][:-1]

            confirm_delete = QMessageBox.question(self, "Confirm Delete", 
                                                  f"Delete user with ID number {id}?",
                                                  QMessageBox.Yes | QMessageBox.No)

            if confirm_delete == QMessageBox.Yes:
                query = "DELETE FROM webusers WHERE id = %s"
                self.cursor.execute(query, (id,))
                self.connection.commit()

                QMessageBox.information(self, "Success", "User deleted successfully!")
                self.load_users_list()


