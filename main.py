from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from db.database import Database
from services.doctors import DoctorService
from services.patients import PatientService
from services.slots import SlotService
from services.appointments import AppointmentService
from services.cancellations import CancellationService
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db, doctor_service, patient_service, slot_service, appointment_service, cancellation_service
    db = Database(env_file=".env.local")
    db.create_schema()
    doctor_service = DoctorService(db)
    patient_service = PatientService(db)
    slot_service = SlotService(db)
    appointment_service = AppointmentService(db)
    cancellation_service = CancellationService(db)
    yield
    db.close()

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/doctors")
async def doctors(request: Request):
    doctors = doctor_service.get_all_doctors()
    return templates.TemplateResponse("doctors.html", {"request": request, "doctors": doctors})

@app.post("/doctors")
async def add_doctor(name: str = Form(...), specialty: str = Form(...)):
    doctor_id = doctor_service.add_doctor(name, specialty)
    return JSONResponse({"status": "success", "doctor_id": doctor_id}) if doctor_id else JSONResponse({"status": "error"})

@app.post("/doctors/update")
async def update_doctor(doctor_id: int = Form(...), name: str = Form(...), specialty: str = Form(...)):
    success = doctor_service.update_doctor(doctor_id, name, specialty)
    return JSONResponse({"status": "success"}) if success else JSONResponse({"status": "error", "message": f"Cannot update Doctor ID {doctor_id}."})

@app.post("/doctors/delete")
async def delete_doctor(doctor_id: int = Form(...)):
    success = doctor_service.delete_doctor(doctor_id)
    return JSONResponse({"status": "success"}) if success else JSONResponse({"status": "error", "message": f"Cannot delete Doctor ID {doctor_id}. It may have associated appointment slots."})

@app.get("/patients")
async def patients(request: Request):
    patients = patient_service.get_all_patients()
    return templates.TemplateResponse("patients.html", {"request": request, "patients": patients})

@app.post("/patients")
async def add_patient(name: str = Form(...), email: str = Form(...)):
    patient_id = patient_service.add_patient(name, email)
    return JSONResponse({"status": "success", "patient_id": patient_id}) if patient_id else JSONResponse({"status": "error"})

@app.post("/patients/update")
async def update_patient(patient_id: int = Form(...), name: str = Form(...), email: str = Form(...)):
    success = patient_service.update_patient(patient_id, name, email)
    return JSONResponse({"status": "success"}) if success else JSONResponse({"status": "error", "message": f"Cannot update Patient ID {patient_id}."})

@app.post("/patients/delete")
async def delete_patient(patient_id: int = Form(...)):
    success = patient_service.delete_patient(patient_id)
    return JSONResponse({"status": "success"}) if success else JSONResponse({"status": "error", "message": f"Cannot delete Patient ID {patient_id}. It may have associated appointments."})

@app.get("/slots")
async def slots(request: Request):
    slots = slot_service.get_all_slots()
    doctors = doctor_service.get_all_doctors()
    return templates.TemplateResponse("slots.html", {"request": request, "slots": slots, "doctors": doctors})

@app.post("/slots")
async def add_slot(doctor_id: int = Form(...), date: str = Form(...), start_time: str = Form(...), end_time: str = Form(...)):
    slot_id = slot_service.add_slot(doctor_id, date, start_time, end_time)
    return JSONResponse({"status": "success", "slot_id": slot_id}) if slot_id else JSONResponse({"status": "error"})

@app.post("/slots/update")
async def update_slot(slot_id: int = Form(...), date: str = Form(...), start_time: str = Form(...), end_time: str = Form(...)):
    success = slot_service.update_slot(slot_id, date, start_time, end_time)
    return JSONResponse({"status": "success"}) if success else JSONResponse({"status": "error", "message": f"Cannot update Slot ID {slot_id}. It may be booked or invalid."})

@app.post("/slots/delete")
async def delete_slot(slot_id: int = Form(...)):
    success = slot_service.delete_slot(slot_id)
    return JSONResponse({"status": "success"}) if success else JSONResponse({"status": "error", "message": f"Cannot delete Slot ID {slot_id}. It may have associated appointments."})

@app.get("/appointments")
async def appointments(request: Request):
    appointments = appointment_service.get_all_appointments()
    patients = patient_service.get_all_patients()
    return templates.TemplateResponse("appointments.html", {"request": request, "appointments": appointments, "patients": patients})

@app.post("/appointments")
async def book_appointment(patient_id: int = Form(...), slot_id: int = Form(...)):
    appointment_id = appointment_service.book_appointment(patient_id, slot_id)
    return JSONResponse({"status": "success", "appointment_id": appointment_id}) if appointment_id else JSONResponse({"status": "error"})

@app.post("/appointments/update")
async def update_appointment(appointment_id: int = Form(...), patient_id: int = Form(...), slot_id: int = Form(...)):
    success = appointment_service.update_appointment(appointment_id, patient_id, slot_id)
    return JSONResponse({"status": "success"}) if success else JSONResponse({"status": "error", "message": f"Cannot update Appointment ID {appointment_id}. Check patient or slot ID."})

@app.post("/appointments/delete")
async def delete_appointment(appointment_id: int = Form(...)):
    success = appointment_service.delete_appointment(appointment_id)
    return JSONResponse({"status": "success"}) if success else JSONResponse({"status": "error", "message": f"Cannot delete Appointment ID {appointment_id}."})

@app.get("/cancellations")
async def cancellations(request: Request):
    cancellations = cancellation_service.get_all_cancellations()
    return templates.TemplateResponse("cancellations.html", {"request": request, "cancellations": cancellations})

@app.post("/cancellations")
async def cancel_appointment(appointment_id: int = Form(...), reason: str = Form(...)):
    cancellation_id = cancellation_service.cancel_appointment(appointment_id, reason)
    return JSONResponse({"status": "success", "cancellation_id": cancellation_id}) if cancellation_id else JSONResponse({"status": "error"})

@app.post("/cancellations/update")
async def update_cancellation(cancellation_id: int = Form(...), reason: str = Form(...)):
    success = cancellation_service.update_cancellation(cancellation_id, reason)
    return JSONResponse({"status": "success"}) if success else JSONResponse({"status": "error", "message": f"Cannot update Cancellation ID {cancellation_id}."})

@app.post("/cancellations/delete")
async def delete_cancellation(cancellation_id: int = Form(...)):
    success = cancellation_service.delete_cancellation(cancellation_id)
    return JSONResponse({"status": "success"}) if success else JSONResponse({"status": "error", "message": f"Cannot delete Cancellation ID {cancellation_id}."})

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)