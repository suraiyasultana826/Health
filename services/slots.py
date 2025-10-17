class SlotService:
    def __init__(self, db):
        self.db = db

    def add_slot(self, doctor_id, date, start_time, end_time):
        query = """
        INSERT INTO appointment_slots (doctor_id, date, start_time, end_time)
        VALUES (%s, %s, %s, %s)
        """
        try:
            self.db.cursor.execute(query, (doctor_id, date, start_time, end_time))
            self.db.connection.commit()
            return self.db.cursor.lastrowid
        except Error as e:
            print(f"Error adding slot: {e}")
            return None