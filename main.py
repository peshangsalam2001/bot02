import telebot
import re
import random
import string
import time
from datetime import datetime

BOT_TOKEN = "8072279299:AAHSQpNR0d4PuzY5l9kHAqT61-IjWhNjIAI"
bot = telebot.TeleBot(BOT_TOKEN)

def parse_card_input(text):
    # Find card number (13-19 digits, Luhn valid)
    card_match = re.search(r"\b(?:\d[ -]*?){13,19}\b", text)
    if card_match:
        card_number = re.sub(r"\D", "", card_match.group())
        # Simple Luhn check
        if len(card_number) not in [15, 16] or not luhn_valid(card_number):
            return None
    else:
        return None

    # Find expiration (MM/YY, MM/YYYY, MM-YY, etc.)
    exp_match = re.search(r"\b(\d{1,2})[\/\-](\d{2,4})\b", text)
    if exp_match:
        mm = exp_match.group(1).zfill(2)
        yy = exp_match.group(2)
        if len(yy) == 4:
            yy = yy[2:]
        current_year = datetime.now().year % 100
        if not (1 <= int(mm) <= 12) or int(yy) < current_year:
            return None
    else:
        return None

    # Find CVV (3-4 digits)
    cvv_match = re.search(r"(?:cvv|cvc|安全码|驗證碼)[:：]?\s*(\d{3,4})", text, re.IGNORECASE)
    if not cvv_match:
        cvv_match = re.search(r"\b\d{3,4}\b", text.split()[-1])
    if cvv_match:
        cvv = cvv_match.group(1) if cvv_match.groups() else cvv_match.group()
    else:
        return None

    return card_number, mm, yy, cvv

def luhn_valid(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d*2))
    return checksum % 10 == 0

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,
        "💳 Universal Card Checker Bot\n"
        "Send card details in ANY format!\n"
        "Examples:\n"
        "5218531024116809 CVV:983 EXP:07/2029\n"
        "Card: 4242 4242 4242 4242\n"
        "Exp: 12/25 CVC 123"
    )

@bot.message_handler(func=lambda message: True)
def card_handler(message):
    parsed = parse_card_input(message.text)
    if not parsed:
        bot.reply_to(message, "❌ Couldn't extract valid card details")
        return

    cc, mm, yy, cvv = parsed
    # Your card checking logic here
    response = f"✅ Extracted Card:\n{cc}|{mm}|{yy}|{cvv}"
    bot.reply_to(message, response)

if __name__ == "__main__":
    bot.infinity_polling()