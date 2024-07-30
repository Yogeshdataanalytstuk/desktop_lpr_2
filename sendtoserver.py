import requests
import re
from datetime import datetime
import myocr as ocr
import mysql.connector

import mysql.connector
from mysql.connector import Error

def create_db_connection():
    """Create a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host='lpr-1.c7c60yyc479j.eu-west-2.rds.amazonaws.com',
            user='ndsadmin',
            passwd='ndsadmin',
            database='lprv1'
        )
        print("Connected to MySQL database")
        return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def clean_plate(plate):
    """Clean the plate number to remove any non-alphanumeric characters."""
    return re.sub('[^A-Za-z0-9]', '', plate)

def send_plate(numberplate, bot_id, username_from_db):
    """
    Send the plate number to the server.

    Parameters:
    - numberplate: The image or data to be processed by OCR.
    - bot_id: ID of the bot/user.
    - username_from_db: Username associated with the bot/user.

    Returns:
    - The cleaned plate data if successful, None otherwise.
    """
    conn = create_db_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Use OCR to get the plate number
            plate = ocr.numperpred(numberplate)
            clean_plate_data = clean_plate(plate)
            print("clean_plate_data:", clean_plate_data)

            # Ensure cleaned plate data is valid
            if len(clean_plate_data) ==7 and len(clean_plate_data) <=7:
                # Prepare the data for insertion
                user_id = bot_id  # Assume session contains user ID
                timestamp = datetime.now()

                # SQL statement for insertion
                insert_query = """
                    INSERT INTO numberplates (user_id, plate_number, timestamp)
                    VALUES (%s, %s, %s)
                """

                # Data to be inserted
                record_to_insert = (user_id, clean_plate_data, timestamp)

                # Execute the insert query
                cursor.execute(insert_query, record_to_insert)

                # Commit changes to the database
                conn.commit()

                print("Record inserted successfully")
                return clean_plate_data
            else:
                print("No valid plate data to send.")
                return None

        except mysql.connector.Error as error:
            print(f"Error inserting record into numberplates table: {error}")

        finally:
            # Close cursor and connection
            if 'cursor' in locals():
                cursor.close()
            conn.close()
            print("MySQL connection closed")

    else:
        print("Failed to connect to MySQL database")
        return None
