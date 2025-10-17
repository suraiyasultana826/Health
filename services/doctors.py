from mysql.connector import Error

class DoctorService:
    def __init__(self, db):
        self.db = db

    def add_doctor(self, name, specialty):
        query = "INSERT INTO doctors (name, specialty) VALUES (%s, %s)"
        try:
            self.db.cursor.execute(query, (name, specialty))
            self.db.connection.commit()
            return self.db.cursor.lastrowid
        except Error as e:
            print(f"Error adding doctor: {e}")
            return None

    def get_doctor_availability(self, doctor_id, date):
        query = """
        SELECT s.id, s.date, s.start_time, s.end_time
        FROM appointment_slots s
        WHERE s.doctor_id = %s AND s.date = %s AND s.is_available = TRUE
        """
        try:
            self.db.cursor.execute(query, (doctor_id, date))
            return self.db.cursor.fetchall()
        except Error as e:
            print(f"Error fetching availability: {e}")
            return []