from mysql.connector import Error

class PatientService:
    def __init__(self, db):
        self.db = db

    def add_patient(self, name: str, email: str) -> int:
        query = "INSERT INTO patients (name, email) VALUES (%s, %s)"
        try:
            self.db.cursor.execute(query, (name, email))
            self.db.connection.commit()
            return self.db.cursor.lastrowid
        except Error as e:
            print(f"Error adding patient: {e}")
            return None

    def get_patient(self, patient_id: int) -> tuple:
        query = "SELECT id, name, email FROM patients WHERE id = %s"
        try:
            self.db.cursor.execute(query, (patient_id,))
            return self.db.cursor.fetchone()
        except Error as e:
            print(f"Error fetching patient: {e}")
            return None

    def get_all_patients(self) -> list:
        query = "SELECT id, name, email FROM patients"
        try:
            self.db.cursor.execute(query)
            return self.db.cursor.fetchall()
        except Error as e:
            print(f"Error fetching patients: {e}")
            return []

    def update_patient(self, patient_id: int, name: str, email: str) -> bool:
        query = "UPDATE patients SET name = %s, email = %s WHERE id = %s"
        try:
            self.db.cursor.execute(query, (name, email, patient_id))
            self.db.connection.commit()
            return self.db.cursor.rowcount > 0
        except Error as e:
            print(f"Error updating patient: {e}")
            self.db.connection.rollback()
            return False

    def delete_patient(self, patient_id: int) -> bool:
        check_query = "SELECT COUNT(*) FROM appointments WHERE patient_id = %s"
        try:
            self.db.cursor.execute(check_query, (patient_id,))
            appt_count = self.db.cursor.fetchone()[0]
            if appt_count > 0:
                print(f"Error: Patient ID {patient_id} has {appt_count} associated appointments")
                return False
            delete_query = "DELETE FROM patients WHERE id = %s"
            self.db.cursor.execute(delete_query, (patient_id,))
            self.db.connection.commit()
            return self.db.cursor.rowcount > 0
        except Error as e:
            print(f"Error deleting patient: {e}")
            self.db.connection.rollback()
            return False

    def get_patient_appointments(self, patient_id: int) -> list:
        query = """
        SELECT a.id, d.name, s.date, s.start_time, s.end_time
        FROM appointments a
        JOIN appointment_slots s ON a.slot_id = s.id
        JOIN doctors d ON s.doctor_id = d.id
        WHERE a.patient_id = %s
        """
        try:
            self.db.cursor.execute(query, (patient_id,))
            return self.db.cursor.fetchall()
        except Error as e:
            print(f"Error fetching patient appointments: {e}")
            return []