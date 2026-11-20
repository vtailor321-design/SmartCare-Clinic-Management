from database.db_core import DatabaseManager

class ReportService:
    def __init__(self):
        self.db = DatabaseManager()

    def get_summary_stats(self):
        """Fetches total counts for the summary cards."""
        patients = self.db.execute_query("SELECT COUNT(*) as total FROM patients", fetch_one=True)
        # Calculate total revenue from paid or partially paid bills
        revenue = self.db.execute_query("SELECT SUM(amount_paid) as total FROM payments", fetch_one=True)
        doctors = self.db.execute_query("SELECT COUNT(*) as total FROM doctors", fetch_one=True)
        
        return {
            "total_patients": patients['total'] if patients and patients['total'] else 0,
            "total_revenue": revenue['total'] if revenue and revenue['total'] else 0.0,
            "total_doctors": doctors['total'] if doctors and doctors['total'] else 0
        }

    def get_appointment_stats(self):
        """Fetches data for Appointment Status Chart."""
        query = "SELECT status, COUNT(*) as count FROM appointments GROUP BY status"
        result = self.db.execute_query(query, fetch=True)
        return result if result else []

    def get_revenue_trends(self):
        """Fetches last 7 days revenue for the Trend Chart."""
        query = """
            SELECT a.appointment_date as date, SUM(p.amount_paid) as daily_rev 
            FROM payments p
            JOIN bills b ON p.bill_id = b.bill_id
            JOIN appointments a ON b.appointment_id = a.appointment_id
            GROUP BY a.appointment_date 
            ORDER BY a.appointment_date DESC LIMIT 7
        """
        result = self.db.execute_query(query, fetch=True)
        return result if result else []