from pyrogram import Client, filters, errors
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from os import environ 

API_ID = int(environ.get('API_ID', '4052973'))
API_HASH = environ.get('API_HASH', '3238bd8ae26df065d11c4054fe8a231c')
BOT_TOKEN = environ.get('BOT_TOKEN', '6111248503:AAGaXvVz8MlSB8uwc63m_pIRuxxLNV5ctis')

Bot = Client(name='Autoapprove', api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

try:
    mongo_client = MongoClient("mongodb+srv://joinreq:joinreq@cluster0.iug7n9m.mongodb.net/?retryWrites=true&w=majority")  # Replace with your MongoDB URI
    db = mongo_client["Cluster0"]  # Database name
    users_collection = db["users"]  # Collection name for storing users
    print("Connected to MongoDB successfully.")
except PyMongoError as e:
    print(f"Failed to connect to MongoDB: {e}")
    exit(1)  # Exit if the database connection fails

# Automatically approve all join requests
@Bot.on_chat_join_request()
def approve_all_requests(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Approve the join request
    client.approve_chat_join_request(chat_id, user_id)
    print(f"Approved join request for user {user_id}")

if __name__ == "__main__":
    Bot.run()
