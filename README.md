# Health



A modern web application for managing healthcare operations including doctors, patients, appointment slots, appointments, and cancellations. Built with FastAPI, MySQL, SQLAlchemy, and Tailwind CSS, featuring real-time updates via WebSockets, responsive UI with modal-based interactions, and comprehensive testing.

## 🌟 Features

- **Full CRUD Operations**: Create, read, update, and delete doctors, patients, appointment slots, appointments, and cancellations
- **Real-Time Updates**: Database changes reflected instantly across all connected clients using WebSockets and MySQL triggers
- **Responsive UI**: Modern, mobile-friendly interface styled with Tailwind CSS
- **Modal-Based Interactions**: Clean, non-intrusive modals for forms and feedback messages
- **Client-Side Validation**: Real-time form validation with visual feedback
- **Search and Filter**: Advanced filtering capabilities for all entity types
- **WebSocket Communication**: Live data synchronization without page refreshes
- **Database Change Tracking**: MySQL triggers automatically log changes to a centralized `changes` table
- **Comprehensive Testing**: Unit and integration tests for all endpoints
- **Production-Ready**: MySQL database with proper connection pooling and error handling

## 📁 Project Structure

```
helth/
│
├── db/
│   ├── __init__.py
│   └── database.py           # Database models, connection, and MySQL triggers
│
├── services/
│   ├── __init__.py
│   ├── doctors.py            # Doctor CRUD operations
│   ├── patients.py           # Patient CRUD operations
│   ├── slots.py              # Appointment slot CRUD operations
│   ├── appointments.py       # Appointment CRUD operations
│   └── cancellations.py      # Cancellation CRUD operations
│
├── static/
│   ├── favicon.ico           # Application favicon
│   └── scripts.js            # JavaScript for modals, CRUD, and WebSocket updates
│
├── templates/
│   ├── navbar.html           # Reusable navigation bar component
│   ├── home.html             # Homepage with navigation cards
│   ├── doctors.html          # Doctor management interface
│   ├── patients.html         # Patient management interface
│   ├── slots.html            # Appointment slot management interface
│   ├── appointments.html     # Appointment booking interface
│   └── cancellations.html    # Cancellation tracking interface
│
├── tests/
│   ├── __init__.py
│   ├── conftests.py       # Conftests
│   ├── test_doctors.py       # Doctor endpoint tests
│   ├── test_patients.py      # Patient endpoint tests
│   ├── test_slots.py         # Slot endpoint tests
│   ├── test_appointments.py  # Appointment endpoint tests
│   └── test_cancellations.py # Cancellation endpoint tests
│
├── main.py                   # FastAPI application entry point
├── requirements.txt          # Python dependencies
├── .env.local               # Environment configuration (not in repo)
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## 🔧 Prerequisites

- **Python**: Version 3.10 or higher
- **MySQL**: Version 8.0 or higher
- **Web Browser**: Chrome, Firefox, Safari, or any modern browser
- **Git**: For cloning the repository (optional)

### For Windows Users (Chocolatey)
```bash
choco install python --version=3.10.6
choco install git
choco install mysql
```

### For macOS Users (Homebrew)
```bash
brew install python@3.10
brew install mysql
```

### For Linux Users (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
sudo apt install mysql-server
```

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd helth
```

### 2. Set Up Python Virtual Environment

```bash
# Create virtual environment
python3.10 -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies include:**
- `fastapi==0.100.0` - Modern web framework
- `uvicorn==0.23.2` - ASGI server
- `jinja2==3.1.2` - Template engine
- `python-dotenv==1.0.0` - Environment variable management
- `mysql-connector-python==8.0.33` - MySQL driver
- `websockets==12.0` - WebSocket support
- `sqlalchemy==2.0.23` - ORM for database operations
- `pytest==7.4.0` - Testing framework
- `httpx==0.24.1` - HTTP client for testing

### 4. Set Up MySQL Database

#### Start MySQL Server

**Windows:**
```bash
# Via Services or MySQL Workbench
net start MySQL80
```

**macOS:**
```bash
mysql.server start
```

**Linux:**
```bash
sudo systemctl start mysql
sudo systemctl enable mysql  # Start on boot
```

#### Create Database and User

```bash
# Login to MySQL
mysql -u root -p

# Execute the following SQL commands:
```

```sql
CREATE DATABASE helth CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER 'healthcare_user'@'localhost' IDENTIFIED BY 'your_secure_password';

GRANT ALL PRIVILEGES ON helth.* TO 'healthcare_user'@'localhost';

FLUSH PRIVILEGES;

EXIT;
```

### 5. Configure Environment Variables

Create a `.env.local` file in the project root:

```bash
# Linux/macOS
touch .env.local

# Windows
type nul > .env.local
```

Add the following configuration (replace values as needed):

```env
DATABASE_URL=mysql+mysqlconnector://healthcare_user:your_secure_password@localhost:3306/helth
```

**Configuration options:**
- `healthcare_user` - Your MySQL username
- `your_secure_password` - Your MySQL password
- `localhost` - Database host (use IP if remote)
- `3306` - MySQL port (default)
- `helth` - Database name

### 6. Initialize Database Schema

The application automatically creates all necessary tables and triggers on first run:
- `doctors` - Doctor information
- `patients` - Patient records
- `appointment_slots` - Available time slots
- `appointments` - Booked appointments
- `cancellations` - Cancellation records
- `changes` - Change tracking for real-time updates

## 🎯 Running the Application

### Easy Mode

Just run normally, it's a standalone front+back end app

```bash
python main.py
```

### Development Mode

```bash
uvicorn main:app --reload --host localhost --port 8080
```

**Options:**
- `--reload` - Auto-restart on code changes
- `--host localhost` - Bind to localhost
- `--port 8080` - Use port 8080

### Production Mode

```bash
uvicorn main:app --host localhost --port 8080 --workers 4
```

**Options:**
- `--host 0.0.0.0` - Accept connections from any IP
- `--workers 4` - Run 4 worker processes

### Access the Application

Open your browser and navigate to:
```
http://localhost:8080
```

**Available endpoints:**
- `/` - Homepage
- `/doctors` - Manage doctors
- `/patients` - Manage patients
- `/slots` - Manage appointment slots
- `/appointments` - Manage appointments
- `/cancellations` - Track cancellations
- `/docs` - Interactive API documentation (Swagger UI)
- `/redoc` - Alternative API documentation

## 🧪 Running Tests

The application includes a comprehensive test suite using `pytest` and `pytest-asyncio` to verify CRUD operations and WebSocket functionality. Tests are located in the `tests/` directory and use an in-memory SQLite database for isolation.

### Setup
   ```bash
   pip install pytest==7.4.0 pytest-asyncio==0.21.0 httpx==0.23.0
```

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_doctors.py
```

### Run with Coverage Report

```bash
pytest --cov=services --cov-report=html
```

### Run with Verbose Output

```bash
pytest -v
```

### Test Structure

Each test file covers:
- ✅ Creating entities
- ✅ Reading/listing entities
- ✅ Updating entities
- ✅ Deleting entities
- ✅ Error handling (404, validation errors)
- ✅ Edge cases

## 📖 Usage Guide

### Managing Doctors

1. **Add a Doctor:**
   - Click "Add Doctor" button
   - Fill in name and specialty
   - Submit form
   - Doctor appears in the list immediately

2. **Edit a Doctor:**
   - Click the edit icon (pencil) next to a doctor
   - Modify name or specialty
   - Save changes

3. **Delete a Doctor:**
   - Click the delete icon (trash) next to a doctor
   - Confirm deletion
   - Doctor is removed from the list

4. **Search and Filter:**
   - Use search box to find doctors by name
   - Use specialty dropdown to filter by specialty

### Managing Patients

Similar workflow to doctors:
- Add patient name and email
- Edit patient information
- Delete patients
- Search by name, filter by email domain

### Managing Appointment Slots

1. **Create a Slot:**
   - Select doctor from dropdown
   - Choose date
   - Set start and end time
   - Set availability (true/false)

2. **Update Availability:**
   - Edit slot
   - Toggle availability
   - Save changes

### Booking Appointments

1. **Book an Appointment:**
   - Select patient from dropdown
   - Select available slot
   - Submit booking
   - Appointment is created and slot becomes unavailable

### Recording Cancellations

1. **Cancel an Appointment:**
   - Select appointment to cancel
   - Enter cancellation reason
   - Submit cancellation
   - Appointment slot becomes available again

## 🔄 Real-Time Updates

The application uses WebSockets to provide real-time updates:

1. **Database Triggers**: MySQL triggers automatically log changes to the `changes` table
2. **WebSocket Polling**: Server polls the changes table every second
3. **Client Updates**: Connected clients receive update notifications
4. **Automatic Refresh**: UI refreshes automatically without page reload

**Supported operations:**
- Adding new records
- Updating existing records
- Deleting records

All connected users see changes instantly!

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port number
uvicorn main:app --reload --host localhost --port 8000
```

### MySQL Connection Errors
```bash
# Check if MySQL is running
# Windows:
net start | findstr MySQL

# Linux/macOS:
ps aux | grep mysql

# Verify credentials in .env.local
# Test connection:
mysql -u healthcare_user -p helth
```

### Module Not Found Errors
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Static Files Not Loading
```bash
# Verify files exist
ls static/favicon.ico
ls static/scripts.js

# Check file permissions (Linux/macOS)
chmod 644 static/*
```

### WebSocket Connection Failed
- Check browser console for errors
- Verify WebSocket URL matches server host/port
- Ensure firewall allows WebSocket connections

### Database Schema Issues
```sql
-- Drop and recreate database (WARNING: deletes all data)
DROP DATABASE helth;
CREATE DATABASE helth CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Then restart the application to recreate tables
```

### Form Submission Returns 405 Error
- Ensure endpoints have trailing slashes where required
- Check `main.py` router prefixes match form endpoints
- Verify form `action` attributes in HTML templates

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the Repository**
   ```bash
   git fork <repository-url>
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make Your Changes**
   - Write clean, documented code
   - Add tests for new features
   - Follow existing code style

4. **Run Tests**
   ```bash
   pytest
   ```

5. **Commit Your Changes**
   ```bash
   git commit -m "Add amazing feature"
   ```

6. **Push to Branch**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Open a Pull Request**
   - Describe your changes
   - Reference any related issues
   - Wait for review

## 📝 Future Enhancements

- [ ] User authentication and role-based access control
- [ ] Patient history and medical records
- [ ] Prescription management
- [ ] Billing and invoicing
- [ ] Analytics dashboard with charts

## 📄 License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2025 Helth

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 Acknowledgments

- **FastAPI** - Modern, fast web framework for Python
- **Tailwind CSS** - Utility-first CSS framework
- **Font Awesome** - Icon library
- **MySQL** - Reliable relational database
- **SQLAlchemy** - Python SQL toolkit and ORM

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review closed issues for solutions

---
