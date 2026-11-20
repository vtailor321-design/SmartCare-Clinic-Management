import pywhatkit
import threading
import re

class WhatsAppService:
    @staticmethod
    def clean_phone(phone):
        """Sirf digits nikal kar last 10 digits ke aage +91 lagayega."""
        digits = re.sub(r'\D', '', str(phone))  # Spaces, '-', '+' sab hata dega
        if len(digits) >= 10:
            return "+91" + digits[-10:]
        return "+91" + digits

    @staticmethod
    def send_message(phone, message):
        """Sends WhatsApp message reliably without closing the tab too early."""
        def send():
            formatted_phone = WhatsAppService.clean_phone(phone)
            
            try:
                print(f"Opening WhatsApp for {formatted_phone}...")
                pywhatkit.sendwhatmsg_instantly(
                    phone_no=formatted_phone, 
                    message=message, 
                    wait_time=25,      # WhatsApp load hone ke liye enough time
                    tab_close=False    # Tab khud band nahi hoga, message pakka jayega
                )
                print("WhatsApp message sent successfully!")
            except Exception as e:
                print(f"WhatsApp Error: {e}")

        thread = threading.Thread(target=send, daemon=True)
        thread.start()