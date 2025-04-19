import telebot
from telebot import types

TOKEN = '7438009531:AAGgank9ch5ZjphQk20735a3nGwpVQdGF70'
BOT_USERNAME = 'Bot02PA_Bot'

bot = telebot.TeleBot(TOKEN)

user_coins = {}
invited_users = set()

# نرخەکانی کۆرسەکان
courses_data = {
    "کۆرسی مایکرۆسۆفت ئێکسڵ": 20,
    "کۆرسی زمانی پایسۆن": 15,
    "کۆرسی مایکرۆسۆفت ئەکسس": 10
}

# فۆنکشنی نامەی پێشواز
def send_welcome_message(chat_id, user_id, first_name):
    photo_url = 'https://imgur.com/a/2EDWQ0H'
    caption = f"""سڵاو بەڕێز {first_name}، بەخێربێیت بۆ بۆتی ئەکادیمیای پێشەنگ.
ئەم بۆتە تایبەتە بە کۆمەڵێک خزمەتگوزاری و زانیاری، هەر یەکە لە کڕینی کۆرس، زانینی کۆینەکانت، زانیاری تەکنەلۆجی و زۆر شتی تر.

بۆ هەر یەکێک لەو تایبەتمەندیانە پەنجە بە دوگمەی مەبەست بنێ:
"""

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("کۆینەکانم", callback_data='my_coins'),
        types.InlineKeyboardButton("لینکی بانگهێشتنامە", callback_data='invite_link'),
        types.InlineKeyboardButton("کۆرسەکان", callback_data='courses'),
        types.InlineKeyboardButton("هەموو بۆتەکانم", callback_data='all_bots')
    )

    bot.send_photo(chat_id, photo_url, caption=caption, reply_markup=markup)

# فرمانی /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    args = message.text.split()

    if user_id not in user_coins:
        user_coins[user_id] = 0

    if len(args) > 1:
        inviter_id = args[1]
        if inviter_id != str(user_id):
            key = f"{inviter_id}_{user_id}"
            if key not in invited_users:
                invited_users.add(key)
                user_coins[int(inviter_id)] = user_coins.get(int(inviter_id), 0) + 1
                bot.send_message(int(inviter_id), f"کەسێک بە بانگەوازت هاتە ناو بۆتەکە. 1 کۆینت زیاد کرا.")

    send_welcome_message(message.chat.id, user_id, first_name)

# هەڵگرتنی دوگمەکان
@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    user_id = call.from_user.id
    first_name = call.from_user.first_name

    def add_back_button():
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("گەڕانەوە", callback_data='back'))
        return markup

    if call.data == 'my_coins':
        coins = user_coins.get(user_id, 0)
        text = f"بەڕێز {first_name}، ئەم کۆینە بۆ مەبەستی کڕینی کۆرسەکان بەکاردێت.\nتۆ ئێستا {coins} کۆینت هەیە."
        bot.send_message(call.message.chat.id, text, reply_markup=add_back_button())

    elif call.data == 'invite_link':
        link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
        bot.send_message(call.message.chat.id, f"ئەمە لینکی بانگهێشتنامەکەتە:\n{link}", reply_markup=add_back_button())

    elif call.data == 'courses':
        markup = types.InlineKeyboardMarkup()
        for course, price in courses_data.items():
            markup.add(types.InlineKeyboardButton(f"{course} - {price} کۆین", callback_data=f"buy_{course}"))
        markup.add(types.InlineKeyboardButton("گەڕانەوە", callback_data='back'))
        bot.send_message(call.message.chat.id, "کۆرسە بەردەستەکان:", reply_markup=markup)

    elif call.data.startswith('buy_'):
        course_name = call.data[4:]
        course_price = courses_data.get(course_name, 0)
        coins = user_coins.get(user_id, 0)

        if coins >= course_price:
            user_coins[user_id] -= course_price
            bot.send_message(call.message.chat.id,
                             f"کۆرسی {course_name} بە سەرکەوتوویی کڕدرایە ✅\nکۆینی ماوەتەوە: {user_coins[user_id]}",
                             reply_markup=add_back_button())
        else:
            bot.send_message(call.message.chat.id,
                             f"ببوورە، تۆ {course_price} کۆین پێویستە بۆ کڕینی کۆرسی {course_name}، بەڵام تەنها {coins} کۆینت هەیە.",
                             reply_markup=add_back_button())

    elif call.data == 'all_bots':
        bot.send_message(call.message.chat.id, "ئەمە بۆتە تایبەتی ئەکادیمیای پێشەنگە:\n@PeshangTestBot", reply_markup=add_back_button())

    elif call.data == 'back':
        send_welcome_message(call.message.chat.id, user_id, first_name)

bot.polling()