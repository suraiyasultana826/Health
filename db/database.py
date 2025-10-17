import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

class Database:
    def __init__(self, env_file: str = ".env.local"):
        self.connection = None
        self.cursor = None
        
        # Load environment variables
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        dotenv_path = os.path.join(root, env_file)
        
        if not os.path.exists(dotenv_path):
            raise FileNotFoundError(f"Environment file {dotenv_path} not found")
        
        load_dotenv(dotenv_path)
        
        # Retrieve and validate environment variables
        host = os.getenv('HOST')
        user = os.getenv('USER')
        password = os.getenv('PASSWORD')
        database = os.getenv('DATABASE')
        port = os.getenv('PORT')
        
        required_vars = {'HOST': host, 'USER': user, 'PASSWORD': password, 'DATABASE': database, 'PORT': port}
        missing_vars = [key for key, value in required_vars.items() if value is None]
        if missing_vars:
            raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")
        
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=int(port)  # Ensure port is an integer
            )
            self.cursor = self.connection.cursor()
        except Error as e:
            raise ConnectionError(f"Error connecting to MySQL: {e}") from e

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
            raise RuntimeError(f"Error creating schema: {e}") from e

    def close(self):
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()