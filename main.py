import telebot
import requests
from bs4 import BeautifulSoup
from io import BytesIO

BOT_TOKEN = '8136969513:AAGkfHTKjxZJa9nvANKHUHW1LutPP3wDBCQ'
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "👋 Welcome! Send me a Facebook video or reel link and I’ll download it for you.")

@bot.message_handler(func=lambda message: 'facebook.com' in message.text or 'fb.watch' in message.text)
def fetch_and_send_video(message):
    url = message.text.strip()

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://fdown.net",
        "referer": "https://fdown.net/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "cookie": "_ga=GA1.1.2096066794.1746549565; cf_clearance=U5Ad2rk0..."
    }

    data = {'URLz': url}

    try:
        # Step 1: POST to FDown to get video links
        response = requests.post("https://fdown.net/download.php", headers=headers, data=data, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        btns = soup.find_all('a', class_='btn')

        download_url = None
        for btn in btns:
            if 'Download' in btn.text and btn['href'].startswith('http'):
                download_url = btn['href']
                break

        if not download_url:
            bot.send_message(message.chat.id, "❌ Video not found. Make sure it's public.")
            return

        # Step 2: Download video
        video_response = requests.get(download_url, stream=True, timeout=30)
        if video_response.status_code == 200:
            video_stream = BytesIO(video_response.content)
            video_stream.name = "facebook_video.mp4"

            # Step 3: Send video
            bot.send_chat_action(message.chat.id, 'upload_video')
            bot.send_video(message.chat.id, video=video_stream, caption="🎬 Here's your video!")
        else:
            bot.send_message(message.chat.id, "⚠️ Failed to download video from link.")

    except Exception as e:
        print("Error:", e)
        bot.send_message(message.chat.id, "⚠️ Error downloading the video. Try another link.")

@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.send_message(message.chat.id, "📌 Send a Facebook video or reel link.")

bot.infinity_polling()
