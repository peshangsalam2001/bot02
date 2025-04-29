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
    bot.reply_to(message, "Welcome! Please provide your card details to upgrade your subscription.")

@bot.message_handler(commands=['upgrade'])
def upgrade_command(message):
    bot.reply_to(message, "Please send your card number.")

    @bot.message_handler(func=lambda m: True)
    def get_card_number(msg):
        card_number = msg.text
        bot.reply_to(msg, "Please send your card CVC.")
        
        @bot.message_handler(func=lambda m: True)
        def get_card_cvc(msg):
            card_cvc = msg.text
            bot.reply_to(msg, "Please send the card's expiration month (MM).")
            
            @bot.message_handler(func=lambda m: True)
            def get_exp_month(msg):
                exp_month = msg.text
                bot.reply_to(msg, "Please send the card's expiration year (YY).")
                
                @bot.message_handler(func=lambda m: True)
                def get_exp_year(msg):
                    exp_year = msg.text
                    bot.reply_to(msg, "Please send the card's postal code.")
                    
                    @bot.message_handler(func=lambda m: True)
                    def get_postal_code(msg):
                        postal_code = msg.text
                        email = "peshangsalam2001@gmail.com"  # Use specified email

                        # Make payment request
                        payment_method_id = make_payment_request(email, card_number, card_cvc, exp_month, exp_year, postal_code)

                        if payment_method_id:
                            # Upgrade subscription
                            upgrade_response = upgrade_subscription(email, payment_method_id)
                            if upgrade_response:
                                message_response = upgrade_response.get('toast', {}).get('message', 'Unknown error')
                                bot.reply_to(msg, message_response)
                            else:
                                bot.reply_to(msg, "Failed to upgrade subscription.")
                        else:
                            bot.reply_to(msg, "Failed to create payment method.")

                    bot.register_next_step_handler(msg, get_postal_code)

                bot.register_next_step_handler(msg, get_exp_year)

            bot.register_next_step_handler(msg, get_exp_month)

        bot.register_next_step_handler(msg, get_card_cvc)

    bot.register_next_step_handler(message, get_card_number)

# Start polling
bot.polling()