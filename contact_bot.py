import logging
from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Replace with your own values
api_id = '2170492'
api_hash = '82b683da442942d5c177ec520318a32f'
bot_token = '7304879730:AAHWnILVrNQjeD7QuLMd3UOuC5xf72mzd5I'
admin_chat_id = '1159381624'

app = Client("contact_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Dictionary to store user messages and their corresponding chat IDs
user_messages = {}

@app.on_message(filters.private & ~filters.bot)
async def forward_to_admin(client, message):
    try:
        logging.info(f"Forwarding message from {message.from_user.id} to admin {admin_chat_id}")
        # Store the user chat ID and message ID for reply purposes
        user_messages[message.message_id] = (message.from_user.id, message.chat.id)
        # Forward the message to the admin
        await message.forward(admin_chat_id)
        
    except PeerIdInvalid:
        logging.error("Peer ID is invalid or admin has not started a chat.")
        await message.reply_text("Error: The admin has not started a conversation with the bot yet. Please contact the admin to start a conversation with the bot.")

@app.on_message(filters.chat(admin_chat_id) & filters.reply)
async def reply_to_user(client, message):
    if message.reply_to_message:
        # Extract the original message ID from the reply
        original_message_id = message.reply_to_message.message_id
        user_info = user_messages.get(original_message_id)
        if user_info:
            original_sender_id, user_chat_id = user_info
            logging.info(f"Sending reply from admin {admin_chat_id} to user {user_chat_id}")
            await client.send_message(user_chat_id, message.text)
        else:
            logging.error(f"User chat ID not found for message ID {original_message_id}")
            await client.send_message(admin_chat_id, "Failed to find the user chat ID. Please check.")

@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    welcome_message = (
        "Hello! I'm your contact bot.\n"
        "Please send your message, and I will forward it to the admin.\n"
        "If you have any questions or need support, let me know!"
    )
    logging.info("Sending start message to user.")
    await message.reply_text(welcome_message)

if __name__ == "__main__":
    app.run()
