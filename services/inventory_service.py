from database.db_core import DatabaseManager

class InventoryService:
    def __init__(self):
        self.db = DatabaseManager()

    def get_inventory_status(self, search_text=""):
        """Fetches all medicines along with their current stock and low stock warnings."""
        query = """
            SELECT m.medicine_id, m.name, m.category, m.manufacturer, m.unit_price, 
                   COALESCE(i.stock_quantity, 0) as stock_quantity, 
                   COALESCE(i.low_stock_threshold, 10) as threshold
            FROM medicines m
            LEFT JOIN medicine_inventory i ON m.medicine_id = i.medicine_id
        """
        if search_text:
            query += " WHERE m.name LIKE %s OR m.category LIKE %s"
            search_term = f"%{search_text}%"
            query += " ORDER BY m.name ASC"
            return self.db.execute_query(query, (search_term, search_term), fetch=True)
            
        query += " ORDER BY m.name ASC"
        return self.db.execute_query(query, fetch=True)

    def add_new_medicine(self, data):
        """Adds a new medicine to the master catalog and initializes its inventory to 0."""
        conn = self.db.get_connection()
        if not conn: return False
        
        try:
            cursor = conn.cursor()
            # Insert into master catalog
            cursor.execute("""
                INSERT INTO medicines (name, generic_name, category, manufacturer, unit_price) 
                VALUES (%s, %s, %s, %s, %s)
            """, (data['name'], data['generic_name'], data['category'], data['manufacturer'], data['unit_price']))
            
            med_id = cursor.lastrowid
            
            # Initialize inventory record
            cursor.execute("""
                INSERT INTO medicine_inventory (medicine_id, stock_quantity, low_stock_threshold) 
                VALUES (%s, 0, %s)
            """, (med_id, data['threshold']))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error adding medicine: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def add_stock_purchase(self, data):
        """Records a purchase and updates the current stock quantity."""
        conn = self.db.get_connection()
        if not conn: return False
        
        try:
            cursor = conn.cursor()
            # 1. Record the purchase transaction
            cursor.execute("""
                INSERT INTO purchases (medicine_id, supplier_name, batch_number, quantity, purchase_price, expiry_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (data['medicine_id'], data['supplier'], data['batch'], data['quantity'], data['price'], data['expiry']))
            
            # 2. Update the inventory stock (FIX: Insert if not exists, else Update)
            cursor.execute("""
                INSERT INTO medicine_inventory (medicine_id, stock_quantity, low_stock_threshold) 
                VALUES (%s, %s, 10)
                ON DUPLICATE KEY UPDATE stock_quantity = stock_quantity + %s
            """, (data['medicine_id'], data['quantity'], data['quantity']))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error adding stock: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
            
    def get_medicine_dropdown(self):
        """Fetches medicine list for the restock dropdown."""
        return self.db.execute_query("SELECT medicine_id, name FROM medicines ORDER BY name", fetch=True)

    def delete_medicine(self, medicine_id):
        """Deletes a medicine and its inventory records safely."""
        conn = self.db.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            # Delete child records first to avoid foreign key errors
            cursor.execute("DELETE FROM medicine_inventory WHERE medicine_id = %s", (medicine_id,))
            cursor.execute("DELETE FROM purchases WHERE medicine_id = %s", (medicine_id,))
            # Delete master record
            cursor.execute("DELETE FROM medicines WHERE medicine_id = %s", (medicine_id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error deleting medicine: {e}")
            return False
        finally:
            cursor.close()
            conn.close()