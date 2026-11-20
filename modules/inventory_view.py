import customtkinter as ctk
from tkinter import ttk, messagebox
from services.inventory_service import InventoryService

class InventoryView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.service = InventoryService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # Top Bar
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=20, pady=20)
        
        self.lbl_title = ctk.CTkLabel(self.top_frame, text="Medicine Inventory", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1E3A8A")
        self.lbl_title.pack(side="left")
        
        self.btn_restock = ctk.CTkButton(self.top_frame, text="📦 Add Stock (Purchase)", fg_color="#3B82F6", hover_color="#2563EB", command=self.open_restock_modal)
        self.btn_restock.pack(side="right", padx=(5, 0))
        
        self.btn_add_med = ctk.CTkButton(self.top_frame, text="+ Add New Medicine", fg_color="#10B981", hover_color="#059669", command=self.open_add_medicine_modal)
        self.btn_add_med.pack(side="right", padx=5)
        
        self.entry_search = ctk.CTkEntry(self.top_frame, placeholder_text="Search Medicine...", width=200)
        self.entry_search.pack(side="right", padx=15)
        self.entry_search.bind("<KeyRelease>", self.on_search)

        # Table
        self.table_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="white")
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        style = ttk.Style()
        columns = ("ID", "Medicine Name", "Category", "Unit Price (₹)", "Current Stock", "Status")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
            
        self.tree.column("Medicine Name", width=200)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        # --- Bottom Action Bar ---
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.btn_delete = ctk.CTkButton(self.bottom_frame, text="Delete Medicine", fg_color="#EF4444", hover_color="#DC2626", command=self.delete_medicine)
        self.btn_delete.pack(side="right")

    def load_data(self, search_text=""):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        inventory = self.service.get_inventory_status(search_text)
        if inventory:
            for item in inventory:
                stock = item['stock_quantity']
                thresh = item['threshold']
                
                # Determine stock status
                if stock <= 0:
                    status = "🔴 OUT OF STOCK"
                elif stock <= thresh:
                    status = "🟠 LOW STOCK"
                else:
                    status = "🟢 AVAILABLE"
                    
                self.tree.insert("", "end", values=(
                    item['medicine_id'], item['name'], item['category'], 
                    f"{item['unit_price']:.2f}", stock, status
                ))

    def on_search(self, event):
        self.load_data(self.entry_search.get().strip())

    def open_add_medicine_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Add New Medicine Catalog")
        modal.geometry("450x550")
        modal.grab_set()
        
        ctk.CTkLabel(modal, text="New Medicine Entry", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1E3A8A").pack(pady=15)
        
        def create_input(label_text, placeholder=""):
            ctk.CTkLabel(modal, text=label_text).pack(anchor="w", padx=40)
            entry = ctk.CTkEntry(modal, width=370, placeholder_text=placeholder)
            entry.pack(pady=(0, 10))
            return entry

        name_entry = create_input("Medicine Name (Brand)", "e.g. Dolo 650")
        gen_entry = create_input("Generic Name", "e.g. Paracetamol")
        cat_entry = create_input("Category", "e.g. Tablet, Syrup, Injection")
        mfg_entry = create_input("Manufacturer")
        price_entry = create_input("Selling Price per Unit (₹)", "e.g. 2.50")
        thresh_entry = create_input("Low Stock Alert Threshold", "e.g. 50")
        
        def save():
            try:
                data = {
                    "name": name_entry.get().strip(),
                    "generic_name": gen_entry.get().strip(),
                    "category": cat_entry.get().strip(),
                    "manufacturer": mfg_entry.get().strip(),
                    "unit_price": float(price_entry.get().strip()),
                    "threshold": int(thresh_entry.get().strip() or 10)
                }
                if not data['name'] or data['unit_price'] <= 0:
                    messagebox.showerror("Error", "Valid Name and Price are required.")
                    return
                    
                if self.service.add_new_medicine(data):
                    messagebox.showinfo("Success", "Medicine added to catalog!")
                    self.load_data()
                    modal.destroy()
                else:
                    messagebox.showerror("Error", "Could not add medicine. Name might already exist.")
            except ValueError:
                messagebox.showerror("Format Error", "Price and Threshold must be valid numbers.")

        ctk.CTkButton(modal, text="Save Medicine", width=370, command=save).pack(pady=15)

    def open_restock_modal(self):
        meds = self.service.get_medicine_dropdown()
        if not meds:
            messagebox.showinfo("Notice", "Catalog is empty. Add a new medicine first.")
            return
            
        modal = ctk.CTkToplevel(self)
        modal.title("Purchase / Restock Medicine")
        modal.geometry("450x550")
        modal.grab_set()
        
        ctk.CTkLabel(modal, text="Restock Inventory", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1E3A8A").pack(pady=15)
        
        med_list = [f"{m['medicine_id']} - {m['name']}" for m in meds]
        ctk.CTkLabel(modal, text="Select Medicine").pack(anchor="w", padx=40)
        med_dd = ctk.CTkOptionMenu(modal, values=med_list, width=370)
        med_dd.pack(pady=(0, 10))
        
        def create_input(label_text, placeholder=""):
            ctk.CTkLabel(modal, text=label_text).pack(anchor="w", padx=40)
            entry = ctk.CTkEntry(modal, width=370, placeholder_text=placeholder)
            entry.pack(pady=(0, 10))
            return entry
            
        qty_entry = create_input("Quantity Added", "e.g. 500")
        price_entry = create_input("Total Purchase Cost (₹)", "e.g. 1500")
        batch_entry = create_input("Batch Number", "e.g. BATCH-A01")
        expiry_entry = create_input("Expiry Date (YYYY-MM-DD)", "e.g. 2028-12-31")
        supplier_entry = create_input("Supplier Name")
        
        def save_stock():
            try:
                med_id = int(med_dd.get().split(" - ")[0])
                data = {
                    "medicine_id": med_id,
                    "quantity": int(qty_entry.get().strip()),
                    "price": float(price_entry.get().strip()),
                    "batch": batch_entry.get().strip() or "UNKNOWN",
                    "expiry": expiry_entry.get().strip(),
                    "supplier": supplier_entry.get().strip()
                }
                
                if not data['expiry'] or data['quantity'] <= 0:
                    messagebox.showerror("Error", "Valid Quantity and Expiry Date are required.")
                    return
                    
                if self.service.add_stock_purchase(data):
                    messagebox.showinfo("Success", "Stock updated successfully!")
                    self.load_data()
                    modal.destroy()
                else:
                    messagebox.showerror("Error", "Failed to update stock.")
                    
            except ValueError:
                messagebox.showerror("Format Error", "Quantity and Price must be valid numbers.")

        ctk.CTkButton(modal, text="Update Stock", width=370, fg_color="#F59E0B", hover_color="#D97706", command=save_stock).pack(pady=15)

    def delete_medicine(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a medicine from the table to delete.")
            return
            
        item = self.tree.item(selected[0])
        med_id = item['values'][0]
        med_name = item['values'][1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{med_name}'?\nThis will also remove its stock history."):
            if self.service.delete_medicine(med_id):
                self.load_data()
                messagebox.showinfo("Success", "Medicine deleted successfully.")
            else:
                messagebox.showerror("Error", "Could not delete medicine. It might be linked to old prescriptions.")    