from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Date, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from dotenv import load_dotenv
import os

load_dotenv('.env.local')
DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Doctor(Base):
    __tablename__ = 'doctors'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    specialty = Column(String(100), nullable=False)

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)

class AppointmentSlot(Base):
    __tablename__ = 'appointment_slots'
    id = Column(Integer, primary_key=True)
    doctor_id = Column(Integer, ForeignKey('doctors.id'))
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_available = Column(Boolean, default=True)

class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    slot_id = Column(Integer, ForeignKey('appointment_slots.id'))
    booked_at = Column(DateTime, nullable=False)

class Cancellation(Base):
    __tablename__ = 'cancellations'
    id = Column(Integer, primary_key=True)
    appointment_id = Column(Integer, ForeignKey('appointments.id'))
    reason = Column(String(255))
    cancelled_at = Column(DateTime, nullable=False)

class Change(Base):
    __tablename__ = 'changes'
    id = Column(Integer, primary_key=True)
    table_name = Column(String(50), nullable=False)
    action = Column(String(20), nullable=False)
    record_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)

# def init_triggers():
#     with engine.connect() as conn:
#         for table in ['doctors', 'patients', 'appointment_slots', 'appointments', 'cancellations']:
#             conn.execute(f"DROP TRIGGER IF EXISTS {table}_insert_trigger")
#             conn.execute(f"DROP TRIGGER IF EXISTS {table}_update_trigger")
#             conn.execute(f"DROP TRIGGER IF EXISTS {table}_delete_trigger")
            
#             conn.execute(f"""
#                 CREATE TRIGGER {table}_insert_trigger
#                 AFTER INSERT ON {table}
#                 FOR EACH ROW
#                 BEGIN
#                     INSERT INTO changes (table_name, action, record_id)
#                     VALUES ('{table}', 'INSERT', NEW.id);
#                 END;
#             """)
#             conn.execute(f"""
#                 CREATE TRIGGER {table}_update_trigger
#                 AFTER UPDATE ON {table}
#                 FOR EACH ROW
#                 BEGIN
#                     INSERT INTO changes (table_name, action, record_id)
#                     VALUES ('{table}', 'UPDATE', NEW.id);
#                 END;
#             """)
#             conn.execute(f"""
#                 CREATE TRIGGER {table}_delete_trigger
#                 AFTER DELETE ON {table}
#                 FOR EACH ROW
#                 BEGIN
#                     INSERT INTO changes (table_name, action, record_id)
#                     VALUES ('{table}', 'DELETE', OLD.id);
#                 END;
#             """)
#         conn.commit()

# def seed_data():
#     db = SessionLocal()
#     try:
#         # Check if doctors table is empty
#         if db.query(Doctor).count() == 0:
#             doctors = [
#                 Doctor(name="Dr. John Smith", specialty="Cardiology"),
#                 Doctor(name="Dr. Jane Doe", specialty="Pediatrics"),
#             ]
#             db.add_all(doctors)
#         # Check if patients table is empty
#         if db.query(Patient).count() == 0:
#             patients = [
#                 Patient(name="Alice Brown", email="alice@example.com"),
#                 Patient(name="Bob White", email="bob@example.com"),
#             ]
#             db.add_all(patients)
#         db.commit()
#     except Exception as e:
#         db.rollback()
#         print(f"Error seeding data: {e}")
#     finally:
#         db.close()

# init_triggers()
# seed_data()