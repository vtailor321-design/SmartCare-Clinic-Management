import customtkinter as ctk
from services.report_service import ReportService
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ReportsView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.service = ReportService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # Top Bar
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        self.lbl_title = ctk.CTkLabel(self.top_frame, text="Business Analytics & Reports", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1E3A8A")
        self.lbl_title.pack(side="left")
        
        self.btn_refresh = ctk.CTkButton(self.top_frame, text="🔄 Refresh Data", fg_color="#10B981", hover_color="#059669", command=self.load_data)
        self.btn_refresh.pack(side="right")

        # Summary Cards Frame
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="x", padx=20, pady=10)
        self.cards_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.lbl_patients = self.create_card(self.cards_frame, "Total Registered Patients", 0, "#3B82F6")
        self.lbl_revenue = self.create_card(self.cards_frame, "Total Revenue Collected (₹)", 1, "#10B981")
        self.lbl_doctors = self.create_card(self.cards_frame, "Active Doctors", 2, "#F59E0B")

        # Charts Frame
        self.charts_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.charts_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.charts_frame.grid_columnconfigure((0, 1), weight=1)
        self.charts_frame.grid_rowconfigure(0, weight=1)
        
        self.chart1_container = ctk.CTkFrame(self.charts_frame, fg_color="white", corner_radius=10)
        self.chart1_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self.chart2_container = ctk.CTkFrame(self.charts_frame, fg_color="white", corner_radius=10)
        self.chart2_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

    def create_card(self, parent, title, col, color):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10, height=120)
        card.grid(row=0, column=col, sticky="ew", padx=10)
        card.grid_propagate(False)
        
        # Color bar on top
        color_bar = ctk.CTkFrame(card, fg_color=color, height=5, corner_radius=0)
        color_bar.place(relwidth=1.0, rely=0)
        
        title_lbl = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14), text_color="#64748B")
        title_lbl.place(relx=0.1, rely=0.25)
        
        value_lbl = ctk.CTkLabel(card, text="...", font=ctk.CTkFont(size=32, weight="bold"), text_color="#1E293B")
        value_lbl.place(relx=0.1, rely=0.55)
        
        return value_lbl

    def load_data(self):
        # 1. Update Cards
        stats = self.service.get_summary_stats()
        self.lbl_patients.configure(text=str(stats['total_patients']))
        self.lbl_revenue.configure(text=f"₹ {stats['total_revenue']:,.2f}")
        self.lbl_doctors.configure(text=str(stats['total_doctors']))
        
        # 2. Draw Charts
        self.draw_appointment_chart()
        self.draw_revenue_chart()

    def draw_appointment_chart(self):
        # Clear old chart
        for widget in self.chart1_container.winfo_children():
            widget.destroy()
            
        data = self.service.get_appointment_stats()
        labels = [item['status'] for item in data] if data else ["No Data"]
        counts = [item['count'] for item in data] if data else [1]
        colors = ['#3B82F6', '#10B981', '#EF4444', '#F59E0B'][:len(labels)]
        
        fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
        ax.pie(counts, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, textprops={'fontsize': 10})
        ax.set_title("Appointments by Status", fontsize=12, pad=15)
        
        canvas = FigureCanvasTkAgg(fig, master=self.chart1_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def draw_revenue_chart(self):
        # Clear old chart
        for widget in self.chart2_container.winfo_children():
            widget.destroy()
            
        data = self.service.get_revenue_trends()
        dates = [str(item['date'])[-5:] for item in reversed(data)] if data else ["No Data"]
        revs = [float(item['daily_rev']) for item in reversed(data)] if data else [0]
        
        fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
        ax.bar(dates, revs, color='#10B981', width=0.5)
        ax.set_title("Recent Revenue Trend (Last 7 Days)", fontsize=12, pad=15)
        ax.set_ylabel("Amount (₹)", fontsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        canvas = FigureCanvasTkAgg(fig, master=self.chart2_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)