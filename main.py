from fastapi import FastAPI, Request, WebSocket
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from db.database import SessionLocal
from services import doctors, patients, slots, appointments, cancellations, booking, auth
import asyncio
import uvicorn

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class WebSocketManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = WebSocketManager()

async def websocket_endpoint(websocket: WebSocket, table_name: str):
    await manager.connect(websocket)
    try:
        db = SessionLocal()
        last_change_id = 0
        while True:
            changes = db.query(db.database.Change).filter(
                db.database.Change.id > last_change_id,
                db.database.Change.table_name == table_name
            ).all()
            if changes:
                last_change_id = max(change.id for change in changes)
                await manager.broadcast(f"update_{table_name}")
            await asyncio.sleep(1)
    except Exception:
        await manager.disconnect(websocket)
    finally:
        db.close()

@app.websocket("/ws/doctors")
async def websocket_doctors(websocket: WebSocket):
    await websocket_endpoint(websocket, "doctors")

@app.websocket("/ws/patients")
async def websocket_patients(websocket: WebSocket):
    await websocket_endpoint(websocket, "patients")

@app.websocket("/ws/appointment_slots")
async def websocket_slots(websocket: WebSocket):
    await websocket_endpoint(websocket, "appointment_slots")

@app.websocket("/ws/appointments")
async def websocket_appointments(websocket: WebSocket):
    await websocket_endpoint(websocket, "appointments")

@app.websocket("/ws/cancellations")
async def websocket_cancellations(websocket: WebSocket):
    await websocket_endpoint(websocket, "cancellations")

# Helper function to check authentication
def is_authenticated(request: Request) -> bool:
    """Check if user is authenticated"""
    token = request.cookies.get("session_token")
    if not token:
        return False
    
    user = auth.get_user_from_session(token)
    return user is not None

# Login page (no authentication required)
@app.get("/login")
async def login_page(request: Request):
    """Display login page"""
    # If already logged in, redirect to home
    if is_authenticated(request):
        return RedirectResponse(url="/", status_code=302)
    
    return templates.TemplateResponse("login.html", {"request": request})

# Protected routes - require authentication
@app.get("/")
async def home(request: Request):
    """Homepage - requires authentication"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/booking")
async def booking_page(request: Request):
    """Advanced booking interface - requires authentication"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("booking.html", {"request": request})

@app.get("/doctors")
async def doctors_page(request: Request):
    """Doctors page - requires authentication"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=302)
    
    db = SessionLocal()
    doctor_list = doctors.get_doctors(db)
    db.close()
    return templates.TemplateResponse("doctors.html", {"request": request, "doctors": doctor_list})

@app.get("/patients")
async def patients_page(request: Request):
    """Patients page - requires authentication"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=302)
    
    db = SessionLocal()
    patient_list = patients.get_patients(db)
    db.close()
    return templates.TemplateResponse("patients.html", {"request": request, "patients": patient_list})

@app.get("/slots")
async def slots_page(request: Request):
    """Slots page - requires authentication"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=302)
    
    db = SessionLocal()
    slot_list = slots.get_slots(db)
    db.close()
    return templates.TemplateResponse("slots.html", {"request": request, "slots": slot_list})

@app.get("/appointments")
async def appointments_page(request: Request):
    """Appointments page - requires authentication"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=302)
    
    db = SessionLocal()
    appointment_list = appointments.get_appointments(db)
    db.close()
    return templates.TemplateResponse("appointments.html", {"request": request, "appointments": appointment_list})

@app.get("/cancellations")
async def cancellations_page(request: Request):
    """Cancellations page - requires authentication"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=302)
    
    db = SessionLocal()
    cancellation_list = cancellations.get_cancellations(db)
    db.close()
    return templates.TemplateResponse("cancellations.html", {"request": request, "cancellations": cancellation_list})

# Include all routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(doctors.router, prefix="/doctors", tags=["doctors"])
app.include_router(patients.router, prefix="/patients", tags=["patients"])
app.include_router(slots.router, prefix="/appointment_slots", tags=["slots"])
app.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
app.include_router(cancellations.router, prefix="/cancellations", tags=["cancellations"])
app.include_router(booking.router, prefix="/booking", tags=["booking"])

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)