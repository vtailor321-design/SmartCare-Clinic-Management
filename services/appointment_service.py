from database.db_core import DatabaseManager

class AppointmentService:
    def __init__(self):
        self.db = DatabaseManager()

    def get_all_appointments(self, search_text=""):
        """Fetches all appointments with Patient and Doctor names."""
        query = """
            SELECT a.appointment_id, p.full_name as patient_name, u.full_name as doctor_name, 
                   a.appointment_date, a.time_slot, a.token_number, a.status 
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN doctors d ON a.doctor_id = d.doctor_id
            JOIN users u ON d.user_id = u.user_id
        """
        if search_text:
            query += " WHERE p.full_name LIKE %s OR u.full_name LIKE %s"
            search_term = f"%{search_text}%"
            query += " ORDER BY a.appointment_date DESC, a.token_number ASC"
            return self.db.execute_query(query, (search_term, search_term), fetch=True)
            
        query += " ORDER BY a.appointment_date DESC, a.token_number ASC"
        return self.db.execute_query(query, fetch=True)

    def get_dropdown_data(self):
        """Fetches lists of patients and doctors for the booking form dropdowns."""
        patients = self.db.execute_query("SELECT patient_id, full_name, phone FROM patients ORDER BY full_name", fetch=True)
        doctors = self.db.execute_query("SELECT d.doctor_id, u.full_name, d.specialization FROM doctors d JOIN users u ON d.user_id = u.user_id", fetch=True)
        return patients or [], doctors or []

    def is_slot_available(self, doctor_id, appt_date, time_slot):
        """Checks if the doctor is already booked for the exact date and time slot."""
        query = "SELECT COUNT(*) as count FROM appointments WHERE doctor_id = %s AND appointment_date = %s AND time_slot = %s AND status != 'Cancelled'"
        result = self.db.execute_query(query, (doctor_id, appt_date, time_slot), fetch_one=True)
        return result['count'] == 0 if result else False

    def generate_token(self, doctor_id, appt_date):
        """Generates the next sequential token number for a specific doctor on a specific date."""
        query = "SELECT MAX(token_number) as max_token FROM appointments WHERE doctor_id = %s AND appointment_date = %s"
        result = self.db.execute_query(query, (doctor_id, appt_date), fetch_one=True)
        return (result['max_token'] or 0) + 1

    def book_appointment(self, data):
        """Validates availability and books the appointment."""
        # 1. Check double booking
        if not self.is_slot_available(data['doctor_id'], data['appointment_date'], data['time_slot']):
            return False, "This time slot is already booked for the selected doctor."
            
        # 2. Generate Token
        token = self.generate_token(data['doctor_id'], data['appointment_date'])
        
        # 3. Save Appointment
        query = """INSERT INTO appointments (patient_id, doctor_id, appointment_date, time_slot, token_number, status)
                   VALUES (%s, %s, %s, %s, %s, 'Pending')"""
        params = (data['patient_id'], data['doctor_id'], data['appointment_date'], data['time_slot'], token)
        
        if self.db.execute_query(query, params) is not None:
            return True, f"Appointment Booked!\nToken Number: {token}"
        return False, "Database error occurred."
        
    def update_status(self, appointment_id, new_status):
        """Updates the status (Completed/Cancelled)."""
        query = "UPDATE appointments SET status = %s WHERE appointment_id = %s"
        self.db.execute_query(query, (new_status, appointment_id))