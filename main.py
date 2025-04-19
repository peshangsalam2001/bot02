import telebot
from telebot import types

TOKEN = "7438009531:AAGgank9ch5ZjphQk20735a3nGwpVQdGF70"
bot = telebot.TeleBot(TOKEN)

# database
user_data = {}  # Stores coin count
referrals = {}  # Tracks who referred whom

welcome_image = 'https://telegra.ph/file/ae508eaaf738ddc6206b7.jpg'  # Change to your own

courses = {
    "کۆرسی مایکرۆسۆفت ئێکسڵ": {"coins": 30, "link": "https://t.me/AboutMasterLord"},
    "کۆرسی زمانی پایسۆن": {"coins": 20, "link": "https://t.me/AboutMasterLord"},
    "کۆرسی مایکرۆسۆفت ئەکسس": {"coins": 10, "link": "https://t.me/AboutMasterLord"},
}

def get_main_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("کۆرسەکان", callback_data="courses"),
        types.InlineKeyboardButton("کۆینەکانم", callback_data="mycoins"),
    )
    keyboard.add(
        types.InlineKeyboardButton("لینکی بانگهێشتنامە", callback_data="referral"),
        types.InlineKeyboardButton("هەموو بۆتەکانم", callback_data="bots"),
    )
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    ref_id = None

    # Detect referral
    if len(message.text.split()) > 1:
        ref_id = int(message.text.split()[1])
        if ref_id != user_id and user_id not in user_data:
            user_data[ref_id] = user_data.get(ref_id, 0) + 1
            bot.send_message(ref_id, f"🏅 کەسێک بە بەکارهێنانی لینکی بانگهێشتت بۆتەکەی بەکارھێنا، کۆینێک بۆ زیادکرایەوە!\nکۆینەکانی تۆ: {user_data[ref_id]}")

    user_data[user_id] = user_data.get(user_id, 0)

    bot.send_photo(
        user_id,
        welcome_image,
        caption="بەخێربێیت بۆ بۆتی کۆرسەکان! 👋\nتکایە یەکێک لە دوگمەکان هەلبژێرە:",
        reply_markup=get_main_keyboard()
    )

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.from_user.id

    if call.data == "back":
        bot.edit_message_caption(
            call.message.chat.id,
            call.message.message_id,
            caption="بەخێربێیت بۆ بۆتی کۆرسەکان! 👋\nتکایە یەکێک لە دوگمەکان هەلبژێرە:",
            reply_markup=get_main_keyboard()
        )

    elif call.data == "courses":
        keyboard = types.InlineKeyboardMarkup()
        for name in courses:
            keyboard.add(types.InlineKeyboardButton(f"{name} - {courses[name]['coins']} کۆین", callback_data=f"course_{name}"))
        keyboard.add(types.InlineKeyboardButton("🔙 گەڕانەوە", callback_data="back"))
        bot.edit_message_caption(
            call.message.chat.id,
            call.message.message_id,
            caption="📚 ئەم کۆرسانە بەردەستە:",
            reply_markup=keyboard
        )

    elif call.data == "mycoins":
        coins = user_data.get(user_id, 0)
        bot.edit_message_caption(
            call.message.chat.id,
            call.message.message_id,
            caption=f"💰 ژمارەی کۆینەکانت: {coins}\n🔙 گەڕانەوە:",
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("🔙 گەڕانەوە", callback_data="back")
            )
        )

    elif call.data == "referral":
        link = f"https://t.me/Bot02PA_Bot?start={user_id}"
        bot.edit_message_caption(
            call.message.chat.id,
            call.message.message_id,
            caption=f"🔗 ئەمە لینکەکەتە:\n{link}",
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("🔙 گەڕانەوە", callback_data="back")
            )
        )

    elif call.data == "bots":
        bot.edit_message_caption(
            call.message.chat.id,
            call.message.message_id,
            caption="🤖 بۆتەکانت بزانی... (ئەم بەشە دەستکاری بکە بۆ زیادکردنی بۆت)\n🔙 گەڕانەوە:",
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("🔙 گەڕانەوە", callback_data="back")
            )
        )

    elif call.data.startswith("course_"):
        course_name = call.data.split("course_")[1]
        course_info = courses[course_name]
        coins_required = course_info['coins']

        if user_data[user_id] >= coins_required:
            bot.edit_message_caption(
                call.message.chat.id,
                call.message.message_id,
                caption=f"🎉 پیرۆزە بەڕێز، ئەمە کۆرسەکەتە: {course_info['link']}",
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🔙 گەڕانەوە", callback_data="back")
                )
            )
        else:
            bot.edit_message_caption(
                call.message.chat.id,
                call.message.message_id,
                caption="❌ ببورە بڕی پێویست لە کۆینت نیە بۆ کڕینی ئەم کۆرسە، تکایە کۆینەکانت زیادبکە لەڕێگەی لینکی بانگهێشتنامە یاخود کڕینی کۆین",
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🔙 گەڕانەوە", callback_data="back")
                )
            )

bot.infinity_polling()
