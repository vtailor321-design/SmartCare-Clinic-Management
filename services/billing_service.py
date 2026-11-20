from database.db_core import DatabaseManager

class BillingService:
    def __init__(self):
        self.db = DatabaseManager()

    def get_all_bills(self, search_text=""):
        query = """
            SELECT b.bill_id, p.full_name as patient_name, a.appointment_date, 
                   b.net_amount, b.status 
            FROM bills b
            JOIN patients p ON b.patient_id = p.patient_id
            LEFT JOIN appointments a ON b.appointment_id = a.appointment_id
        """
        if search_text:
            query += " WHERE p.full_name LIKE %s OR b.bill_id = %s ORDER BY b.bill_id DESC"
            bid = search_text if search_text.isdigit() else 0
            return self.db.execute_query(query, (f"%{search_text}%", bid), fetch=True)
            
        query += " ORDER BY b.bill_id DESC"
        return self.db.execute_query(query, fetch=True)

    def get_unbilled_appointments(self):
        """Fetches completed appointments that do not have a bill generated yet."""
        query = """
            SELECT a.appointment_id, p.patient_id, p.full_name, a.appointment_date, d.consultation_fee
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.status = 'Completed' 
              AND a.appointment_id NOT IN (SELECT appointment_id FROM bills WHERE appointment_id IS NOT NULL)
        """
        return self.db.execute_query(query, fetch=True)

    def create_bill(self, data):
        conn = self.db.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            # 1. Insert Master Bill
            q_bill = "INSERT INTO bills (patient_id, appointment_id, total_amount, discount, net_amount, status) VALUES (%s, %s, %s, %s, %s, 'Unpaid')"
            cursor.execute(q_bill, (data['patient_id'], data['appointment_id'], data['total_amount'], data['discount'], data['net_amount']))
            bill_id = cursor.lastrowid
            
            # 2. Insert Bill Details (Line Items)
            q_item = "INSERT INTO bill_details (bill_id, item_description, amount) VALUES (%s, %s, %s)"
            for item in data['items']:
                cursor.execute(q_item, (bill_id, item['desc'], item['amount']))
                
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Billing Error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def add_payment(self, bill_id, amount_paid, method):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("INSERT INTO payments (bill_id, amount_paid, payment_method) VALUES (%s, %s, %s)", (bill_id, amount_paid, method))
            
            # Recalculate and Update Bill Status
            cursor.execute("SELECT net_amount FROM bills WHERE bill_id = %s", (bill_id,))
            net = cursor.fetchone()['net_amount']
            
            cursor.execute("SELECT SUM(amount_paid) as paid FROM payments WHERE bill_id = %s", (bill_id,))
            paid = cursor.fetchone()['paid'] or 0
            
            status = 'Paid' if paid >= net else 'Partial' if paid > 0 else 'Unpaid'
            cursor.execute("UPDATE bills SET status = %s WHERE bill_id = %s", (status, bill_id))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Payment Error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def get_bill_pdf_data(self, bill_id):
        bill_info = self.db.execute_query("SELECT b.*, p.full_name, p.phone FROM bills b JOIN patients p ON b.patient_id = p.patient_id WHERE b.bill_id = %s", (bill_id,), fetch_one=True)
        items = self.db.execute_query("SELECT item_description, amount FROM bill_details WHERE bill_id = %s", (bill_id,), fetch=True)
        payments = self.db.execute_query("SELECT SUM(amount_paid) as total_paid FROM payments WHERE bill_id = %s", (bill_id,), fetch_one=True)
        
        if not bill_info: return None
        bill_info['items'] = items or []
        bill_info['total_paid'] = payments['total_paid'] if payments and payments['total_paid'] else 0
        return bill_info