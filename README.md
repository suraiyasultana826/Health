# Helth

![BOOK, TRACK and MANAGE](https://i.kym-cdn.com/entries/icons/original/000/032/279/Screen_Shot_2019-12-30_at_11.26.24_AM.png)

A web-based application for managing doctors, patients, appointment slots, appointments, and cancellations in a healthcare setting. Built with FastAPI, MySQL, and Tailwind CSS, it features a responsive UI with a common navbar, modal-based feedback, and centralized JavaScript for CRUD operations.

## Features
- **CRUD Operations**: Create, read, update, and delete doctors, patients, appointment slots, appointments, and cancellations.
- **Responsive UI**: Styled with Tailwind CSS, including a consistent navbar across all pages.
- **Modal Feedback**: Success and error messages displayed in modals.
- **Client-Side Validation**: Ensures required fields are filled before form submission.
- **MySQL Database**: Production grade database

## File Structure
```
helth/
│
├── db/
│   ├── __init__.py
│   └── database.py        # Database connection and schema
│
├── services/
│   ├── __init__.py
│   ├── doctors.py        # Doctor CRUD operations
│   ├── patients.py       # Patient CRUD operations
│   ├── slots.py          # Appointment slot CRUD operations
│   ├── appointments.py   # Appointment CRUD operations
│   └── cancellations.py   # Cancellation CRUD operations
│
├── static/
│   ├── favicon.ico       # Favicon for the app
│   └── scripts.js        # Common JavaScript for modals and CRUD
│
├── templates/
│   ├── navbar.html       # Reusable navbar template
│   ├── home.html         # Homepage with navigation
│   ├── doctors.html      # CRUD for doctors with modal feedback
│   ├── patients.html     # CRUD for patients with modal feedback
│   ├── slots.html        # CRUD for appointment slots with modal feedback
│   ├── appointments.html # CRUD for appointments with modal feedback
│   └── cancellations.html # CRUD for cancellations with modal feedback
│
├── main.py               # FastAPI app entry point
├── requirements.txt      # Project dependencies
└── README.md             # This file
```

## Prerequisites
- **Operating System**: Windows, macOS, or Linux
- **Python**: Version 3.10
- **Web Browser**: Chrome, Firefox, or any modern browser
- **Git**: For cloning the repository (optional)

## For Chocolatey users (Windows Only)

If you are cultured enough to use Chocolatey (or have it installed), then please install git, python and other pre requisits via `choco install <package name>`

```
choco install python --version=3.10.6
choco install git
```

However, highly recommend installing MySQL via the official download from the official link [here](https://dev.mysql.com/downloads/installer/)

## Installation

### 1. Install Python 3.10
1. **Download Python 3.10**:
   - Visit the [official Python website](https://www.python.org/downloads/release/python-3100/).
   - Download the installer for Python 3.10 for your operating system (Windows, macOS, or Linux).
2. **Install Python**:
   - **Windows**: Run the installer, check "Add Python 3.10 to PATH," and select "Install Now." If you forgot to check that option, reinstall correctly.
   - **macOS**: Run the installer and follow the prompts.
   - **Linux**: Use your package manager (e.g., `sudo apt install python3.10` on Ubuntu) or build from source.
3. **Verify Installation**:
   ```bash
   python3.10 --version
   ```
   Ensure the output shows `Python 3.10.x`.

### 2. Clone the Repository
1. Clone the project (or download and extract the ZIP):
   ```bash
   git clone <repository-url>
   cd healthcare_ticketing
   ```
   Replace `<repository-url>` with the actual repository URL if hosted on GitHub or similar.

### 3. Set Up a Virtual Environment
1. Create a virtual environment:
   ```bash
   python3.10 -m venv venv
   ```
2. Activate the virtual environment:
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

### 4. Install Dependencies
1. Install required packages from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
   The `requirements.txt` includes:
   ```
   fastapi
   uvicorn
   jinja2
   python-dotenv
   mysql-connector-python
   ```

### 5. Set Up the Database
1. **Install MySQL**:
   - Download and install MySQL 8.0 or higher from the [official MySQL website](https://dev.mysql.com/downloads/installer/).
   - **Windows/macOS**: Use the MySQL Installer or Community Server package.
   - **Linux**: Install via package manager (e.g., `sudo apt install mysql-server` on Ubuntu).
2. **Start MySQL Server**:
   - Ensure the MySQL server is running:
     - **Windows**: Start via Services or MySQL Workbench.
     - **macOS**: Run `mysql.server start`.
     - **Linux**: Run `sudo systemctl start mysql`.
3. **Create the Database**:
   - Log in to MySQL:
     ```bash
     mysql -u root -p
     ```
     Enter your root password when prompted.
   - Create a database (e.g., `helth`):
     ```sql
     CREATE DATABASE helth;
     ```
   - (OPTIONAL) Create a user and grant privileges:
     ```sql
     CREATE USER 'healthcare_user'@'localhost' IDENTIFIED BY 'your_secure_password';
     GRANT ALL PRIVILEGES ON healthcare_db.* TO 'healthcare_user'@'localhost';
     FLUSH PRIVILEGES;
     EXIT;
     ```
     Replace `your_secure_password` with a strong password.
4. **Configure Environment Variables**:
   - (IMPORTANT!) Create a `.env.local` file in the project root:
     ```bash
     #linux/Mac
     touch .env.local
     ```
   - Add the MySQL configuration:
     ```
        HOST=localhost
        USER=root
        PORT=3306
        PASSWORD=root
        DATABASE=helth
     ```
5. **Initialize the Database**:
   - The application will automatically create the required tables (`doctors`, `patients`, `slots`, `appointments`, `cancellations`) when first run, assuming `db/database.py` is configured to use Python MySQL Connector with a running MySQL server.

### 6. Add Static Files
1. Ensure the `static/` folder contains:
   - `favicon.ico`: A favicon image for the app.
   - `scripts.js`: The common JavaScript file for modals and CRUD operations (already provided in the project).
2. If missing, create an empty `favicon.ico` or download one and place it in `static/`.

## Running the Application
1. Start the FastAPI server, the app is standalone API/Backend/Frontend:
   ```bash
   python main.py
   ```
2. Open a web browser and navigate to:
   ```
   http://localhost:8080
   ```
3. The homepage displays navigation links to manage doctors, patients, slots, appointments, and cancellations.

## Usage
- **Home Page**: Access all sections via the navbar or cards.
- **Doctors**: Add, update, or delete doctors (name, specialty).
- **Patients**: Manage patient details (name, email).
- **Slots**: Create or update doctor availability slots (doctor, date, time).
- **Appointments**: Book or update appointments (patient, slot).
- **Cancellations**: Record or update cancellations (appointment, reason).
- **Feedback**: Success/error messages appear in modals.
- **Validation**: Required fields are checked client-side; invalid inputs are highlighted.

## Notes
- **Database**: MySQL was used, one can also use their preferred database, by changing the file `database.py`
- **Static Files**: Ensure `static/favicon.ico` and `static/scripts.js` are accessible. FastAPI serves static files automatically.
- **Responsive Design**: The UI is responsive, but you can enhance the navbar with a hamburger menu for mobile devices.
- **Security**: Add authentication and input sanitization for production use.
- **Further Improvements**:
  - Add client-side validation for specific fields (e.g., email format, time constraints).
  - Implement a loading state for form submissions in modals.
  - Cache static files for better performance.

## Troubleshooting
- **Port Conflict**: If port 8080 is in use, change the port in the `uvicorn` command (e.g., `--port 8000`).
- **Dependencies**: If `pip install` fails, ensure `pip` is for Python 3.10 (`pip3.10 install -r requirements.txt`).
- **Database Issues**: Verify `.env.local` exists and `DATABASE_URL` is correct.
- **Static Files Not Loading**: Check that `static/` contains `favicon.ico` and `scripts.js`.

## Contributing
Contributions are welcome! Please:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit changes (`git commit -m "Add feature"`).
4. Push to the branch (`git push origin feature-name`).
5. Open a pull request.

## License
This project is licensed under the MIT License.