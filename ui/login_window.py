import customtkinter as ctk
from tkinter import messagebox
from services.auth_service import AuthService

class LoginWindow(ctk.CTk):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.auth = AuthService()
        
        # Window configuration (Purana Centered Style)
        self.title("SmartCare - Secure Login")
        self.geometry("500x550")
        self.resizable(False, False) 
        ctk.set_appearance_mode("light")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main centered frame
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        lbl_welcome = ctk.CTkLabel(self.main_frame, text="SmartCare Clinic", font=ctk.CTkFont(size=32, weight="bold"), text_color="#1E3A8A")
        lbl_welcome.pack(pady=(10, 5))
        
        lbl_sub = ctk.CTkLabel(self.main_frame, text="Please login to your account", font=ctk.CTkFont(size=14), text_color="#64748B")
        lbl_sub.pack(pady=(0, 20))
        
        # --- TABVIEW (Split between Admin and Doctor) ---
        self.tabview = ctk.CTkTabview(self.main_frame, width=400, fg_color="#F8FAFC", segmented_button_selected_color="#1E3A8A", anchor="n")
        self.tabview.pack(pady=10, fill="both", expand=True)
        
        tab_admin = self.tabview.add("Admin / Staff")
        tab_doctor = self.tabview.add("Are you a Doctor?")
        # Internal Override to force Center alignment
        self.tabview._segmented_button.grid_configure(sticky="n")
        
        # ----------------------------------------
        # TAB 1: Admin / Receptionist Login
        # ----------------------------------------
        self.admin_user = ctk.CTkEntry(tab_admin, width=320, height=45, placeholder_text="Username (e.g. admin)", font=ctk.CTkFont(size=14))
        self.admin_user.pack(pady=(30, 15))
        
        self.admin_pass = ctk.CTkEntry(tab_admin, width=320, height=45, placeholder_text="Password (e.g. admin123)", show="*", font=ctk.CTkFont(size=14))
        self.admin_pass.pack(pady=(0, 30))
        
        btn_admin_login = ctk.CTkButton(
            tab_admin, text="Login to Dashboard", width=320, height=45, 
            fg_color="#10B981", hover_color="#059669", font=ctk.CTkFont(size=15, weight="bold"),
            command=lambda: self.process_login(self.admin_user.get(), self.admin_pass.get())
        )
        btn_admin_login.pack()

        # ----------------------------------------
        # TAB 2: Doctor Login
        # ----------------------------------------
        ctk.CTkLabel(tab_doctor, text="👨‍⚕️ Doctor's Portal", font=ctk.CTkFont(size=16, weight="bold"), text_color="#3B82F6").pack(pady=(15, 5))
        
        self.doc_user = ctk.CTkEntry(tab_doctor, width=320, height=45, placeholder_text="Doctor Username (e.g. dr_anil)", font=ctk.CTkFont(size=14))
        self.doc_user.pack(pady=(10, 15))
        
        self.doc_pass = ctk.CTkEntry(tab_doctor, width=320, height=45, placeholder_text="Password", show="*", font=ctk.CTkFont(size=14))
        self.doc_pass.pack(pady=(0, 25))
        
        btn_doc_login = ctk.CTkButton(
            tab_doctor, text="Access Prescriptions", width=320, height=45, 
            fg_color="#3B82F6", hover_color="#2563EB", font=ctk.CTkFont(size=15, weight="bold"),
            command=lambda: self.process_login(self.doc_user.get(), self.doc_pass.get())
        )
        btn_doc_login.pack()

        # ==========================================
        # SMART KEYBOARD BINDINGS (ENTER KEY LOGIC)
        # ==========================================
        # Admin tab enter events
        self.admin_user.bind("<Return>", lambda event: self.admin_pass.focus())
        self.admin_pass.bind("<Return>", lambda event: self.process_login(self.admin_user.get(), self.admin_pass.get()))
        
        # Doctor tab enter events
        self.doc_user.bind("<Return>", lambda event: self.doc_pass.focus())
        self.doc_pass.bind("<Return>", lambda event: self.process_login(self.doc_user.get(), self.doc_pass.get()))

        # Auto-focus: App open hote hi typing cursor apne aap Username box me aa jayega
        self.admin_user.focus()

    def process_login(self, username, password):
        username = username.strip()
        password = password.strip()
        
        if not username or not password:
            messagebox.showwarning("Warning", "Please enter both username and password.")
            return
            
        user_data = self.auth.login(username, password)
        
        if user_data:
            self.destroy() 
            self.on_login_success(user_data) 
        else:
            messagebox.showerror("Login Failed", "Invalid credentials. Please try again.")