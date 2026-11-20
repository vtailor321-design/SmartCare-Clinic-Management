from database.db_core import DatabaseManager

class PrescriptionService:
    def __init__(self):
        self.db = DatabaseManager()

    def get_doctor_id(self, user_id):
        result = self.db.execute_query("SELECT doctor_id FROM doctors WHERE user_id = %s", (user_id,), fetch_one=True)
        return result['doctor_id'] if result else None

    def get_appointments_for_prescription(self, doctor_user_id):
        """Fetches appointments specifically for the logged-in doctor."""
        doc_id = self.get_doctor_id(doctor_user_id)
        if not doc_id: return []
        
        query = """
            SELECT a.appointment_id, p.full_name as patient_name, a.appointment_date, a.token_number, p.patient_id
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            WHERE a.doctor_id = %s AND a.status = 'Pending'
            ORDER BY a.appointment_date DESC, a.token_number ASC
        """
        return self.db.execute_query(query, (doc_id,), fetch=True)

    def get_or_create_medicine(self, name):
        """Finds a medicine ID by name, creates it if it doesn't exist."""
        result = self.db.execute_query("SELECT medicine_id FROM medicines WHERE name = %s", (name,), fetch_one=True)
        if result:
            return result['medicine_id']
        else:
            return self.db.execute_query("INSERT INTO medicines (name, unit_price) VALUES (%s, 0)", (name,))

    def save_prescription(self, data):
        """Saves prescription and medicines using a database transaction."""
        conn = self.db.get_connection()
        if not conn: return False
        
        try:
            cursor = conn.cursor()
            # 1. Insert Prescription
            q_presc = """INSERT INTO prescriptions (appointment_id, patient_id, doctor_id, diagnosis, instructions, follow_up_date) 
                         VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(q_presc, (data['appointment_id'], data['patient_id'], data['doctor_id'], 
                                     data['diagnosis'], data['instructions'], data['follow_up']))
            prescription_id = cursor.lastrowid
            
            # 2. Insert Medicines
            q_med = """INSERT INTO prescription_medicines (prescription_id, medicine_id, dosage, duration) 
                       VALUES (%s, %s, %s, %s)"""
            
            for med in data['medicines']:
                med_id = self.get_or_create_medicine(med['name'])
                cursor.execute(q_med, (prescription_id, med_id, med['dosage'], med['duration']))
                
            # 3. Mark appointment as completed automatically
            cursor.execute("UPDATE appointments SET status = 'Completed' WHERE appointment_id = %s", (data['appointment_id'],))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error saving prescription: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def get_full_prescription_data_for_pdf(self, appointment_id):
        """Gathers all nested data required for the PDF report."""
        query_info = """
            SELECT p.full_name as patient_name, p.dob, p.gender, 
                   u.full_name as doctor_name, d.specialization, d.qualification,
                   a.token_number, pr.diagnosis, pr.instructions, pr.follow_up_date as follow_up
            FROM prescriptions pr
            JOIN appointments a ON pr.appointment_id = a.appointment_id
            JOIN patients p ON pr.patient_id = p.patient_id
            JOIN doctors d ON pr.doctor_id = d.doctor_id
            JOIN users u ON d.user_id = u.user_id
            WHERE pr.appointment_id = %s
        """
        info = self.db.execute_query(query_info, (appointment_id,), fetch_one=True)
        if not info: return None
        
        query_meds = """
            SELECT m.name, pm.dosage, pm.duration 
            FROM prescription_medicines pm
            JOIN medicines m ON pm.medicine_id = m.medicine_id
            WHERE pm.prescription_id = (SELECT prescription_id FROM prescriptions WHERE appointment_id = %s)
        """
        meds = self.db.execute_query(query_meds, (appointment_id,), fetch=True)
        info['medicines'] = meds or []
        return info