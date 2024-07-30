from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFormLayout, QTextEdit, QLabel, QLineEdit, QPushButton, QMessageBox, QInputDialog
from PyQt5.QtCore import Qt
import sys

class NetworkWindow(QWidget):
    def __init__(self, bot_id, conn2):
        super().__init__()

        self.cursor = conn2.cursor()
        self.cursor1 = conn2.cursor()
        self.connection = conn2
        self.bot_id = bot_id
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Edit Site Details")

        # Using QFormLayout for a better form-like UI
        self.form_layout = QFormLayout()


        # Additional fields with password handling
        self.id_edit = QLineEdit()
        self.id_edit.setEnabled(False)
        self.id_edit.setMinimumWidth(400) 
        self.form_layout.addRow(QLabel("ID:"), self.id_edit)

        self.username_edit = QLineEdit()
        self.username_edit.setEnabled(False)
        self.username_edit.setMinimumWidth(400)
        self.form_layout.addRow(QLabel("Username:"), self.username_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setEnabled(False)
        self.password_edit.setMinimumWidth(400) 
        self.form_layout.addRow(QLabel("Password:"), self.password_edit)

        self.ip_address_edit = QLineEdit()
        self.ip_address_edit.setEnabled(False)
        self.ip_address_edit.setMinimumWidth(400)
        self.form_layout.addRow(QLabel("IP Address:"), self.ip_address_edit)

        self.network_hardcore_edit = QLineEdit()
        self.network_hardcore_edit.setEnabled(False)
        self.network_hardcore_edit.setMinimumWidth(400) 
        self.form_layout.addRow(QLabel("Network Hardcore:"), self.network_hardcore_edit)

        self.network_username_edit = QLineEdit()
        self.network_username_edit.setEnabled(False)
        self.network_username_edit.setMinimumWidth(400) 
        self.form_layout.addRow(QLabel("Network Username:"), self.network_username_edit)

        self.network_password_edit = QLineEdit()
        self.network_password_edit.setEchoMode(QLineEdit.Password)
        self.network_password_edit.setEnabled(False)
        self.network_password_edit.setMinimumWidth(400)
        self.form_layout.addRow(QLabel("Network Password:"), self.network_password_edit)

        self.network_ipaddress_edit = QLineEdit()
        self.network_ipaddress_edit.setEnabled(False)
        self.network_ipaddress_edit.setMinimumWidth(400)
        self.form_layout.addRow(QLabel("Network IP Address:"), self.network_ipaddress_edit)

        self.network_stream_edit = QLineEdit()
        self.network_stream_edit.setEnabled(False)
        self.network_stream_edit.setMinimumWidth(400)
        self.form_layout.addRow(QLabel("Network Stream:"), self.network_stream_edit)

        # Button to toggle edit mode
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.toggle_edit_mode)
        self.form_layout.addRow(self.edit_button)

        # Button to save changes
        self.save_button = QPushButton("Save")
        self.save_button.setEnabled(False)  # Initially disabled
        self.save_button.clicked.connect(self.save_profile)
        self.form_layout.addRow(self.save_button)

        self.setLayout(self.form_layout)

        # Load profile details on initialization
        self.load_profile()

    def load_profile(self):
        query = "SELECT * FROM dappusers WHERE id = %s"
        self.cursor.execute(query, (self.bot_id,))
        profile_info = self.cursor.fetchone()  # Fetch one row

        if profile_info:
            (id_value, username_value, password_value, ip_address_value,
             network_hardcore_value, network_username_value, network_password_value,
             network_ipaddress_value, network_stream_value) = profile_info

            

            # Additional fields
            self.id_edit.setText(str(id_value) if id_value is not None else "")
            self.username_edit.setText(username_value if username_value else "")
            self.password_edit.setText(password_value if password_value else "")
            self.ip_address_edit.setText(ip_address_value if ip_address_value else "")
            self.network_hardcore_edit.setText(str(network_hardcore_value) if network_hardcore_value is not None else "")
            self.network_username_edit.setText(network_username_value if network_username_value else "")
            self.network_password_edit.setText(network_password_value if network_password_value else "")
            self.network_ipaddress_edit.setText(network_ipaddress_value if network_ipaddress_value else "")
            self.network_stream_edit.setText(network_stream_value if network_stream_value else "")

    def toggle_edit_mode(self):
        password, ok = QInputDialog.getText(self, 'Password Required', 'Enter password:', QLineEdit.Password)
        query = "SELECT password FROM dappusers WHERE id = %s"
        self.cursor1.execute(query, (self.bot_id,))
        fetched_password = self.cursor1.fetchone()

        db_password = fetched_password[0] if fetched_password else ""

        if ok and password.strip() == db_password:
            # Enable editing
            #self.id_edit.setEnabled(True)
            self.username_edit.setEnabled(True)
            self.password_edit.setEnabled(True)
            self.ip_address_edit.setEnabled(True)
            self.network_hardcore_edit.setEnabled(True)
            self.network_username_edit.setEnabled(True)
            self.network_password_edit.setEnabled(True)
            self.network_ipaddress_edit.setEnabled(True)
            self.network_stream_edit.setEnabled(True)
            self.save_button.setEnabled(True)
        else:
            # Clear password field and disable editing
            QMessageBox.warning(self, "Access Denied", "Incorrect password.")
            self.id_edit.setEnabled(False)
            self.username_edit.setEnabled(False)
            self.password_edit.setEnabled(False)
            self.ip_address_edit.setEnabled(False)
            self.network_hardcore_edit.setEnabled(False)
            self.network_username_edit.setEnabled(False)
            self.network_password_edit.setEnabled(False)
            self.network_ipaddress_edit.setEnabled(False)
            self.network_stream_edit.setEnabled(False)
            self.save_button.setEnabled(False)

    def save_profile(self):
        try:
            

            # Additional fields
            id_value = self.id_edit.text().strip()
            username_value = self.username_edit.text().strip()
            password_value = self.password_edit.text().strip()
            ip_address_value = self.ip_address_edit.text().strip()
            network_hardcore_value = self.network_hardcore_edit.text().strip()
            network_username_value = self.network_username_edit.text().strip()
            network_password_value = self.network_password_edit.text().strip()
            network_ipaddress_value = self.network_ipaddress_edit.text().strip()
            network_stream_value = self.network_stream_edit.text().strip()

            # Basic validation: Check if required fields are empty
            if not username_value:
                QMessageBox.warning(self, "Warning", "Site Name cannot be empty.")
                return

            # Update database with new values
            query = """
                UPDATE dappusers
                SET id = %s, username = %s, password = %s, ip_address = %s,
                    network_hardcore = %s, network_username = %s,
                    network_password = %s, network_ipaddress = %s,
                    network_stream = %s
                WHERE id = %s
            """
            self.cursor.execute(query, (id_value, username_value, password_value,
                                        ip_address_value, network_hardcore_value,
                                        network_username_value, network_password_value,
                                        network_ipaddress_value, network_stream_value,
                                        self.bot_id))

            self.connection.commit()

            # Optionally, display a success message
            QMessageBox.information(self, "Success", "Profile updated successfully!")

            # Disable editing after saving
            self.id_edit.setEnabled(False)
            self.username_edit.setEnabled(False)
            self.password_edit.setEnabled(False)
            self.ip_address_edit.setEnabled(False)
            self.network_hardcore_edit.setEnabled(False)
            self.network_username_edit.setEnabled(False)
            self.network_password_edit.setEnabled(False)
            self.network_ipaddress_edit.setEnabled(False)
            self.network_stream_edit.setEnabled(False)
            self.save_button.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving: {e}")


