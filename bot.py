import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from zipfile import ZipFile
from io import BytesIO
from flask import Flask, request, jsonify
import threading

# Fetch the bot token and allowed user IDs from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')  # Telegram Bot Token from environment variable
ALLOWED_USER_IDS = list(map(int, os.getenv('ALLOWED_USER_IDS', '').split(',')))  # List of allowed user IDs from environment variable

# Flask app initialization
app = Flask(__name__)

# Function to scrape image links from chapter page
def get_image_links(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    img_tags = soup.find_all('img')
    
    # Extracting image URLs
    image_urls = [img['src'] for img in img_tags if img.get('src')]
    return image_urls

# Function to create a ZIP file from images
def create_zip_from_images(image_urls):
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, 'w') as zip_file:
        for idx, img_url in enumerate(image_urls):
            img_data = requests.get(img_url).content
            img_name = f"image_{idx + 1}.jpg"
            zip_file.writestr(img_name, img_data)
    zip_buffer.seek(0)
    return zip_buffer

# Telegram bot handler for image download and ZIP creation
async def download_and_send_zip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in ALLOWED_USER_IDS:
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    url = update.message.text.strip()
    
    if not url:
        await update.message.reply_text("Please send a valid chapter URL.")
        return
    
    await update.message.reply_text("Downloading images, please wait...")

    # Step 1: Scrape image URLs from the chapter page
    image_urls = get_image_links(url)
    
    if not image_urls:
        await update.message.reply_text("Failed to extract images from the page.")
        return

    # Step 2: Create a ZIP file with the images
    zip_buffer = create_zip_from_images(image_urls)
    
    # Step 3: Send the ZIP file as a Telegram document
    await update.message.reply_document(document=zip_buffer, filename="chapter_images.zip")

# Flask route for health check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

# Flask route for the webhook (Telegram Bot)
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    update = Update.de_json(data, bot)
    bot.process_update(update)
    return jsonify({"status": "ok"}), 200

# Initialize Telegram bot
bot = ApplicationBuilder().token(BOT_TOKEN).build()

# Add message handler for non-command text
bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_and_send_zip))

# Function to set up webhook (for Koyeb deployment)
def set_webhook():
    webhook_url = 'https://<your-app-name>.koyeb.app/webhook'  # Replace with your actual Koyeb app URL
    bot.set_webhook(webhook_url)

# Start the Flask app and the Telegram bot in parallel
def run_flask_app():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

def run_bot():
    bot.run_polling()

if __name__ == '__main__':
    # Set the webhook to Koyeb URL
    set_webhook()

    # Run Flask app in one thread and Telegram bot in another
    threading.Thread(target=run_flask_app).start()
    threading.Thread(target=run_bot).start()
