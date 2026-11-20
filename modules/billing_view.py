import customtkinter as ctk
from tkinter import ttk, messagebox
from services.billing_service import BillingService
from utils.pdf_generator import generate_invoice_pdf
import os
from services.whatsapp_service import WhatsAppService

class BillingView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.service = BillingService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=20, pady=20)
        
        self.lbl_title = ctk.CTkLabel(self.top_frame, text="Billing & Payments", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1E3A8A")
        self.lbl_title.pack(side="left")
        
        self.btn_add = ctk.CTkButton(self.top_frame, text="+ Generate New Bill", fg_color="#10B981", hover_color="#059669", command=self.open_generate_bill_modal)
        self.btn_add.pack(side="right")
        
        self.entry_search = ctk.CTkEntry(self.top_frame, placeholder_text="Search Patient Name/Bill ID...", width=250)
        self.entry_search.pack(side="right", padx=15)
        self.entry_search.bind("<KeyRelease>", self.on_search)

        # Table
        self.table_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="white")
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        style = ttk.Style()
        columns = ("Bill ID", "Patient Name", "Appt Date", "Net Payable (₹)", "Status")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
            
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Bottom Actions
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.btn_print = ctk.CTkButton(self.bottom_frame, text="Print Invoice PDF", fg_color="#3B82F6", hover_color="#2563EB", command=self.print_invoice)
        self.btn_print.pack(side="right", padx=5)
        
        self.btn_pay = ctk.CTkButton(self.bottom_frame, text="Make Payment", fg_color="#F59E0B", hover_color="#D97706", command=self.open_payment_modal)
        self.btn_pay.pack(side="right", padx=5)

    def load_data(self, search_text=""):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        bills = self.service.get_all_bills(search_text)
        if bills:
            for b in bills:
                self.tree.insert("", "end", values=(b['bill_id'], b['patient_name'], b['appointment_date'], b['net_amount'], b['status']))

    def on_search(self, event):
        self.load_data(self.entry_search.get().strip())

    def open_generate_bill_modal(self):
        unbilled = self.service.get_unbilled_appointments()
        if not unbilled:
            messagebox.showinfo("Notice", "No completed appointments pending for billing.")
            return

        modal = ctk.CTkToplevel(self)
        modal.title("Generate Bill")
        modal.geometry("500x600")
        modal.grab_set()
        
        ctk.CTkLabel(modal, text="Create Invoice", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1E3A8A").pack(pady=15)
        
        # Select Appointment
        appt_list = [f"{a['appointment_id']} - {a['full_name']} ({a['appointment_date']})" for a in unbilled]
        
        ctk.CTkLabel(modal, text="Select Completed Appointment").pack(anchor="w", padx=30)
        appt_dd = ctk.CTkOptionMenu(modal, values=appt_list, width=440)
        appt_dd.pack(pady=(0, 15))
        
        # Items Entry
        items_frame = ctk.CTkFrame(modal, fg_color="transparent")
        items_frame.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(items_frame, text="Item Description", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(items_frame, text="Amount (₹)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, sticky="w", padx=10)
        
        desc1 = ctk.CTkEntry(items_frame, width=280)
        desc1.grid(row=1, column=0, pady=5)
        desc1.insert(0, "Doctor Consultation Fee") # Default text
        
        amt1 = ctk.CTkEntry(items_frame, width=150)
        amt1.grid(row=1, column=1, padx=10, pady=5)
        
        desc2 = ctk.CTkEntry(items_frame, width=280, placeholder_text="e.g. Pharmacy/Medicines")
        desc2.grid(row=2, column=0, pady=5)
        amt2 = ctk.CTkEntry(items_frame, width=150, placeholder_text="0")
        amt2.grid(row=2, column=1, padx=10, pady=5)
        
        ctk.CTkLabel(modal, text="Discount Applied (₹)").pack(anchor="w", padx=30, pady=(10,0))
        discount_entry = ctk.CTkEntry(modal, width=440, placeholder_text="0")
        discount_entry.pack(pady=5)
        
        def process_bill():
            try:
                # Find matching appointment data
                selected_str = appt_dd.get()
                appt_id = int(selected_str.split(" - ")[0])
                patient_id = next((a['patient_id'] for a in unbilled if a['appointment_id'] == appt_id), None)
                
                d1, a1 = desc1.get().strip(), amt1.get().strip()
                d2, a2 = desc2.get().strip(), amt2.get().strip()
                
                if not d1 or not a1:
                    messagebox.showerror("Validation", "At least one item (Consultation) is required.")
                    return
                    
                items = [{"desc": d1, "amount": float(a1)}]
                if d2 and a2: items.append({"desc": d2, "amount": float(a2)})
                
                total = sum(i['amount'] for i in items)
                discount = float(discount_entry.get().strip() or 0)
                
                data = {
                    "patient_id": patient_id,
                    "appointment_id": appt_id,
                    "items": items,
                    "total_amount": total,
                    "discount": discount,
                    "net_amount": total - discount
                }
                
                if self.service.create_bill(data):
                    messagebox.showinfo("Success", "Bill Generated Successfully!")
                    self.load_data()
                    modal.destroy()
                else:
                    messagebox.showerror("Error", "Could not generate bill.")
                    
            except ValueError:
                messagebox.showerror("Format Error", "Please enter valid numeric amounts.")
        ctk.CTkButton(modal, text="Generate Bill", width=440, height=40, font=ctk.CTkFont(weight="bold"), command=process_bill).pack(pady=20)


    def open_payment_modal(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a Bill first.")
            return
            
        item = self.tree.item(selected[0])
        bill_id = item['values'][0]
        status = item['values'][4]
        
        if status == 'Paid':
            messagebox.showinfo("Notice", "This bill is already fully paid.")
            return
            
        modal = ctk.CTkToplevel(self)
        modal.title("Receive Payment")
        modal.geometry("350x400")
        modal.grab_set()
        
        ctk.CTkLabel(modal, text=f"Pay for Bill #{bill_id}", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        
        ctk.CTkLabel(modal, text="Amount Received (₹)").pack(anchor="w", padx=40)
        amount_entry = ctk.CTkEntry(modal, width=270)
        amount_entry.pack(pady=5)
        
        ctk.CTkLabel(modal, text="Payment Method").pack(anchor="w", padx=40, pady=(15,0))
        method_dd = ctk.CTkOptionMenu(modal, values=["Cash", "UPI", "Card", "Bank Transfer"], width=270)
        method_dd.pack(pady=5)
        
        def save_payment():
            try:
                amt = float(amount_entry.get().strip())
                if self.service.add_payment(bill_id, amt, method_dd.get()):
                    messagebox.showinfo("Success", "Payment Recorded!")
                    self.load_data()
                    
                    # --- NAYA LOGIC: Auto PDF & WhatsApp on Payment ---
                    data = self.service.get_bill_pdf_data(bill_id)
                    if data:
                        # 1. Background me Invoice PDF banayega
                        filename = f"Invoice_BILL{bill_id}_{data['full_name'].replace(' ', '_')}.pdf"
                        path = generate_invoice_pdf(data, filename)
                        
                        # 2. Exports folder khol dega (Drag & Drop ke liye)
                        import os
                        os.startfile(os.path.abspath("exports"))
                        
                        # 3. Patient ko Confirmation Text Bhejna
                        try:
                            # DB se patient ka asli number nikal rahe hain
                            phone = data['phone'] 
                            
                            msg = f"🏥 *SmartCare Clinic*\n\nHello {data['full_name']},\n"
                            msg += f"We have received your payment of Rs. {amt} via {method_dd.get()}.\n\n"
                            msg += f"🧾 *Bill ID:* {bill_id}\n"
                            msg += f"💰 *Total Paid:* Rs. {data['total_paid']:.2f}\n\n"
                            msg += "Please find your detailed PDF Invoice attached with this message. Wish you a speedy recovery!"
                            
                            from services.whatsapp_service import WhatsAppService
                            WhatsAppService.send_message(phone, msg)
                        except Exception as e:
                            print(f"WhatsApp Error: {e}")
                    # --------------------------------------------------
                    
                    modal.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid Amount.")
        ctk.CTkButton(modal, text="Save Payment", width=250, height=40, font=ctk.CTkFont(weight="bold"), fg_color="#10B981", hover_color="#059669", command=save_payment).pack(pady=30)
    def print_invoice(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a Bill to print.")
            return
            
        bill_id = self.tree.item(selected[0])['values'][0]
        data = self.service.get_bill_pdf_data(bill_id)
        
        if data:
            filename = f"Invoice_BILL{bill_id}_{data['full_name'].replace(' ', '_')}.pdf"
            path = generate_invoice_pdf(data, filename)
            os.startfile(os.path.abspath(path))