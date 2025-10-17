class PatientService:
    def __init__(self, db):
        self.db = db

    def add_patient(self, name, email):
        query = "INSERT INTO patients (name, email) VALUES (%s, %s)"
        try:
            self.db.cursor.execute(query, (name, email))
            self.db.connection.commit()
            return self.db.cursor.lastrowid
        except Error as e:
            print(f"Error adding patient: {e}")
            return None

    def get_patient_appointments(self, patient_id):
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