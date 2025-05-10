import os
import telebot
from snapchat_dl import SnapchatDL

# Initialize Telegram Bot
bot = telebot.TeleBot(os.environ.get('8136969513:AAGkfHTKjxZJa9nvANKHUHW1LutPP3wDBCQ'))

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Send /download <username> to get Snapchat stories")

@bot.message_handler(commands=['download'])
def handle_download(message):
    try:
        username = message.text.split()[1]
        bot.reply_to(message, f"⏳ Downloading stories for @{username}...")
        
        # Configure SnapchatDL
        dl = SnapchatDL(
            directory_prefix="downloads",
            max_workers=2,
            quiet=True
        )
        
        # Download stories
        results = dl.download(username)
        
        # Send media to user
        for file in os.listdir(f"downloads/{username}"):
            with open(f"downloads/{username}/{file}", 'rb') as f:
                bot.send_document(message.chat.id, f)

    except IndexError:
        bot.reply_to(message, "❌ Please provide a username")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

if __name__ == '__main__':
    bot.infinity_polling()