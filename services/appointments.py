from mysql.connector import Error

class AppointmentService:
    def __init__(self, db):
        self.db = db

    def book_appointment(self, patient_id: int, slot_id: int) -> int:
        check_slot = "SELECT id FROM appointment_slots WHERE id = %s AND is_available = TRUE"
        check_patient = "SELECT id FROM patients WHERE id = %s"
        try:
            self.db.cursor.execute(check_slot, (slot_id,))
            if not self.db.cursor.fetchone():
                print(f"Error: Slot ID {slot_id} is invalid or unavailable")
                return None
            self.db.cursor.execute(check_patient, (patient_id,))
            if not self.db.cursor.fetchone():
                print(f"Error: Patient ID {patient_id} is invalid")
                return None
            query = """
            INSERT INTO appointments (patient_id, slot_id, booked_at)
            VALUES (%s, %s, NOW())
            """
            update_slot = "UPDATE appointment_slots SET is_available = FALSE WHERE id = %s"
            self.db.cursor.execute(query, (patient_id, slot_id))
            self.db.cursor.execute(update_slot, (slot_id,))
            self.db.connection.commit()
            return self.db.cursor.lastrowid
        except Error as e:
            print(f"Error booking appointment: {e}")
            self.db.connection.rollback()
            return None

    def get_appointment(self, appointment_id: int) -> tuple:
        query = """
        SELECT a.id, p.name, d.name, s.date, s.start_time, s.end_time
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN appointment_slots s ON a.slot_id = s.id
        JOIN doctors d ON s.doctor_id = d.id
        WHERE a.id = %s
        """
        try:
            self.db.cursor.execute(query, (appointment_id,))
            return self.db.cursor.fetchone()
        except Error as e:
            print(f"Error fetching appointment: {e}")
            return None

    def get_all_appointments(self) -> list:
        query = """
        SELECT a.id, p.name, d.name, s.date, s.start_time, s.end_time
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN appointment_slots s ON a.slot_id = s.id
        JOIN doctors d ON s.doctor_id = d.id
        """
        try:
            self.db.cursor.execute(query)
            return self.db.cursor.fetchall()
        except Error as e:
            print(f"Error fetching appointments: {e}")
            return []

    def update_appointment(self, appointment_id: int, patient_id: int, slot_id: int) -> bool:
        check_slot = "SELECT id FROM appointment_slots WHERE id = %s AND is_available = TRUE"
        check_patient = "SELECT id FROM patients WHERE id = %s"
        try:
            self.db.cursor.execute(check_slot, (slot_id,))
            if not self.db.cursor.fetchone():
                print(f"Error: Slot ID {slot_id} is invalid or unavailable")
                return False
            self.db.cursor.execute(check_patient, (patient_id,))
            if not self.db.cursor.fetchone():
                print(f"Error: Patient ID {patient_id} is invalid")
                return False
            # Free up the old slot
            free_slot_query = """
            UPDATE appointment_slots s
            JOIN appointments a ON s.id = a.slot_id
            SET s.is_available = TRUE
            WHERE a.id = %s
            """
            update_query = """
            UPDATE appointments
            SET patient_id = %s, slot_id = %s, booked_at = NOW()
            WHERE id = %s
            """
            set_slot_unavailable = "UPDATE appointment_slots SET is_available = FALSE WHERE id = %s"
            self.db.cursor.execute(free_slot_query, (appointment_id,))
            self.db.cursor.execute(update_query, (patient_id, slot_id, appointment_id))
            self.db.cursor.execute(set_slot_unavailable, (slot_id,))
            self.db.connection.commit()
            return self.db.cursor.rowcount > 0
        except Error as e:
            print(f"Error updating appointment: {e}")
            self.db.connection.rollback()
            return False

    def delete_appointment(self, appointment_id: int) -> bool:
        check_query = "SELECT slot_id FROM appointments WHERE id = %s"
        try:
            self.db.cursor.execute(check_query, (appointment_id,))
            slot = self.db.cursor.fetchone()
            if not slot:
                print(f"Error: Appointment ID {appointment_id} does not exist")
                return False
            delete_query = "DELETE FROM appointments WHERE id = %s"
            update_slot = "UPDATE appointment_slots SET is_available = TRUE WHERE id = %s"
            self.db.cursor.execute(delete_query, (appointment_id,))
            self.db.cursor.execute(update_slot, (slot[0],))
            self.db.connection.commit()
            return self.db.cursor.rowcount > 0
        except Error as e:
            print(f"Error deleting appointment: {e}")
            self.db.connection.rollback()
            return False