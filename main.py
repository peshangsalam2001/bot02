import telebot
import requests

# Initialize global variables
stripe_key = None
bot_token = '8072279299:AAHAEodRhWpDb2g7EIVNFc3pk1Yg0YlpaPc'  # Replace with your actual bot token
bot = telebot.TeleBot(bot_token)

# Track user states
user_states = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Welcome! First, send /setup to configure your Stripe secret key.")

@bot.message_handler(commands=['setup'])
def setup(message):
    bot.send_message(message.chat.id, "Please send me your Stripe secret key.")
    user_states[message.chat.id] = {'step': 'waiting_for_stripe_key'}

@bot.message_handler(commands=['pay'])
def pay(message):
    # Check if stripe_key is set
    global stripe_key
    if not stripe_key:
        bot.reply_to(message, "Please run /setup first to set your Stripe secret key.")
        return
    bot.send_message(message.chat.id,
        "Enter your credit card details in this format:\n"
        "Number, Month, Year, CVC\n"
        "Example:\n4242424242424242, 12, 2024, 123")
    user_states[message.chat.id] = {'step': 'waiting_for_card_details'}

@bot.message_handler(func=lambda msg: msg.chat.id in user_states)
def handle_state(message):
    state = user_states[message.chat.id]
    if state['step'] == 'waiting_for_stripe_key':
        # Save the secret key
        global stripe_key
        stripe_key = message.text.strip()
        user_states[message.chat.id]['step'] = 'ready'
        bot.reply_to(message, "Stripe secret key received! Now send /pay to enter your card details.")
    elif state['step'] == 'waiting_for_card_details':
        # Parse card details
        parts = message.text.split(',')
        if len(parts) != 4:
            bot.reply_to(message, "Invalid format. Please send details as:\nNumber, Month, Year, CVC")
            return
        card_number = parts[0].strip()
        exp_month = parts[1].strip()
        exp_year = parts[2].strip()
        cvc = parts[3].strip()

        # Proceed with payment
        process_payment(message.chat.id, card_number, exp_month, exp_year, cvc)
        del user_states[message.chat.id]
    else:
        bot.reply_to(message, "Unexpected state. Send /setup to start again.")

def process_payment(chat_id, card_number, exp_month, exp_year, cvc):
    email = f"user_{chat_id}@example.com"  # Generate email

    # Create Stripe payment method
    response = requests.post(
        "https://api.stripe.com/v1/payment_methods",
        headers={
            "Authorization": f"Bearer {stripe_key}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "type": "card",
            "billing_details[email]": email,
            "card[number]": card_number,
            "card[cvc]": cvc,
            "card[exp_month]": exp_month,
            "card[exp_year]": exp_year
        }
    )

    resp_json = response.json()
    payment_method_id = resp_json.get('id', '')

    if not payment_method_id:
        bot.send_message(chat_id, f"Failed to create payment method: {resp_json.get('error', resp_json)}")
        return

    bot.send_message(chat_id, f"Payment method created: {payment_method_id}")

    # Proceed with upgrade
    upgrade_response = requests.post(
        "https://www.residenturbanist.com/upgrade?_data=routes%2Fupgrade",
        headers={
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://www.residenturbanist.com",
            "Referer": "https://www.residenturbanist.com/upgrade",
            "User-Agent": "Mozilla/5.0"
        },
        data={
            "email": email,
            "force_three_d_secure": "false",
            "price_id": "c5106d42-b50c-440e-8a4e-fafeb2691893",
            "upgrade_error_message": "Oops, something went wrong.",
            "upgrade_success_message": "You are now a premium subscriber",
            "payment_method": payment_method_id,
            "tax_id": "",
            "tax_id_type": "",
            "amount_cents": "100"
        }
    )

    try:
        json_resp = upgrade_response.json()
        status = json_resp.get('status', '')
        message_text = json_resp.get('message', '')
    except:
        status = ''
        message_text = upgrade_response.text

    if "success" in status.lower():
        bot.send_message(chat_id, f"Upgrade successful: {message_text}")
    elif "error" in status.lower():
        bot.send_message(chat_id, f"Upgrade failed: {message_text}")
    else:
        bot.send_message(chat_id, f"Response: {message_text}")

# Run the bot
bot.polling()