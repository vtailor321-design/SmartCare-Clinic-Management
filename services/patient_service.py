from database.db_core import DatabaseManager

class PatientService:
    def __init__(self):
        self.db = DatabaseManager()

    def get_all_patients(self, search_text=""):
        """Fetches patients from the database. Supports search by Name, Phone, or ID."""
        if search_text:
            query = "SELECT * FROM patients WHERE full_name LIKE %s OR phone LIKE %s OR patient_id = %s ORDER BY patient_id DESC"
            search_term = f"%{search_text}%"
            # If search is a number, use it for ID search, otherwise 0
            pid = search_text if search_text.isdigit() else 0
            return self.db.execute_query(query, (search_term, search_term, pid), fetch=True)
        
        query = "SELECT * FROM patients ORDER BY patient_id DESC"
        return self.db.execute_query(query, fetch=True)

    def add_patient(self, data):
        """Inserts a new patient into the database."""
        query = """INSERT INTO patients (full_name, dob, gender, phone, address, blood_group, emergency_contact) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        params = (data['full_name'], data['dob'], data['gender'], data['phone'], 
                  data['address'], data['blood_group'], data['emergency_contact'])
        return self.db.execute_query(query, params)
        
    def delete_patient(self, patient_id):
        """Deletes a patient from the database."""
        query = "DELETE FROM patients WHERE patient_id = %s"
        return self.db.execute_query(query, (patient_id,))