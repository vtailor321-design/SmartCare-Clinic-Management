import customtkinter as ctk
from tkinter import ttk, messagebox
from services.appointment_service import AppointmentService

class AppointmentsView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.service = AppointmentService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # --- Top Bar ---
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=20, pady=20)
        
        self.lbl_title = ctk.CTkLabel(self.top_frame, text="Appointments Schedule", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1E3A8A")
        self.lbl_title.pack(side="left")
        
        self.btn_add = ctk.CTkButton(self.top_frame, text="+ Book Appointment", fg_color="#10B981", hover_color="#059669", font=ctk.CTkFont(weight="bold"), command=self.open_booking_modal)
        self.btn_add.pack(side="right")
        
        self.entry_search = ctk.CTkEntry(self.top_frame, placeholder_text="Search Patient/Doctor...", width=220)
        self.entry_search.pack(side="right", padx=15)
        self.entry_search.bind("<KeyRelease>", self.on_search)

        # --- Table Frame ---
        self.table_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="white")
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", rowheight=35, borderwidth=0, font=('Helvetica', 11))
        style.configure("Treeview.Heading", font=('Helvetica', 11, 'bold'), background="#F1F5F9", foreground="#1E293B", padding=5)
        style.map("Treeview", background=[("selected", "#EFF6FF")], foreground=[("selected", "#1D4ED8")])
        
        columns = ("Appt ID", "Patient Name", "Doctor Name", "Date", "Time Slot", "Token", "Status")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
            
        self.tree.column("Appt ID", width=60)
        self.tree.column("Token", width=60)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # --- Bottom Action Bar ---
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.btn_complete = ctk.CTkButton(self.bottom_frame, text="Mark Completed", fg_color="#3B82F6", hover_color="#2563EB", command=lambda: self.change_status("Completed"))
        self.btn_complete.pack(side="right", padx=5)
        
        self.btn_cancel = ctk.CTkButton(self.bottom_frame, text="Cancel Appointment", fg_color="#EF4444", hover_color="#DC2626", command=lambda: self.change_status("Cancelled"))
        self.btn_cancel.pack(side="right", padx=5)

    def load_data(self, search_text=""):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        appointments = self.service.get_all_appointments(search_text)
        if appointments:
            for a in appointments:
                self.tree.insert("", "end", values=(
                    a['appointment_id'], a['patient_name'], a['doctor_name'], 
                    a['appointment_date'], a['time_slot'], a['token_number'], a['status']
                ))

    def on_search(self, event):
        self.load_data(self.entry_search.get().strip())
        
    def change_status(self, new_status):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select an appointment from the table first.")
            return
            
        item = self.tree.item(selected[0])
        appt_id = item['values'][0]
        current_status = item['values'][6]
        
        if current_status == new_status:
            return
            
        if messagebox.askyesno("Confirm", f"Mark appointment #{appt_id} as {new_status}?"):
            self.service.update_status(appt_id, new_status)
            self.load_data()

    def open_booking_modal(self):
        patients_data, doctors_data = self.service.get_dropdown_data()
        
        if not patients_data or not doctors_data:
            messagebox.showerror("Error", "You need at least one Patient and one Doctor in the system to book an appointment.")
            return

        modal = ctk.CTkToplevel(self)
        modal.title("Book Appointment")
        modal.geometry("450x600")
        modal.grab_set() 
        
        ctk.CTkLabel(modal, text="New Appointment Booking", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1E3A8A").pack(pady=20)
        
        # Format Data for Dropdowns (ID - Name format)
        patient_list = [f"{p['patient_id']} - {p['full_name']} ({p['phone']})" for p in patients_data]
        doctor_list = [f"{d['doctor_id']} - {d['full_name']} ({d['specialization']})" for d in doctors_data]
        time_slots = ["09:00 AM - 09:30 AM", "09:30 AM - 10:00 AM", "10:00 AM - 10:30 AM", "10:30 AM - 11:00 AM",
                      "11:00 AM - 11:30 AM", "11:30 AM - 12:00 PM", "05:00 PM - 05:30 PM", "05:30 PM - 06:00 PM"]
        
        ctk.CTkLabel(modal, text="Select Patient", text_color="#475569").pack(anchor="w", padx=40)
        patient_dd = ctk.CTkOptionMenu(modal, values=patient_list, width=370)
        patient_dd.pack(pady=(0, 15))
        
        ctk.CTkLabel(modal, text="Select Doctor", text_color="#475569").pack(anchor="w", padx=40)
        doctor_dd = ctk.CTkOptionMenu(modal, values=doctor_list, width=370)
        doctor_dd.pack(pady=(0, 15))
        
        ctk.CTkLabel(modal, text="Appointment Date (YYYY-MM-DD)", text_color="#475569").pack(anchor="w", padx=40)
        date_entry = ctk.CTkEntry(modal, width=370, placeholder_text="e.g. 2026-11-20")
        date_entry.pack(pady=(0, 15))
        
        ctk.CTkLabel(modal, text="Time Slot", text_color="#475569").pack(anchor="w", padx=40)
        time_dd = ctk.CTkOptionMenu(modal, values=time_slots, width=370)
        time_dd.pack(pady=(0, 25))
        
        def save():
            date_val = date_entry.get().strip()
            if not date_val:
                messagebox.showerror("Error", "Date is required!")
                return
                
            # Extract IDs from the dropdown text ("ID - Name...")
            p_id = int(patient_dd.get().split(" - ")[0])
            d_id = int(doctor_dd.get().split(" - ")[0])
            
            data = {
                "patient_id": p_id,
                "doctor_id": d_id,
                "appointment_date": date_val,
                "time_slot": time_dd.get()
            }
            
            success, msg = self.service.book_appointment(data)
            if success:
                messagebox.showinfo("Success", msg)
                self.load_data()
                modal.destroy()
            else:
                messagebox.showerror("Booking Failed", msg)

        ctk.CTkButton(modal, text="Confirm Booking", width=370, height=40, font=ctk.CTkFont(weight="bold"), command=save).pack()