import telebot
import os
from PIL import Image
from fpdf import FPDF

API_TOKEN = '8136137612:AAFguFx9ZQPSwyiyDZz08-TDJ5ztLiPVbDY'
bot = telebot.TeleBot(API_TOKEN)

# Dictionary to temporarily store photos for each user
user_photos = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "📸 Send me one or more images, and I'll convert them to a PDF!")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.chat.id

    # Get file ID and info
    file_info = bot.get_file(message.photo[-1].file_id)
    file = bot.download_file(file_info.file_path)

    # Create temp folder for user
    folder = f'temp/{user_id}'
    os.makedirs(folder, exist_ok=True)

    # Save the image
    image_path = f"{folder}/{message.message_id}.jpg"
    with open(image_path, 'wb') as new_file:
        new_file.write(file)

    # Store path in list
    if user_id not in user_photos:
        user_photos[user_id] = []
    user_photos[user_id].append(image_path)

    bot.send_message(user_id, "✅ Image saved! Send more or type /convert to make a PDF.")

@bot.message_handler(commands=['convert'])
def convert_to_pdf(message):
    user_id = message.chat.id
    if user_id not in user_photos or len(user_photos[user_id]) == 0:
        bot.send_message(user_id, "❌ You haven't sent any images.")
        return

    image_paths = sorted(user_photos[user_id])  # Sort by order received
    pdf_path = f"temp/{user_id}/output.pdf"

    pdf = FPDF()
    for image_path in image_paths:
        image = Image.open(image_path)
        image = image.convert('RGB')
        image.save("temp/temp.jpg")

        pdf.add_page()
        pdf.image("temp/temp.jpg", x=10, y=10, w=190)  # Resize if needed

    pdf.output(pdf_path, "F")

    with open(pdf_path, 'rb') as pdf_file:
        bot.send_document(user_id, pdf_file)

    # Cleanup
    for img in image_paths:
        os.remove(img)
    os.remove("temp/temp.jpg")
    os.remove(pdf_path)
    user_photos[user_id] = []

    bot.send_message(user_id, "🎉 PDF created and sent!")

bot.polling()
