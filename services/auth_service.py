from database.db_core import DatabaseManager
from utils.security import hash_password, verify_password

class AuthService:
    def __init__(self):
        self.db = DatabaseManager()

    def login(self, username, password):
        """Validates credentials and returns user data if successful."""
        query = "SELECT user_id, username, password_hash, role, full_name FROM users WHERE username = %s AND is_active = 1"
        user = self.db.execute_query(query, (username,), fetch_one=True)
        
        if user and verify_password(password, user['password_hash']):
            # Remove password hash from the returned dictionary for security in memory
            del user['password_hash']
            return user
        return None

    def initialize_default_admin(self):
        """Creates a default admin user if the users table is completely empty."""
        query_check = "SELECT COUNT(*) as count FROM users"
        result = self.db.execute_query(query_check, fetch_one=True)
        
        if result and result['count'] == 0:
            hashed_pw = hash_password("admin123")
            query_insert = """
                INSERT INTO users (username, password_hash, role, full_name) 
                VALUES (%s, %s, %s, %s)
            """
            self.db.execute_query(query_insert, ("admin", hashed_pw, "Admin", "System Administrator"))
            print("Default admin created automatically. Username: 'admin', Password: 'admin123'")
