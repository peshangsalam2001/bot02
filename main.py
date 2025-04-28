import telebot
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Replace with your actual Telegram Bot Token
BOT_TOKEN = "8072279299:AAHAEodRhWpDb2g7EIVNFc3pk1Yg0YlpaPc"
bot = telebot.TeleBot(BOT_TOKEN)

FIREFLY_SIGNUP_URL = "https://www.fireflyapp.com/signup.php"
FIREFLY_HEADERS = {
    "content-type": "application/x-www-form-urlencoded",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "sec-fetch-mode": "navigate",
    "origin": "https://www.fireflyapp.com",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1",
    "referer": "https://www.fireflyapp.com/signup.php",
    "sec-fetch-dest": "document",
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Please provide the signup details in the following format:\n\nsubdomain|name|email|password|stripeToken")

@bot.message_handler(func=lambda message: len(message.text.split('|')) == 5)
def signup_firefly(message):
    try:
        subdomain, name, email, password, stripe_token = message.text.split('|')

        payload = {
            "subdomain": subdomain,
            "item": "item_1",  # Assuming a default item
            "name": name,
            "email": email,
            "reg_password": password,
            "reg_password_confirmation": password,
            "account_info": "1",
            "company": "",
            "address": "YOUR_ADDRESS",  # You might need to collect this or hardcode a default
            "country": "US",             # Assuming US, adjust if needed
            "state": "NJ",               # Assuming NJ, adjust if needed
            "city": "YOUR_CITY",         # You might need to collect this or hardcode a default
            "zip": "YOUR_ZIP",           # You might need to collect this or hardcode a default
            "phone": "YOUR_PHONE",       # You might need to collect this or hardcode a default
            "pay_type": "card",
            "stripeToken": stripe_token,
            "terms_and_policies": "1",
            "timezoneoffset": "-180",    # Assuming a default offset
            "time_zone": "Asia/Baghdad",  # Assuming a default timezone
            "lang": "en-US",
            "main_page": "677000bf050fed682c237e7b4c7cb9aa", # Assuming a default
            "auth_key": "",
        }

        response = requests.post(FIREFLY_SIGNUP_URL, headers=FIREFLY_HEADERS, data=payload)
        response.raise_for_status()

        if "congratulations" in response.text.lower():
            bot.reply_to(message, "Signup successful!")
        else:
            bot.reply_to(message, f"Signup failed. Response from server:\n{response.text}")

    except requests.exceptions.RequestException as e:
        bot.reply_to(message, f"Error during signup request: {e}")
    except ValueError:
        bot.reply_to(message, "Invalid input format. Please use: subdomain|name|email|password|stripeToken")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        bot.reply_to(message, f"An unexpected error occurred: {e}")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Send /start to begin the Firefly III signup process.")

if __name__ == '__main__':
    logging.info("Bot started...")
    bot.polling(none_stop=True)
