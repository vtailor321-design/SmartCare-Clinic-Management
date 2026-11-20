import customtkinter as ctk
from tkinter import ttk, messagebox
from services.prescription_service import PrescriptionService
from utils.pdf_generator import generate_prescription_pdf
import os

class PrescriptionsView(ctk.CTkFrame):
    def __init__(self, master, user_data, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.user_data = user_data
        self.service = PrescriptionService()
        
        # Check Role Security
        if self.user_data['role'] != 'Doctor':
            self.setup_unauthorized_ui()
            return
            
        self.setup_ui()
        self.load_appointments()

    def setup_unauthorized_ui(self):
        lbl = ctk.CTkLabel(self, text="Access Restricted.\nOnly Doctors can write Prescriptions.", font=("Helvetica", 24), text_color="#EF4444")
        lbl.place(relx=0.5, rely=0.5, anchor="center")

    def setup_ui(self):
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=20, pady=20)
        
        self.lbl_title = ctk.CTkLabel(self.top_frame, text="Write Prescription", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1E3A8A")
        self.lbl_title.pack(side="left")
        
        # Table of Pending Appointments for this Doctor
        self.table_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="white")
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(self.table_frame, text="Your Pending Appointments", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        style = ttk.Style()
        columns = ("Appt ID", "Patient ID", "Patient Name", "Date", "Token")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
            
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.btn_write = ctk.CTkButton(self.table_frame, text="Write Prescription for Selected", fg_color="#10B981", hover_color="#059669", command=self.open_prescription_form)
        self.btn_write.pack(pady=10)

    def load_appointments(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        appts = self.service.get_appointments_for_prescription(self.user_data['user_id'])
        if appts:
            for a in appts:
                self.tree.insert("", "end", values=(a['appointment_id'], a['patient_id'], a['patient_name'], a['appointment_date'], a['token_number']))

    def open_prescription_form(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select an appointment from the list.")
            return
            
        item = self.tree.item(selected[0])
        appt_id = item['values'][0]
        patient_id = item['values'][1]
        patient_name = item['values'][2]
        
        modal = ctk.CTkToplevel(self)
        modal.title(f"Prescription - {patient_name}")
        modal.geometry("700x700")
        modal.grab_set()
        
        ctk.CTkLabel(modal, text=f"Prescribing for: {patient_name}", font=ctk.CTkFont(size=18, weight="bold"), text_color="#1E3A8A").pack(pady=15)
        
        scroll = ctk.CTkScrollableFrame(modal, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Diagnosis
        ctk.CTkLabel(scroll, text="Diagnosis", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10)
        diag_entry = ctk.CTkTextbox(scroll, width=650, height=60)
        diag_entry.pack(pady=(0, 15))
        
        # Dynamic Medicines Section
        ctk.CTkLabel(scroll, text="Medicines (Rx)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10)
        meds_container = ctk.CTkFrame(scroll, fg_color="transparent")
        meds_container.pack(fill="x", pady=5)
        
        medicine_rows = []
        
        def add_med_row():
            row = ctk.CTkFrame(meds_container, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            n = ctk.CTkEntry(row, width=250, placeholder_text="Medicine Name")
            n.pack(side="left", padx=5)
            d = ctk.CTkEntry(row, width=150, placeholder_text="Dosage (e.g. 1-0-1)")
            d.pack(side="left", padx=5)
            dur = ctk.CTkEntry(row, width=150, placeholder_text="Duration (e.g. 5 Days)")
            dur.pack(side="left", padx=5)
            
            medicine_rows.append({"name": n, "dosage": d, "duration": dur})
            
        add_med_row() # Add one blank row by default
        ctk.CTkButton(scroll, text="+ Add Another Medicine", fg_color="#3B82F6", width=200, command=add_med_row).pack(anchor="w", padx=15, pady=10)
        
        # Instructions & Follow-up
        ctk.CTkLabel(scroll, text="General Instructions", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(15,0))
        inst_entry = ctk.CTkTextbox(scroll, width=650, height=60)
        inst_entry.pack(pady=(0, 15))
        
        ctk.CTkLabel(scroll, text="Follow-up Date (YYYY-MM-DD)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10)
        follow_entry = ctk.CTkEntry(scroll, width=250)
        follow_entry.pack(anchor="w", padx=10, pady=(0, 20))
        
        def save():
            diag = diag_entry.get("1.0", "end-1c").strip()
            if not diag:
                messagebox.showerror("Error", "Diagnosis cannot be empty.")
                return
                
            meds_data = []
            for r in medicine_rows:
                n = r['name'].get().strip()
                if n: meds_data.append({"name": n, "dosage": r['dosage'].get(), "duration": r['duration'].get()})
                
            data = {
                "appointment_id": appt_id,
                "patient_id": patient_id,
                "doctor_id": self.service.get_doctor_id(self.user_data['user_id']),
                "diagnosis": diag,
                "instructions": inst_entry.get("1.0", "end-1c").strip(),
                "follow_up": follow_entry.get().strip() or None,
                "medicines": meds_data
            }
            
            if self.service.save_prescription(data):
                messagebox.showinfo("Success", "Prescription saved successfully! Generating PDF...")
                self.load_appointments()
                modal.destroy()
                
                # Generate and Open PDF
                pdf_data = self.service.get_full_prescription_data_for_pdf(appt_id)
                if pdf_data:
                    filename = f"Prescription_{appt_id}_{patient_name.replace(' ', '_')}.pdf"
                    path = generate_prescription_pdf(pdf_data, filename)
                    os.startfile(os.path.abspath(path)) # Opens the PDF automatically (Windows only)
            else:
                messagebox.showerror("Error", "Database error occurred.")

        ctk.CTkButton(modal, text="Save & Print Prescription", width=650, height=45, font=ctk.CTkFont(weight="bold"), command=save).pack(pady=10)