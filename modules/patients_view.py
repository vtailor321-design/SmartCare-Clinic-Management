import customtkinter as ctk
from tkinter import ttk, messagebox
from services.patient_service import PatientService

class PatientsView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.service = PatientService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # --- Top Bar (Title & Search & Add Button) ---
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=20, pady=20)
        
        self.lbl_title = ctk.CTkLabel(self.top_frame, text="Patient Management", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1E3A8A")
        self.lbl_title.pack(side="left")
        
        self.btn_add = ctk.CTkButton(self.top_frame, text="+ Add New Patient", fg_color="#10B981", hover_color="#059669", font=ctk.CTkFont(weight="bold"), command=self.open_add_modal)
        self.btn_add.pack(side="right")
        
        self.entry_search = ctk.CTkEntry(self.top_frame, placeholder_text="Search Name/Phone...", width=250)
        self.entry_search.pack(side="right", padx=15)
        # Search instantly as user types
        self.entry_search.bind("<KeyRelease>", self.on_search)

        # --- Table Frame ---
        self.table_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="white")
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Tkinter Treeview Styling for Modern Look
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", rowheight=35, borderwidth=0, font=('Helvetica', 11))
        style.configure("Treeview.Heading", font=('Helvetica', 11, 'bold'), background="#F1F5F9", foreground="#1E293B", padding=5)
        style.map("Treeview", background=[("selected", "#EFF6FF")], foreground=[("selected", "#1D4ED8")])
        
        # Create Table
        columns = ("ID", "Name", "DOB", "Gender", "Phone", "Blood Group")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        
        self.tree.column("ID", width=80)
        self.tree.column("Name", width=200)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # --- Bottom Action Bar ---
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.btn_delete = ctk.CTkButton(self.bottom_frame, text="Delete Selected Patient", fg_color="#EF4444", hover_color="#DC2626", command=self.delete_patient)
        self.btn_delete.pack(side="right")

    def load_data(self, search_text=""):
        # Clear existing table data
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Fetch from database
        patients = self.service.get_all_patients(search_text)
        if patients:
            for p in patients:
                self.tree.insert("", "end", values=(p['patient_id'], p['full_name'], p['dob'], p['gender'], p['phone'], p['blood_group']))

    def on_search(self, event):
        self.load_data(self.entry_search.get().strip())

    def open_add_modal(self):
        """Opens a popup window to add a new patient."""
        modal = ctk.CTkToplevel(self)
        modal.title("Register New Patient")
        modal.geometry("450x650")
        modal.grab_set() # Lock focus to this window
        
        ctk.CTkLabel(modal, text="Patient Registration", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1E3A8A").pack(pady=20)
        
        def create_input(label_text, placeholder=""):
            ctk.CTkLabel(modal, text=label_text, text_color="#475569").pack(anchor="w", padx=40)
            entry = ctk.CTkEntry(modal, width=370, placeholder_text=placeholder)
            entry.pack(pady=(0, 15))
            return entry

        name_entry = create_input("Full Name", "e.g. Rahul Sharma")
        dob_entry = create_input("Date of Birth (YYYY-MM-DD)", "e.g. 1990-05-20")
        phone_entry = create_input("Phone Number", "10-digit number")
        address_entry = create_input("Address", "Full residential address")
        
        # Dropdowns
        ctk.CTkLabel(modal, text="Gender", text_color="#475569").pack(anchor="w", padx=40)
        gender_entry = ctk.CTkOptionMenu(modal, values=["Male", "Female", "Other"], width=370)
        gender_entry.pack(pady=(0, 15))
        
        ctk.CTkLabel(modal, text="Blood Group", text_color="#475569").pack(anchor="w", padx=40)
        bg_entry = ctk.CTkOptionMenu(modal, values=["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-", "Unknown"], width=370)
        bg_entry.pack(pady=(0, 20))
        
        def save():
            data = {
                "full_name": name_entry.get().strip(),
                "dob": dob_entry.get().strip(),
                "gender": gender_entry.get(),
                "phone": phone_entry.get().strip(),
                "address": address_entry.get().strip(),
                "blood_group": bg_entry.get(),
                "emergency_contact": ""
            }
            if not data['full_name'] or not data['dob'] or not data['phone']:
                messagebox.showerror("Validation Error", "Name, DOB, and Phone are required fields!")
                return
            
            # Save to Database
            self.service.add_patient(data)
            self.load_data() # Refresh Table
            modal.destroy()  # Close popup
            messagebox.showinfo("Success", "Patient registered successfully!")
            
        ctk.CTkButton(modal, text="Save Patient Data", width=370, height=40, font=ctk.CTkFont(weight="bold"), command=save).pack()
        
    def delete_patient(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a patient from the table to delete.")
            return
            
        item = self.tree.item(selected[0])
        p_id = item['values'][0]
        p_name = item['values'][1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to completely remove patient '{p_name}' from the system?"):
            self.service.delete_patient(p_id)
            self.load_data()
            messagebox.showinfo("Deleted", "Patient record deleted successfully.")