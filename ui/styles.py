import customtkinter as ctk

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, current_role, switch_callback, **kwargs):
        super().__init__(master, fg_color="#1E3A8A", corner_radius=0, **kwargs)
        
        self.current_role = current_role
        self.switch_callback = switch_callback
        self.active_button = None
        self.buttons = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        # Brand Logo/Text
        self.brand_label = ctk.CTkLabel(self, text="SmartCare", font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
        self.brand_label.pack(pady=(30, 10))
        
        self.role_label = ctk.CTkLabel(self, text=f"{self.current_role} Panel", font=ctk.CTkFont(size=12), text_color="#93C5FD")
        self.role_label.pack(pady=(0, 30))
        
        # Navigation Links based on Role
        nav_items = ["Dashboard", "Patients", "Appointments"]
        
        if self.current_role in ["Admin", "Receptionist"]:
            nav_items.extend(["Billing"])
            
        if self.current_role in ["Admin"]:
            nav_items.extend(["Doctors", "Inventory", "Reports"])
            
        if self.current_role in ["Doctor"]:
            nav_items.extend(["Prescriptions"])
            
        # Create buttons
        for item in nav_items:
            btn = ctk.CTkButton(
                self, text=item, anchor="w", fg_color="transparent", 
                text_color="white", hover_color="#1E40AF", font=ctk.CTkFont(size=15),
                command=lambda name=item: self.on_nav_click(name)
            )
            btn.pack(fill="x", pady=5, padx=15)
            self.buttons[item] = btn
            
        # Logout Button at bottom
        self.logout_btn = ctk.CTkButton(
            self, text="Logout", anchor="w", fg_color="#DC2626", 
            text_color="white", hover_color="#B91C1C", font=ctk.CTkFont(size=15),
            command=lambda: self.switch_callback("Logout")
        )
        self.logout_btn.pack(side="bottom", fill="x", pady=20, padx=15)
        
    def on_nav_click(self, view_name):
        # Highlight active button
        if self.active_button:
            self.active_button.configure(fg_color="transparent")
        
        self.active_button = self.buttons[view_name]
        self.active_button.configure(fg_color="#3B82F6") # Highlight color
        
        self.switch_callback(view_name)