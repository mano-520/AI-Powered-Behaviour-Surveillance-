import time
import os
from twilio.rest import Client

class AlertSystem:
    def __init__(self):
        # The user will need to put their own credentials here
        self.account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "YOUR ACC SID")
        self.auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "AUTH_TOKEN")
        self.from_phone_number = os.environ.get("TWILIO_PHONE_NUMBER", "TWILIO NUMBER")
        self.to_phone_number = os.environ.get("TARGET_PHONE_NUMBER", "MOBILE NUMBER")
        
        self.cooldown_period = 30  # Don't send more than 1 alert every 30 seconds
        self.last_alert_time = 0

    def send_alert(self, message_body="ALERT: Aggressive behavior detected!"):
        current_time = time.time()
        
        # Check cooldown to prevent spamming SMS
        if current_time - self.last_alert_time < self.cooldown_period:
            print("Alert suppressed due to cooldown.")
            return False
            
        print(f"\n[!] ALERT TRIGGERED: {message_body}")
        
        try:
            # Twilio client initialization
            if self.account_sid != "your_account_sid_here":
                client = Client(self.account_sid, self.auth_token)
                message = client.messages.create(
                    body=message_body,
                    from_=self.from_phone_number,
                    to=self.to_phone_number
                )
                print(f"[*] SMS sent successfully. Message SID: {message.sid}")
            else:
                print("[-] Twilio credentials not configured. Setup variables to send actual SMS.")
                
            self.last_alert_time = current_time
            return True
            
        except Exception as e:
            print(f"[-] Failed to send SMS: {e}")
            return False
