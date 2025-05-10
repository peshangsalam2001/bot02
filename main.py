import telebot
from snapchat_dl import SnapchatDL

# Your bot token
BOT_TOKEN = "8136969513:AAGkfHTKjxZJa9nvANKHUHW1LutPP3wDBCQ"
bot = telebot.TeleBot(BOT_TOKEN)

# Start command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Send me any public Snapchat link (story, spotlight, etc.), and I’ll try to fetch the download link!")

# Handler for all messages (Snapchat links)
@bot.message_handler(func=lambda message: True)
def handle_snapchat_link(message):
    url = message.text.strip()

    if "snapchat.com" not in url:
        bot.reply_to(message, "Please send a valid Snapchat URL.")
        return

    try:
        # Download Snapchat data using snapchat-dl
        downloader = SnapchatDL()
        result = downloader.download(url)

        if result and "url" in result:
            video_url = result["url"]
            bot.send_message(message.chat.id, "Here is your download link:")
            bot.send_message(message.chat.id, video_url)
        else:
            bot.send_message(message.chat.id, "Couldn't extract a video from this link. It may be private or unsupported.")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred:\n{str(e)}")

bot.polling()