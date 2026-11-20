import customtkinter as ctk
from database.db_core import DatabaseManager
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, user_data, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.user_data = user_data
        self.db = DatabaseManager()
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        # Header
        self.header = ctk.CTkLabel(self, text="Dashboard Overview", font=ctk.CTkFont(size=28, weight="bold"), text_color="#1E3A8A")
        self.header.grid(row=0, column=0, sticky="w", pady=(20, 30), padx=20)
        
        # Cards Frame
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.grid(row=1, column=0, sticky="ew", padx=20)
        self.cards_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Initialize Card Widgets
        self.lbl_patients = self.create_card(self.cards_frame, "Total Patients", 0)
        self.lbl_doctors = self.create_card(self.cards_frame, "Total Doctors", 1)
        self.lbl_appointments = self.create_card(self.cards_frame, "Today's Appointments", 2)
        
        # Chart Frame
        self.chart_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.chart_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=30)
        self.grid_rowconfigure(2, weight=1)

    def create_card(self, parent, title, col):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10, height=120)
        card.grid(row=0, column=col, sticky="ew", padx=10)
        card.grid_propagate(False)
        
        title_lbl = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14), text_color="#64748B")
        title_lbl.place(relx=0.1, rely=0.2)
        
        value_lbl = ctk.CTkLabel(card, text="...", font=ctk.CTkFont(size=32, weight="bold"), text_color="#1E3A8A")
        value_lbl.place(relx=0.1, rely=0.5)
        
        return value_lbl

    def load_data(self):
        # Fetch real-time data from MySQL
        patient_count = self.db.execute_query("SELECT COUNT(*) as count FROM patients", fetch_one=True)
        doctor_count = self.db.execute_query("SELECT COUNT(*) as count FROM doctors", fetch_one=True)
        appt_count = self.db.execute_query("SELECT COUNT(*) as count FROM appointments WHERE appointment_date = CURDATE()", fetch_one=True)
        
        # Update Labels
        self.lbl_patients.configure(text=str(patient_count['count']) if patient_count else "0")
        self.lbl_doctors.configure(text=str(doctor_count['count']) if doctor_count else "0")
        self.lbl_appointments.configure(text=str(appt_count['count']) if appt_count else "0")
        
        self.draw_chart()

    def draw_chart(self):
        # 1. Clear old charts to prevent duplication on refresh
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # 2. Fetch REAL data for Today's Appointments
        query = """
            SELECT status, COUNT(*) as count 
            FROM appointments 
            WHERE appointment_date = CURDATE() 
            GROUP BY status
        """
        stats = self.db.execute_query(query, fetch=True)
        
        # Initialize default counts
        counts_dict = {'Completed': 0, 'Pending': 0, 'Cancelled': 0}
        
        # Update with real database values
        if stats:
            for row in stats:
                if row['status'] in counts_dict:
                    counts_dict[row['status']] = row['count']
                    
        categories = list(counts_dict.keys())
        counts = list(counts_dict.values())

        # 3. Draw Matplotlib Chart
        fig, ax = plt.subplots(figsize=(6, 3), dpi=100)
        ax.bar(categories, counts, color=['#10B981', '#F59E0B', '#EF4444'], width=0.5)
        
        # NAYA TITLE JO DIKHNA CHAHIYE
        ax.set_title("Today's Appointments Status", fontsize=12, color="#1E3A8A")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Force Y-axis to show only whole numbers (integers like 0, 1, 2)
        ax.yaxis.get_major_locator().set_params(integer=True)
        
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)