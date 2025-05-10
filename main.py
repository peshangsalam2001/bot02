import telebot
from snapchat_dl import SnapchatDL

# Your bot token
BOT_TOKEN = "8136969513:AAGkfHTKjxZJa9nvANKHUHW1LutPP3wDBCQ"

bot = telebot.TeleBot(BOT_TOKEN)

# Start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Send me any public Snapchat link (story, spotlight, etc.), and I’ll fetch the download link!")

# Handle all other messages
@bot.message_handler(func=lambda message: True)
def handle_snapchat_link(message):
    url = message.text.strip()

    # Validate Snapchat link
    if "snapchat.com" not in url:
        bot.reply_to(message, "Please send a valid Snapchat link.")
        return

    try:
        # Attempt to fetch the video URL
        downloader = SnapchatDL()
        video_url = downloader.get_video_url(url)

        if video_url:
            bot.send_message(message.chat.id, "Here is your download link:")
            bot.send_message(message.chat.id, video_url)
        else:
            bot.send_message(message.chat.id, "Couldn't extract the video. The link might be private or unsupported.")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred:\n{str(e)}")

bot.polling()