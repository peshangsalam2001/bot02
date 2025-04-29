import telebot
import requests

BOT_TOKEN = '8072279299:AAHAEodRhWpDb2g7EIVNFc3pk1Yg0YlpaPc'
bot = telebot.TeleBot(BOT_TOKEN)

user_states = {}
stripe_public_key = None

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Welcome! First, send /setup to configure your Stripe public key.")

@bot.message_handler(commands=['setup'])
def setup(message):
    bot.send_message(message.chat.id, "Please send me your Stripe public key (e.g., pk_live_... or pk_test_...).")
    user_states[message.chat.id] = {'step': 'waiting_for_pubkey'}

@bot.message_handler(commands=['pay'])
def pay(message):
    global stripe_public_key
    if not stripe_public_key:
        bot.reply_to(message, "Please run /setup first to set your Stripe public key.")
        return
    bot.send_message(message.chat.id,
        "Enter your card details in this format:\n"
        "Number, Month, Year, CVC\n"
        "Example:\n4242424242424242, 12, 2024, 123")
    user_states[message.chat.id] = {'step': 'waiting_for_card'}

@bot.message_handler(func=lambda msg: msg.chat.id in user_states)
def handle_state(message):
    state = user_states[message.chat.id]
    if state['step'] == 'waiting_for_pubkey':
        global stripe_public_key
        stripe_public_key = message.text.strip()
        user_states[message.chat.id]['step'] = 'ready'
        bot.reply_to(message, "Stripe public key saved! Now send /pay to enter your card details.")
    elif state['step'] == 'waiting_for_card':
        parts = message.text.split(',')
        if len(parts) != 4:
            bot.reply_to(message, "Invalid format. Send details as:\nNumber, Month, Year, CVC")
            return
        card_number = parts[0].strip()
        exp_month = parts[1].strip()
        exp_year = parts[2].strip()
        cvc = parts[3].strip()
        create_stripe_token_and_signup(message.chat.id, card_number, exp_month, exp_year, cvc)
        del user_states[message.chat.id]
    else:
        bot.reply_to(message, "Unexpected state. Send /setup to restart.")

def create_stripe_token_and_signup(chat_id, card_number, exp_month, exp_year, cvc):
    resp = requests.post(
        'https://api.stripe.com/v1/tokens',
        headers={
            'Authorization': f'Bearer {stripe_public_key}',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        data={
            'card[number]': card_number,
            'card[exp_month]': exp_month,
            'card[exp_year]': exp_year,
            'card[cvc]': cvc
        }
    )
    resp_json = resp.json()
    if 'error' in resp_json:
        error_msg = resp_json['error'].get('message', 'Unknown Stripe error')
        bot.send_message(chat_id, f"Stripe error: {error_msg}")
        return
    token_id = resp_json.get('id')
    if not token_id:
        bot.send_message(chat_id, "Failed to generate Stripe token.")
        return
    signup_response = requests.post(
        'https://www.fireflyapp.com/signup.php',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        },
        data={
            'subdomain': 'peshangsalam2001',
            'item': 'item_1',
            'name': 'Peshang Salam',
            'email': 'peshangsalam2001@gmail.com',
            'reg_password': 'War112233$%',
            'reg_password_confirmation': 'War112233$%',
            'account_info': '1',
            'company': '',
            'address': '198 White Horse Pike',
            'country': 'US',
            'state': 'NJ',
            'city': '3144740104',
            'zip': '08107',
            'phone': '3144740104',
            'pay_type': 'card',
            'stripeToken': token_id,
            'terms_and_policies': '1',
            'timezoneoffset': '-180',
            'time_zone': 'Asia/Baghdad',
            'lang': 'en-US',
            'main_page': '677000bf050fed682c237e7b4c7cb9aa',
            'auth_key': ''
        }
    )
    full_response_text = signup_response.text
    bot.send_message(chat_id, full_response_text)

bot.polling()