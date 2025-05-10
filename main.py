import telebot
import requests
import re

# Replace with your bot token
TOKEN = '8136969513:AAGkfHTKjxZJa9nvANKHUHW1LutPP3wDBCQ'
bot = telebot.TeleBot(TOKEN)

# Facebook video URL pattern
fb_pattern = re.compile(r'(https?://)?(www\.)?(facebook|fb)\.(com)/[^\s]+')

def get_fb_video_url(fb_url):
    api_url = 'https://fdownloader.net/api/ajax'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://fdownloader.net',
        'Referer': 'https://fdownloader.net/',
        'User-Agent': 'Mozilla/5.0'
    }
    data = {'q': fb_url}
    response = requests.post(api_url, headers=headers, data=data)
    if response.status_code == 200:
        result = response.json()
        if 'video' in result and 'hd' in result['video']:
            return result['video']['hd']
    return None

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    fb_link = message.text.strip()

    if re.match(fb_pattern, fb_link):
        bot.send_chat_action(message.chat.id, 'upload_video')
        bot.reply_to(message, "🔄 Processing your Facebook video...")

        video_url = get_fb_video_url(fb_link)
        if video_url:
            bot.send_video(message.chat.id, video=video_url, caption="✅ Here is your Facebook video.")
        else:
            bot.reply_to(message, "❌ Failed to download. Make sure the link is public.")
    else:
        bot.reply_to(message, "📥 Send me a Facebook video/reel/story link to download.")

# Start the bot
print("Bot is running...")
bot.infinity_polling()
