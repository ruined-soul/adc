from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid

# Replace with your own values
api_id = '2170492'
api_hash = '82b683da442942d5c177ec520318a32f'
bot_token = '7304879730:AAHWnILVrNQjeD7QuLMd3UOuC5xf72mzd5I'
admin_chat_id = '1159381624'  # Replace with the admin's Telegram user ID

app = Client("contact_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.private & ~filters.bot)
async def forward_to_admin(client, message):
    try:
        forwarded_message = await message.forward(admin_chat_id)
        await forwarded_message.reply_text(f"From: {message.from_user.id}")
    except PeerIdInvalid:
        await message.reply_text("Error: The admin has not started a conversation with the bot yet. Please contact the admin to start a conversation with the bot.")

@app.on_message(filters.chat(admin_chat_id) & filters.reply)
async def reply_to_user(client, message):
    if message.reply_to_message and message.reply_to_message.forward_from:
        original_sender_id = int(message.reply_to_message.text.split("From: ")[-1])
        await client.send_message(original_sender_id, message.text)

if __name__ == "__main__":
    app.run()
