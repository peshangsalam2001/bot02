import telebot
import requests

# Your Telegram bot token
BOT_TOKEN = '8072279299:AAH0SaBdoqFOIP-qukCCfvCD7LkqefKlu9Q'
bot = telebot.TeleBot(BOT_TOKEN)

# Function to make a request to the Stripe API
def make_payment_request(email, card_number, card_cvc, exp_month, exp_year, postal_code):
    payment_method_url = "https://api.stripe.com/v1/payment_methods"
    
    payload = {
        "type": "card",
        "billing_details[email]": email,
        "billing_details[address][postal_code]": postal_code,
        "card[number]": card_number,
        "card[cvc]": card_cvc,
        "card[exp_month]": exp_month,
        "card[exp_year]": exp_year,
        "key": "pk_live_51IekcQKHPFAlBzyyGNBguT5BEI7NEBqrTxJhsYN1FI1lQb9iWxU5U2OXfi744NEMx5p7EDXh08YXrudrZkkG9bGc00ZCrkXrxL"  # Replace with your actual public key
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.post(payment_method_url, data=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()["id"]
    else:
        return None

# Function to upgrade the subscription
def upgrade_subscription(email, payment_method_id):
    upgrade_url = "https://onedtech.philhillaa.com/upgrade?_data=routes%2Fupgrade"
    
    # Prepare the payload with the payment method ID
    payload = {
        "email": email,
        "force_three_d_secure": "false",
        "price_id": "667c8b20-9c72-4dc4-ad7b-988e543540db",
        "premium_offer_id": "136d8db6-f95f-42c5-bc6c-8fa6f824ef5b",
        "payment_method": payment_method_id,  # Use the pm_ value from the first URL response
        "amount_cents": 100
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0"
    }
    
    response = requests.post(upgrade_url, data=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "Welcome! Please send your card details in one of the following formats: "
                          "`card_number|exp_month|exp_year|card_cvc` (e.g., `4147098797621083|10|28|202` or `4147098797621083|10|2028|202`).")

@bot.message_handler(func=lambda message: True)
def get_card_details(message):
    try:
        # Split the message text to get card details
        card_details = message.text.split('|')
        if len(card_details) != 4:
            raise ValueError("Please provide all four details in the correct format.")

        card_number = card_details[0].strip()
        exp_month = card_details[1].strip()
        exp_year = card_details[2].strip()
        card_cvc = card_details[3].strip()

        email = "peshangsalam2001@gmail.com"  # Use specified email
        postal_code = "10080"  # Use specified postal code

        # Make payment request
        payment_method_id = make_payment_request(email, card_number, card_cvc, exp_month, exp_year, postal_code)

        if payment_method_id:
            # Upgrade subscription using the newly created payment method ID
            upgrade_response = upgrade_subscription(email, payment_method_id)
            if upgrade_response:
                message_response = upgrade_response.get('toast', {}).get('message', 'Unknown error')
                bot.reply_to(message, message_response)
            else:
                bot.reply_to(message, "Failed to upgrade subscription.")
        else:
            bot.reply_to(message, "Failed to create payment method.")
    
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")

# Start polling
bot.polling()