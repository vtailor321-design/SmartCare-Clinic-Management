import sys
import customtkinter as ctk
from tkinter import messagebox
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from services.auth_service import AuthService
from database.db_core import DatabaseManager

class ApplicationManager:
    def __init__(self):
        # 1. Test Database Connection
        db = DatabaseManager()
        conn = db.get_connection()
        if not conn:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Database Error", "Failed to connect to MySQL database.\nPlease check XAMPP/MySQL and config/database.py.")
            sys.exit(1)
        conn.close()

        # 2. Ensure default admin exists
        auth = AuthService()
        auth.initialize_default_admin()
        
        # 3. Start Application Cycle
        self.show_login()

    def show_login(self):
        self.login_app = LoginWindow(on_login_success=self.show_main_window)
        self.login_app.mainloop()

    def show_main_window(self, user_data):
        self.main_app = MainWindow(user_data=user_data, logout_callback=self.on_logout)
        self.main_app.mainloop()
        
    def on_logout(self):
        # Restart the application cycle
        self.show_login()

if __name__ == "__main__":
    ApplicationManager()