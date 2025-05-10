import telebot
from snapchat_dl import SnapchatDL

# Replace with your actual bot token
BOT_TOKEN = "8136969513:AAGkfHTKjxZJa9nvANKHUHW1LutPP3wDBCQ"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Send me a Snapchat video link. and I'll try to download it for you!")

@bot.message_handler(func=lambda message: True)
def download_snapchat_video(message):
    url = message.text.strip()
    
    if "https://www.snapchat.com/" not in url:
        bot.reply_to(message, "Please send a valid Snapchat video URL.")
        return

    try:
        video_url = SnapchatDL().get_video_url(url)
        if video_url:
            bot.send_message(message.chat.id, "Here's your download link:")
            bot.send_message(message.chat.id, video_url)
        else:
            bot.reply_to(message, "Could not extract video. The content might be private or invalid.")
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

bot.polling()