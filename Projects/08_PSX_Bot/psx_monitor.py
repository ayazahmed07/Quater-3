# psx_monitor.py
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
import schedule
import time
from config import ACCOUNT_SID, AUTH_TOKEN, FROM_WHATSAPP_NUMBER, TO_WHATSAPP_NUMBER, PSX_URL

client = Client(ACCOUNT_SID, AUTH_TOKEN)
last_notice_title = None

def send_whatsapp_message(body, media_url=None):
    message_data = {
        'from_': FROM_WHATSAPP_NUMBER,
        'to': TO_WHATSAPP_NUMBER,
        'body': body,
    }
    if media_url:
        message_data['media_url'] = [media_url]
    
    message = client.messages.create(**message_data)
    print(f"WhatsApp message sent: {message.sid}")

def check_psx_announcements():
    global last_notice_title
    try:
        response = requests.get(PSX_URL)
        soup = BeautifulSoup(response.text, 'html.parser')

        first_announcement = soup.find('div', class_='announcement-card')

        if first_announcement:
            title = first_announcement.find('h6').get_text(strip=True)
            date = first_announcement.find('span', class_='announcement-date').get_text(strip=True)
            link = first_announcement.find('a')['href']

            full_link = "https://dps.psx.com.pk" + link

            # Assuming the full_link will redirect to a PDF download page
            if title != last_notice_title:
                last_notice_title = title
                body = f"📢 New PSX Announcement:\n\n📝 {title}\n📅 Date: {date}\n🔗 Link: {full_link}"
                
                # Send both text and pdf file
                send_whatsapp_message(body, media_url=full_link)
            else:
                print("No new announcement found.")
        else:
            print("No announcements found on the page.")

    except Exception as e:
        print(f"Error checking announcements: {e}")

def main():
    print("📈 PSX Announcement Monitor started...")
    check_psx_announcements()
    schedule.every(5).minutes.do(check_psx_announcements)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
