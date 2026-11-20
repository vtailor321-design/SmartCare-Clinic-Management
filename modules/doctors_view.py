import customtkinter as ctk
from tkinter import ttk, messagebox
from services.doctor_service import DoctorService

class DoctorsView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.service = DoctorService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # --- Top Bar ---
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=20, pady=20)
        
        self.lbl_title = ctk.CTkLabel(self.top_frame, text="Doctor Management", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1E3A8A")
        self.lbl_title.pack(side="left")
        
        self.btn_add = ctk.CTkButton(self.top_frame, text="+ Add New Doctor", fg_color="#10B981", hover_color="#059669", font=ctk.CTkFont(weight="bold"), command=self.open_add_modal)
        self.btn_add.pack(side="right")
        
        self.entry_search = ctk.CTkEntry(self.top_frame, placeholder_text="Search Name/Specialty...", width=250)
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
        
        columns = ("Doc ID", "User ID", "Name", "Specialization", "Phone", "Consultation Fee (₹)", "Schedule")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
            
        self.tree.column("Doc ID", width=60)
        self.tree.column("User ID", width=0, stretch=False) # Hidden column for deletion logic
        self.tree.column("Name", width=180)
        self.tree.column("Specialization", width=150)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # --- Bottom Action Bar ---
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.btn_delete = ctk.CTkButton(self.bottom_frame, text="Remove Doctor", fg_color="#EF4444", hover_color="#DC2626", command=self.delete_doctor)
        self.btn_delete.pack(side="right")

    def load_data(self, search_text=""):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        doctors = self.service.get_all_doctors(search_text)
        if doctors:
            for d in doctors:
                self.tree.insert("", "end", values=(
                    d['doctor_id'], d['user_id'], d['full_name'], 
                    d['specialization'], d['phone'], d['consultation_fee'], d['availability_schedule']
                ))

    def on_search(self, event):
        self.load_data(self.entry_search.get().strip())

    def open_add_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Register New Doctor")
        modal.geometry("500x700")
        modal.grab_set() 
        
        ctk.CTkLabel(modal, text="Doctor Registration Profile", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1E3A8A").pack(pady=(15, 5))
        
        # Using a scrollable frame for the large form
        scroll = ctk.CTkScrollableFrame(modal, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        def create_input(label_text, placeholder="", is_password=False):
            ctk.CTkLabel(scroll, text=label_text, text_color="#475569").pack(anchor="w", padx=20)
            entry = ctk.CTkEntry(scroll, width=400, placeholder_text=placeholder, show="*" if is_password else "")
            entry.pack(pady=(0, 15))
            return entry

        # Account Details
        ctk.CTkLabel(scroll, text="Login Credentials", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(5,5))
        username_entry = create_input("Username (For Login)", "e.g. dr_sharma")
        password_entry = create_input("Password", "Enter secure password", is_password=True)
        
        # Professional Details
        ctk.CTkLabel(scroll, text="Professional Profile", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(15,5))
        name_entry = create_input("Full Name", "e.g. Dr. Rajesh Sharma")
        spec_entry = create_input("Specialization", "e.g. Cardiologist, General Physician")
        qual_entry = create_input("Qualification", "e.g. MBBS, MD")
        phone_entry = create_input("Phone Number", "Contact number")
        email_entry = create_input("Email Address", "Email ID")
        fee_entry = create_input("Consultation Fee (₹)", "e.g. 500")
        sched_entry = create_input("Availability Schedule", "e.g. Mon-Fri: 10AM - 4PM")
        
        def save():
            try:
                data = {
                    "username": username_entry.get().strip(),
                    "password": password_entry.get().strip(),
                    "full_name": name_entry.get().strip(),
                    "specialization": spec_entry.get().strip(),
                    "qualification": qual_entry.get().strip(),
                    "phone": phone_entry.get().strip(),
                    "email": email_entry.get().strip(),
                    "consultation_fee": float(fee_entry.get().strip() or 0),
                    "availability_schedule": sched_entry.get().strip()
                }
                
                if not data['username'] or not data['password'] or not data['full_name'] or not data['specialization']:
                    messagebox.showerror("Validation Error", "Username, Password, Name, and Specialization are required!")
                    return
                
                if self.service.add_doctor(data):
                    self.load_data() 
                    modal.destroy()  
                    messagebox.showinfo("Success", "Doctor registered successfully!\nThey can now login with their username/password.")
                else:
                    messagebox.showerror("Database Error", "Failed to add doctor. Username might already exist.")
                    
            except ValueError:
                messagebox.showerror("Format Error", "Consultation Fee must be a valid number.")

        ctk.CTkButton(scroll, text="Save Doctor Profile", width=400, height=40, font=ctk.CTkFont(weight="bold"), command=save).pack(pady=20)
        
    def delete_doctor(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a doctor to remove.")
            return
            
        item = self.tree.item(selected[0])
        user_id = item['values'][1] # Getting the hidden User ID
        doc_name = item['values'][2]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to remove {doc_name}?\nThis will also delete their login access."):
            self.service.delete_doctor(user_id)
            self.load_data()
            messagebox.showinfo("Deleted", "Doctor profile and login access removed.")