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

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column('hashed_password', String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(String(20), default='user')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime, nullable=True)

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