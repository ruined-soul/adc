import logging
from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid

# Set up logging
logging.basicConfig(level=logging.INFO)

# Replace with your own values
api_id = '2170492'
api_hash = '82b683da442942d5c177ec520318a32f'
bot_token = '7304879730:AAHWnILVrNQjeD7QuLMd3UOuC5xf72mzd5I'
admin_chat_id = '1159381624'
app = Client("contact_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.private & ~filters.bot)
async def forward_to_admin(client, message):
    try:
        logging.info(f"Forwarding message from {message.from_user.id} to admin {admin_chat_id}")
        # Forward the message to the admin without including the user ID
        forwarded_message = await message.forward(admin_chat_id)
        # Optionally, add a confirmation message to the admin
        await client.send_message(admin_chat_id, "You have a new contact message.")
    except PeerIdInvalid:
        logging.error("Peer ID is invalid or admin has not started a chat.")
        await message.reply_text("Error: The admin has not started a conversation with the bot yet. Please contact the admin to start a conversation with the bot.")

@app.on_message(filters.chat(admin_chat_id) & filters.reply)
async def reply_to_user(client, message):
    if message.reply_to_message and message.reply_to_message.forward_from:
        # Extract the original sender ID from the reply message
        original_sender_id = int(message.reply_to_message.text.split("From: ")[-1])
        logging.info(f"Sending reply from admin {admin_chat_id} to user {original_sender_id}")
        await client.send_message(original_sender_id, message.text)

@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    welcome_message = (
        "Hello! I'm personal bot of my @ruined_soul.\n"
        "Please send your message, and I will forward it to the master.\n"
        "If you have any questions or need support, let me know!"
    )
    await message.reply_text(welcome_message)

if __name__ == "__main__":
    app.run()
