from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFormLayout, QTextEdit, QLabel, QLineEdit, QPushButton, QMessageBox, QInputDialog
from PyQt5.QtCore import Qt
import sys

class ProfileWindow(QWidget):
    def __init__(self,  bot_id,conn2):
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

        # Creating labels and line edits for each field
        self.site_name_edit = QLineEdit()
        self.site_name_edit.setEnabled(False)  # Initially disabled
        self.form_layout.addRow(QLabel("Site Name:"), self.site_name_edit)

        self.site_address_edit = QLineEdit()
        self.site_address_edit.setEnabled(False)  # Initially disabled
        self.form_layout.addRow(QLabel("Address:"), self.site_address_edit)

        self.site_postcode_edit = QLineEdit()
        self.site_postcode_edit.setEnabled(False)  # Initially disabled
        self.form_layout.addRow(QLabel("Postcode:"), self.site_postcode_edit)

        self.site_phone_number_edit = QLineEdit()
        self.site_phone_number_edit.setEnabled(False)  # Initially disabled
        self.form_layout.addRow(QLabel("Phone Number:"), self.site_phone_number_edit)

        self.site_email_edit = QLineEdit()
        self.site_email_edit.setEnabled(False)  # Initially disabled
        self.form_layout.addRow(QLabel("Email:"), self.site_email_edit)

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
        query = "SELECT * FROM sitedetails WHERE site_id = %s"
        self.cursor.execute(query, (self.bot_id,))
        profile_info = self.cursor.fetchone()  # Fetch one row

        if profile_info:
            site_id, site_name, site_address, site_postcode, site_phone_number, site_email, _ = profile_info

            # Populate fields with fetched data
            self.site_name_edit.setText(site_name if site_name else "")
            self.site_address_edit.setText(site_address if site_address else "")
            self.site_postcode_edit.setText(site_postcode if site_postcode else "")
            self.site_phone_number_edit.setText(site_phone_number if site_phone_number else "")
            self.site_email_edit.setText(site_email if site_email else "")

    def toggle_edit_mode(self):
        password, ok = QInputDialog.getText(self, 'Password Required', 'Enter password:', QLineEdit.Password)
        query = "SELECT password FROM dappusers WHERE id = %s"
        self.cursor1.execute(query, (self.bot_id,))
        fet_password = self.cursor1.fetchone()  
        
        db_password = fet_password[0]

        if ok and password.strip() == db_password:
            # Enable editing
            self.site_name_edit.setEnabled(True)
            self.site_address_edit.setEnabled(True)
            self.site_postcode_edit.setEnabled(True)
            self.site_phone_number_edit.setEnabled(True)
            self.site_email_edit.setEnabled(True)
            self.save_button.setEnabled(True)
        else:
            # Clear password field and disable editing
            QMessageBox.warning(self, "Access Denied", "Incorrect password.")
            self.site_name_edit.setEnabled(False)
            self.site_address_edit.setEnabled(False)
            self.site_postcode_edit.setEnabled(False)
            self.site_phone_number_edit.setEnabled(False)
            self.site_email_edit.setEnabled(False)
            self.save_button.setEnabled(False)

    def save_profile(self):
        try:
            # Get updated values from line edits
            site_name = self.site_name_edit.text().strip()
            site_address = self.site_address_edit.text().strip()
            site_postcode = self.site_postcode_edit.text().strip()
            site_phone_number = self.site_phone_number_edit.text().strip()
            site_email = self.site_email_edit.text().strip()

            # Basic validation: Check if required fields are empty
            if not site_name:
                QMessageBox.warning(self, "Warning", "Site Name cannot be empty.")
                return

            # Update database with new values
            query = """
                UPDATE sitedetails
                SET site_name = %s, site_address = %s, site_postcode = %s,
                    site_phone_number = %s, site_email = %s
                WHERE site_id = %s
            """
            self.cursor.execute(query, (site_name, site_address, site_postcode, site_phone_number, site_email, self.bot_id))

            
            self.connection.commit()

            # Optionally, display a success message
            QMessageBox.information(self, "Success", "Profile updated successfully!")

            # Disable editing after saving
            self.site_name_edit.setEnabled(False)
            self.site_address_edit.setEnabled(False)
            self.site_postcode_edit.setEnabled(False)
            self.site_phone_number_edit.setEnabled(False)
            self.site_email_edit.setEnabled(False)
            self.save_button.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving: {e}")

# Example usage:
# if __name__ == '__main__':
#     app = QApplication([])
#     connection = # Your database connection
#     cursor = connection.cursor()
#     cursor2 = connection.cursor() # Assuming the same connection can be used for both cursors
#     window = ProfileWindow(cursor, bot_id, cursor2, connection)
#     window.show()
#     sys.exit(app.exec_())
