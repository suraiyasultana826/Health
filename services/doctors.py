from mysql.connector import Error

class DoctorService:
    def __init__(self, db):
        self.db = db

    def add_doctor(self, name: str, specialty: str) -> int:
        query = "INSERT INTO doctors (name, specialty) VALUES (%s, %s)"
        try:
            self.db.cursor.execute(query, (name, specialty))
            self.db.connection.commit()
            return self.db.cursor.lastrowid
        except Error as e:
            print(f"Error adding doctor: {e}")
            return None

    def get_doctor_availability(self, doctor_id: int, date: str) -> list:
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

    def get_all_doctors(self) -> list:
        query = "SELECT id, name, specialty FROM doctors"
        try:
            self.db.cursor.execute(query)
            return self.db.cursor.fetchall()
        except Error as e:
            print(f"Error fetching doctors: {e}")
            return []

    def delete_doctor(self, doctor_id: int) -> bool:
        # Check if doctor has associated appointment slots
        check_query = """
        SELECT COUNT(*) FROM appointment_slots s
        WHERE s.doctor_id = %s
        """
        try:
            self.db.cursor.execute(check_query, (doctor_id,))
            slot_count = self.db.cursor.fetchone()[0]
            if slot_count > 0:
                print(f"Error: Doctor ID {doctor_id} has {slot_count} associated appointment slots")
                return False

            # Delete doctor if no dependencies
            delete_query = "DELETE FROM doctors WHERE id = %s"
            self.db.cursor.execute(delete_query, (doctor_id,))
            self.db.connection.commit()
            return self.db.cursor.rowcount > 0
        except Error as e:
            print(f"Error deleting doctor: {e}")
            self.db.connection.rollback()
            return False