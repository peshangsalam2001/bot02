
import requests

BOT_TOKEN = '8072279299:AAH0SaBdoqFOIP-qukCCfvCD7LkqefKlu9Q'
stripe_publishable_key = 'pk_live_51IksXdLsdufqQtEPrF9bXcJSrESLkgnbnfldl87Y1B20yq8lVkogGvYx5jpEduPg2CDuQ1E15IQzaaIRExFp0xkL001gqjnUZQ'

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Send /bulk to check multiple cards at once.\nFormat:\nNumber,Month,Year,CVC\nOne card per line.")

@bot.message_handler(commands=['bulk'])
def handle_bulk(message):
    bot.send_message(message.chat.id, "Please send your cards, one per line, in the format:\nNumber, Month, Year, CVC")
    bot.register_next_step_handler(message, process_multiple_cards)

def process_multiple_cards(message):
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
        result = check_card(card_number, exp_month, exp_year, cvc)
        results.append(f"Card {card_number}: {result}")
    bot.send_message(message.chat.id, "\n".join(results))

def check_card(card_number, exp_month, exp_year, cvc):
    # Create Stripe token
    resp = requests.post(
        'https://api.stripe.com/v1/tokens',
        headers={
            'Authorization': f'Bearer {stripe_publishable_key}',
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
        return f"Error: {resp_json['error'].get('message', 'Unknown error')}"
    token_id = resp_json.get('id')
    if not token_id:
        return "Failed to get token"
    # Here, you can proceed to check the token against your website API
    # For demonstration, we'll just return success
    return "Token generated successfully"

bot.polling()