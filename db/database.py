import mysql.connector
from dotenv import load_dotenv
import os
from mysql.connector import Error

class Database:
    def __init__(self):
        self.connection = None
        try:
            root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            dotenv_path = os.path.join(root, '.env.local')
            load_dotenv(dotenv_path)

            host = os.getenv('HOST')
            user = os.getenv('USER')
            password = os.getenv('PASSWORD')
            database = os.getenv('DATABASE')
            port = os.getenv('PORT')
            print(f" |||||||||||||||||||||| Connecting to database at {host} with user {user}")
        except Exception as e:
            print(f"Error: {e}")
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            )
            self.cursor = self.connection.cursor()
        except Error as e:
            print(f"Error connecting to MySQL: {e}")

    def create_schema(self):
        schema = """
        CREATE TABLE IF NOT EXISTS doctors (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            specialty VARCHAR(100) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS patients (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS appointment_slots (
            id INT AUTO_INCREMENT PRIMARY KEY,
            doctor_id INT,
            date DATE NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            is_available BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        );

        CREATE TABLE IF NOT EXISTS appointments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_id INT,
            slot_id INT,
            booked_at DATETIME NOT NULL,
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (slot_id) REFERENCES appointment_slots(id)
        );

        CREATE TABLE IF NOT EXISTS cancellations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            appointment_id INT,
            reason VARCHAR(255),
            cancelled_at DATETIME NOT NULL,
            FOREIGN KEY (appointment_id) REFERENCES appointments(id)
        );
        """
        try:
            for statement in schema.split(';'):
                if statement.strip():
                    self.cursor.execute(statement)
            self.connection.commit()
        except Error as e:
            print(f"Error creating schema: {e}")

    def close(self):
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()