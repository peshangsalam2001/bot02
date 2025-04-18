import telebot
from telebot import types

# توکەنی بۆتەکە
API_TOKEN = '7438009531:AAGgank9ch5ZjphQk20735a3nGwpVQdGF70'
bot = telebot.TeleBot(API_TOKEN)

# کۆرسەکان
courses = [
    {"name": "کۆرسی مایکرۆسۆفت ئێکسڵ", "price": 20},
    {"name": "کۆرسی زمانی پایسۆن", "price": 15},
    {"name": "کۆرسی مایکرۆسۆفت ئەکسس", "price": 10},
    {"name": "کۆرسی مایکرۆسۆفت وۆرد ئاستی سەرەتا", "price": 25},
    {"name": "کۆرسی مایکرۆسۆفت وۆرد ئاستی سەرەتا (بێ کۆین)", "price": 0}
]

# شێوەیەکی تایبەتی دوگمەیەکان
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # پەیامی بەخێرهاتن
    markup = types.ReplyKeyboardMarkup(row_width=2)
    item1 = types.KeyboardButton("کۆرسی مایکرۆسۆفت ئێکسڵ")
    item2 = types.KeyboardButton("کۆرسی زمانی پایسۆن")
    item3 = types.KeyboardButton("کۆرسی مایکرۆسۆفت ئەکسس")
    item4 = types.KeyboardButton("کۆرسی مایکرۆسۆفت وۆرد ئاستی سەرەتا")
    item5 = types.KeyboardButton("کۆرسی مایکرۆسۆفت وۆرد ئاستی سەرەتا (بێ کۆین)")

    markup.add(item1, item2, item3, item4, item5)
    bot.send_message(message.chat.id, "سڵاو! بەخێربێیت بۆ بۆت! پەنجە بە دوگمەی کۆرسەکان بۆ دیاری کردنی کۆرسەکان.", reply_markup=markup)

# تایبەتمەندی کۆرسەکان
@bot.message_handler(func=lambda message: True)
def send_course_link(message):
    course_name = message.text
    if course_name == "کۆرسی مایکرۆسۆفت وۆرد ئاستی سەرەتا (بێ کۆین)":
        # ئەم کۆرسە بێ کۆینە
        bot.send_message(message.chat.id, "پیرۆزە ئەمە کۆرسەکەتە: https://www.youtube.com/watch?v=JZ88S75tqmk&t=1s")
    else:
        bot.send_message(message.chat.id, "کۆرسەکە پێویست بە کۆین.")
  
bot.polling(none_stop=True)
