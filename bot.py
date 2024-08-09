from pyrogram import Client, filters
from os import environ 

API_ID = int(environ.get('API_ID', '4052973'))
API_HASH = environ.get('API_HASH', '3238bd8ae26df065d11c4054fe8a231c')
BOT_TOKEN = environ.get('BOT_TOKEN', '6111248503:AAGaXvVz8MlSB8uwc63m_pIRuxxLNV5ctis')

Bot = Client(name='Autoapprove', api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Automatically approve all join requests
@Bot.on_chat_join_request()
def approve_all_requests(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Approve the join request
    client.approve_chat_join_request(chat_id, user_id)
    print(f"Approved join request for user {user_id}")

if __name__ == "__main__":
    app.run()
