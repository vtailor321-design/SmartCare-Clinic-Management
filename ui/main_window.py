import customtkinter as ctk
from ui.sidebar import Sidebar
from modules.dashboard_view import DashboardView
from modules.patients_view import PatientsView
from modules.doctors_view import DoctorsView
from tkinter import messagebox
from modules.appointments_view import AppointmentsView
from modules.prescriptions_view import PrescriptionsView
from modules.billing_view import BillingView
from modules.inventory_view import InventoryView
from modules.reports_view import ReportsView


class MainWindow(ctk.CTk):
    def __init__(self, user_data, logout_callback):
        super().__init__()
        
        self.user_data = user_data
        self.logout_callback = logout_callback
        
        self.title("SmartCare - Professional Clinic Management System")
        self.geometry("1100x700")
        self.minsize(900, 600)
        ctk.set_appearance_mode("light")
        self.configure(fg_color="#F4F6F9")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.setup_ui()
        
    def setup_ui(self):
        self.sidebar = Sidebar(self, current_role=self.user_data['role'], switch_callback=self.switch_view, width=250)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew")
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)
        
        self.views = {}
        self.sidebar.on_nav_click("Dashboard")
        
    def switch_view(self, view_name):
        if view_name == "Logout":
            self.destroy()
            self.logout_callback()
            return
            
        for child in self.main_content.winfo_children():
            child.pack_forget()
            
        # Module Router (Now with Auto-Refresh!)
        if view_name == "Dashboard":
            if "Dashboard" not in self.views:
                self.views["Dashboard"] = DashboardView(self.main_content, self.user_data)
            else:
                self.views["Dashboard"].load_data() # Yaha Refresh hoga!
            self.views["Dashboard"].pack(fill="both", expand=True)
            
        elif view_name == "Patients":
            if "Patients" not in self.views:
                self.views["Patients"] = PatientsView(self.main_content)
            else:
                self.views["Patients"].load_data() # Yaha Refresh hoga!
            self.views["Patients"].pack(fill="both", expand=True)
            
        elif view_name == "Doctors":
            if self.user_data['role'] != "Admin":
                messagebox.showerror("Access Denied", "Only Administrators can access Doctor Management.")
                self.sidebar.on_nav_click("Dashboard")
                return
            if "Doctors" not in self.views:
                self.views["Doctors"] = DoctorsView(self.main_content)
            else:
                self.views["Doctors"].load_data() # Yaha Refresh hoga!
            self.views["Doctors"].pack(fill="both", expand=True)
        elif view_name == "Billing":
            if "Billing" not in self.views:
                self.views["Billing"] = BillingView(self.main_content)
            else:
                self.views["Billing"].load_data()
            self.views["Billing"].pack(fill="both", expand=True)    

        elif view_name == "Appointments":
            if "Appointments" not in self.views:
                self.views["Appointments"] = AppointmentsView(self.main_content)
            else:
                self.views["Appointments"].load_data() # Yaha Refresh hoga!
            self.views["Appointments"].pack(fill="both", expand=True)

        elif view_name == "Prescriptions":
            if "Prescriptions" not in self.views:
                self.views["Prescriptions"] = PrescriptionsView(self.main_content, self.user_data)
            else:
                if hasattr(self.views["Prescriptions"], 'load_appointments'):
                    self.views["Prescriptions"].load_appointments() # Yaha Refresh hoga!
            self.views["Prescriptions"].pack(fill="both", expand=True)
        elif view_name == "Inventory":
            if self.user_data['role'] != "Admin":
                messagebox.showerror("Access Denied", "Only Administrators can access Inventory.")
                self.sidebar.on_nav_click("Dashboard")
                return
                
            if "Inventory" not in self.views:
                self.views["Inventory"] = InventoryView(self.main_content)
            else:
                self.views["Inventory"].load_data()
            self.views["Inventory"].pack(fill="both", expand=True)
        elif view_name == "Reports":
            if self.user_data['role'] != "Admin":
                messagebox.showerror("Access Denied", "Only Administrators can view Reports.")
                self.sidebar.on_nav_click("Dashboard")
                return
                
            if "Reports" not in self.views:
                self.views["Reports"] = ReportsView(self.main_content)
            else:
                self.views["Reports"].load_data()
            self.views["Reports"].pack(fill="both", expand=True)
        else:
            placeholder = ctk.CTkFrame(self.main_content, fg_color="transparent")
            placeholder.pack(fill="both", expand=True)
            lbl = ctk.CTkLabel(placeholder, text=f"{view_name} Module\n(Coming in next phases)", font=("Helvetica", 24), text_color="#94A3B8")
            lbl.place(relx=0.5, rely=0.5, anchor="center")
            