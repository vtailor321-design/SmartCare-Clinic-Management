from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
from datetime import datetime

def generate_prescription_pdf(data, filename):
    """Generates a professional PDF prescription."""
    # Ensure directory exists
    os.makedirs("exports", exist_ok=True)
    filepath = os.path.join("exports", filename)
    
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    
    # --- Header (Clinic Info) ---
    c.setFont("Helvetica-Bold", 24)
    c.setFillColorRGB(0.12, 0.23, 0.54) # #1E3A8A Dark Blue
    c.drawString(50, height - 50, "SmartCare Clinic")
    
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(50, height - 65, "123 Health Avenue, Medical District")
    c.drawString(50, height - 77, "Phone: +91 9876543210 | Email: care@smartcare.com")
    
    # Line separator
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.line(50, height - 90, width - 50, height - 90)
    
    # --- Doctor & Date Info ---
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(50, height - 115, f"Dr. {data['doctor_name']}")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 130, f"{data['specialization']} | {data['qualification']}")
    
    c.drawString(width - 150, height - 115, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    c.drawString(width - 150, height - 130, f"Token No: {data['token_number']}")
    
    # --- Patient Info ---
    c.setFillColorRGB(0.95, 0.95, 0.95)
    c.rect(50, height - 190, width - 100, 40, fill=1, stroke=0)
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, height - 170, f"Patient Name: {data['patient_name']}")
    c.setFont("Helvetica", 10)
    c.drawString(60, height - 182, f"Age/DOB: {data['dob']} | Gender: {data['gender']}")
    
    # --- Diagnosis ---
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 230, "Diagnosis:")
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 250, data['diagnosis'])
    
    # --- Rx (Medicines) ---
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 300, "Rx")
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(80, height - 330, "Medicine Name")
    c.drawString(300, height - 330, "Dosage")
    c.drawString(450, height - 330, "Duration")
    
    c.line(50, height - 335, width - 50, height - 335)
    
    c.setFont("Helvetica", 11)
    y_pos = height - 355
    for med in data['medicines']:
        c.drawString(80, y_pos, med['name'])
        c.drawString(300, y_pos, med['dosage'])
        c.drawString(450, y_pos, med['duration'])
        y_pos -= 20
        
    # --- Instructions & Follow-up ---
    y_pos -= 20
    if data['instructions']:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y_pos, "Instructions:")
        c.setFont("Helvetica", 11)
        c.drawString(50, y_pos - 15, data['instructions'])
        y_pos -= 45
        
    if data['follow_up']:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y_pos, f"Next Follow-up Date: {data['follow_up']}")

    # --- Footer Signature ---
    c.line(width - 200, 100, width - 50, 100)
    c.setFont("Helvetica", 10)
    c.drawString(width - 180, 85, "Doctor's Signature")
    
    c.save()
    return filepath


def generate_invoice_pdf(data, filename):
    """Generates a professional PDF Invoice."""
    os.makedirs("exports", exist_ok=True)
    filepath = os.path.join("exports", filename)
    
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    
    # --- Header (Clinic Info) ---
    c.setFont("Helvetica-Bold", 24)
    c.setFillColorRGB(0.12, 0.23, 0.54)
    c.drawString(50, height - 50, "SmartCare Clinic")
    
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(50, height - 65, "123 Health Avenue, Medical District")
    c.drawString(50, height - 77, "Phone: +91 9876543210 | Email: care@smartcare.com")
    
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.line(50, height - 90, width - 50, height - 90)
    
    # --- Invoice Details ---
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 120, "INVOICE / RECEIPT")
    
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 145, f"Invoice No: BILL-{data['bill_id']}")
    c.drawString(50, height - 160, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    c.drawString(50, height - 175, f"Status: {data['status']}")
    
    c.drawString(width - 250, height - 145, f"Patient Name: {data['full_name']}")
    c.drawString(width - 250, height - 160, f"Phone: {data['phone']}")
    
    # --- Table Header ---
    y_pos = height - 210
    c.setFillColorRGB(0.9, 0.9, 0.9)
    c.rect(50, y_pos, width - 100, 25, fill=1, stroke=0)
    
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, y_pos + 8, "Item Description")
    c.drawString(width - 150, y_pos + 8, "Amount (Rs.)")
    
    # --- Table Items ---
    y_pos -= 25
    c.setFont("Helvetica", 11)
    for item in data['items']:
        c.drawString(60, y_pos, item['item_description'])
        c.drawString(width - 150, y_pos, f"{item['amount']:.2f}")
        y_pos -= 20
        
    c.line(50, y_pos, width - 50, y_pos)
    
    # --- Totals ---
    y_pos -= 25
    c.setFont("Helvetica", 11)
    c.drawString(width - 250, y_pos, "Gross Total:")
    c.drawString(width - 150, y_pos, f"{data['total_amount']:.2f}")
    
    y_pos -= 20
    c.drawString(width - 250, y_pos, "Discount:")
    c.drawString(width - 150, y_pos, f"- {data['discount']:.2f}")
    
    y_pos -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width - 250, y_pos, "Net Payable:")
    c.drawString(width - 150, y_pos, f"{data['net_amount']:.2f}")
    
    y_pos -= 25
    c.setFont("Helvetica", 11)
    c.drawString(width - 250, y_pos, "Total Paid:")
    c.drawString(width - 150, y_pos, f"{float(data['total_paid']):.2f}")
    
    c.save()
    return filepath