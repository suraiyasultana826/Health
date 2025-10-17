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
async def index(request: Request):
    doctors = doctor_service.get_all_doctors()
    return templates.TemplateResponse("index.html", {"request": request, "doctors": doctors})

@app.post("/doctors")
async def add_doctor(name: str = Form(...), specialty: str = Form(...)):
    doctor_id = doctor_service.add_doctor(name, specialty)
    return JSONResponse({"status": "success", "doctor_id": doctor_id}) if doctor_id else JSONResponse({"status": "error"})

@app.post("/patients")
async def add_patient(name: str = Form(...), email: str = Form(...)):
    patient_id = patient_service.add_patient(name, email)
    return JSONResponse({"status": "success", "patient_id": patient_id}) if patient_id else JSONResponse({"status": "error"})

@app.post("/slots")
async def add_slot(doctor_id: int = Form(...), date: str = Form(...), start_time: str = Form(...), end_time: str = Form(...)):
    slot_id = slot_service.add_slot(doctor_id, date, start_time, end_time)
    return JSONResponse({"status": "success", "slot_id": slot_id}) if slot_id else JSONResponse({"status": "error"})

@app.post("/appointments")
async def book_appointment(patient_id: int = Form(...), slot_id: int = Form(...)):
    appointment_id = appointment_service.book_appointment(patient_id, slot_id)
    return JSONResponse({"status": "success", "appointment_id": appointment_id}) if appointment_id else JSONResponse({"status": "error"})

@app.post("/cancellations")
async def cancel_appointment(appointment_id: int = Form(...), reason: str = Form(...)):
    cancellation_id = cancellation_service.cancel_appointment(appointment_id, reason)
    return JSONResponse({"status": "success", "cancellation_id": cancellation_id}) if cancellation_id else JSONResponse({"status": "error"})

@app.post("/doctors/delete")
async def delete_doctor(doctor_id: int = Form(...)):
    success = doctor_service.delete_doctor(doctor_id)
    if success:
        return JSONResponse({"status": "success"})
    return JSONResponse({"status": "error", "message": f"Cannot delete Doctor ID {doctor_id}. It may have associated appointment slots."})

@app.get("/doctors/availability")
async def get_doctor_availability(request: Request, doctor_id: int = None, date: str = None):
    availability = doctor_service.get_doctor_availability(doctor_id, date) if doctor_id and date else []
    doctors = doctor_service.get_all_doctors()
    return templates.TemplateResponse("availability.html", {"request": request, "availability": availability, "doctors": doctors})

@app.get("/patients/appointments")
async def get_patient_appointments(request: Request, patient_id: int = None):
    appointments = patient_service.get_patient_appointments(patient_id) if patient_id else []
    return templates.TemplateResponse("appointments.html", {"request": request, "appointments": appointments})

@app.get("/cancellations/stats")
async def get_cancellation_stats(request: Request, doctor_id: int = None):
    stats = cancellation_service.get_cancellation_stats(doctor_id) if doctor_id else None
    doctors = doctor_service.get_all_doctors()
    return templates.TemplateResponse("stats.html", {"request": request, "stats": stats, "doctors": doctors})

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)