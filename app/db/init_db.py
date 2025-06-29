from app.db.postgres import get_connection

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS appointments (
        id SERIAL PRIMARY KEY,
        patient_name TEXT,
        phone_number TEXT,
        appointment_date TIMESTAMP,
        profesional TEXT,
        especialidad TEXT,
        status TEXT,
        confirmation_sent BOOLEAN,
        followup_sent BOOLEAN DEFAULT FALSE,
        attended BOOLEAN DEFAULT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS pending_appointments (
        id SERIAL PRIMARY KEY,
        phone_number TEXT UNIQUE,
        appointment_date TIMESTAMP,
        profesional TEXT,
        especialidad TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        id SERIAL PRIMARY KEY,
        clinic_name TEXT,
        professional_email TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS attachments (
        id SERIAL PRIMARY KEY,
        appointment_id INTEGER REFERENCES appointments(id),
        phone_number TEXT,
        filename TEXT,
        file_path TEXT,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS feedback (
        id SERIAL PRIMARY KEY,
        patient_name TEXT,
        phone_number TEXT,
        feedback_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        feedback_text TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        role TEXT DEFAULT 'professional',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close() 