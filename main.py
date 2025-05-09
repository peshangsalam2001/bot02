import telebot
import os
from convertor import Converter

# Replace with your bot token
BOT_TOKEN = '7835872937:AAHmy808cQtDdMysSxlli_RlbVKOBkkyApA'
bot = telebot.TeleBot(BOT_TOKEN)

# Store user sessions in memory (user_id: list of image file paths)
user_sessions = {}

# Ensure a temp directory exists
TEMP_DIR = 'temp_images'
os.makedirs(TEMP_DIR, exist_ok=True)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Send me one or more pictures. When done, send /convert to get your PDF.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    # Get the highest resolution photo
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    # Save the image to temp directory
    file_path = os.path.join(TEMP_DIR, f'{user_id}_{message.message_id}.jpg')
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    # Add to user session
    user_sessions.setdefault(user_id, []).append(file_path)
    bot.reply_to(message, "Photo received. Send more or /convert to create PDF.")

@bot.message_handler(commands=['convert'])
def convert_to_pdf(message):
    user_id = message.from_user.id
    images = user_sessions.get(user_id)
    if not images:
        bot.reply_to(message, "No images found. Please send some photos first.")
        return

    pdf_path = os.path.join(TEMP_DIR, f'{user_id}_output.pdf')
    try:
        # Use convertor to create PDF
        Converter(images).convert(pdf_path)
        with open(pdf_path, 'rb') as pdf_file:
            bot.send_document(message.chat.id, pdf_file, caption="Here is your PDF!")
    except Exception as e:
        bot.reply_to(message, f"Error creating PDF: {e}")
    finally:
        # Clean up temp files
        for img in images:
            if os.path.exists(img):
                os.remove(img)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        user_sessions[user_id] = []

@bot.message_handler(commands=['cancel'])
def cancel_session(message):
    user_id = message.from_user.id
    images = user_sessions.get(user_id, [])
    for img in images:
        if os.path.exists(img):
            os.remove(img)
    user_sessions[user_id] = []
    bot.reply_to(message, "Session cancelled and images deleted.")

if __name__ == '__main__':
    print("Bot is running...")
    bot.polling(none_stop=True)
