from database.db_core import DatabaseManager
from utils.security import hash_password

class DoctorService:
    def __init__(self):
        self.db = DatabaseManager()

    def get_all_doctors(self, search_text=""):
        """Fetches doctors and their user details from the database."""
        base_query = """
            SELECT d.doctor_id, u.user_id, u.full_name, u.username, 
                   d.specialization, d.qualification, d.phone, 
                   d.email, d.consultation_fee, d.availability_schedule
            FROM doctors d
            JOIN users u ON d.user_id = u.user_id
        """
        
        if search_text:
            query = base_query + " WHERE u.full_name LIKE %s OR d.specialization LIKE %s ORDER BY d.doctor_id DESC"
            search_term = f"%{search_text}%"
            return self.db.execute_query(query, (search_term, search_term), fetch=True)
        
        query = base_query + " ORDER BY d.doctor_id DESC"
        return self.db.execute_query(query, fetch=True)

    def add_doctor(self, data):
        """Creates a user account first, then links it to a new doctor profile."""
        # Step 1: Create User Account for the Doctor
        hashed_pw = hash_password(data['password'])
        user_query = """INSERT INTO users (username, password_hash, role, full_name) 
                        VALUES (%s, %s, 'Doctor', %s)"""
        user_id = self.db.execute_query(user_query, (data['username'], hashed_pw, data['full_name']))
        
        if user_id:
            # Step 2: Create Doctor Profile linked to the User ID
            doc_query = """INSERT INTO doctors 
                           (user_id, specialization, qualification, phone, email, consultation_fee, availability_schedule) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            params = (user_id, data['specialization'], data['qualification'], 
                      data['phone'], data['email'], data['consultation_fee'], data['availability_schedule'])
            self.db.execute_query(doc_query, params)
            return True
        return False
        
    def delete_doctor(self, user_id):
        """Deletes the user, which automatically cascades and deletes the doctor record due to DB constraints."""
        query = "DELETE FROM users WHERE user_id = %s AND role = 'Doctor'"
        return self.db.execute_query(query, (user_id,))