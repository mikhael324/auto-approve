from pyrogram import Client, filters, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from os import environ 
import time

API_ID = int(environ.get('API_ID', '4052973'))
API_HASH = environ.get('API_HASH', '3238bd8ae26df065d11c4054fe8a231c')
BOT_TOKEN = environ.get('BOT_TOKEN', '6111248503:AAGaXvVz8MlSB8uwc63m_pIRuxxLNV5ctis')

custom_admins = [1746132193]  # Replace with the user IDs you want to treat as admins

Bot = Client(name='Autoapprove', api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

try:
    mongo_client = MongoClient("mongodb+srv://joinreq:joinreq@cluster0.iug7n9m.mongodb.net/?retryWrites=true&w=majority")  # Replace with your MongoDB URI
    db = mongo_client["Cluster0"]  # Database name
    users_collection = db["users"]  # Collection name for storing users
    print("Connected to MongoDB successfully.")
except PyMongoError as e:
    print(f"Failed to connect to MongoDB: {e}")
    exit(1)  # Exit if the database connection fails

@Bot.on_message(filters.command("start") & filters.private)
def start(client, message):
    user_id = message.from_user.id

    # Welcome the user with an image, message, and buttons
    client.send_photo(
        chat_id=user_id,
        photo="https://graph.org/file/db66753a1eed955a7d7fc.jpg",
        caption="Add Me To Your Group / Channel !! I Will Accept All The Upcoming Join Requests",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "⚜ Add To Channel ⚜", 
                        url="http://t.me/auto_join_requests_accept_bot?startchannel=maeve_324&admin=invite_users+manage_chat"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔱 Add To Group 🔱", 
                        url="https://t.me/auto_join_requests_accept_bot?startgroup=maeve_324&admin=invite_users+manage_chat"
                    )
                ]
            ]
        )
    )

# Automatically approve all join requests
@Bot.on_chat_join_request()
def approve_and_store_user(client, message):
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name

        # Check if the user already exists in the database
        if users_collection.find_one({"user_id": user_id}):
            print(f"User {user_id} already exists in MongoDB. Skipping insertion.")
        else:
            # Store user information in MongoDB
            user_data = {
                "user_id": user_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "chat_id": chat_id
            }
            users_collection.insert_one(user_data)
            print(f"Stored user {user_id} in MongoDB")


        # Approve the join request
        client.approve_chat_join_request(chat_id, user_id)
        print(f"Approved join request for user {user_id}")
        
        # Send a message to the user
        client.send_message(
            chat_id=user_id,
            text=f"Hi {first_name}, Your Request To Join The Channel Has Been Accepted! Welcome! \n \n Press /start and Enjoy !!🎉"
        )
        print(f"Sent welcome message to user {user_id}")

    except PyMongoError as e:
        print(f"Failed to store user {user_id} in MongoDB: {e}")

    except errors.RPCError as e:
        print(f"Failed to approve join request for user {user_id}: {e}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

@Bot.on_message(filters.command("broadcast") & filters.private & filters.reply)
def start_broadcast(client, message):
    user_id = message.from_user.id

    # Check if the user is in the custom admin list
    if user_id not in custom_admins:
        message.reply_text("You don't have the required permissions to use this command.")
        print(f"User {user_id} tried to use /broadcast without permission.")
        return

    # Get the message to broadcast (the message that the admin replied to)
    broadcast_message = message.reply_to_message

    if not broadcast_message:
        message.reply_text("Please reply to a message to broadcast.")
        return

    # Initialize counters
    success_count = 0
    failed_count = 0
    blocked_count = 0

    try:
        # Use count_documents instead of count
        total_users = users_collection.count_documents({})
        message.reply_text(f"Broadcasting to {total_users} users...")

        users = users_collection.find({})

        for i, user in enumerate(users, start=1):
            try:
                if broadcast_message.text:
                    # Send the text message directly
                    client.send_message(
                        chat_id=user["user_id"],
                        text=broadcast_message.text,
                        parse_mode="html"
                    )
                else:
                    # Handle other media types like photos, videos, etc.
                    broadcast_message.copy(
                        chat_id=user["user_id"]
                    )
                    
                success_count += 1
                print(f"[{i}/{total_users}] Success: Broadcasted message to user {user['user_id']}")
            except errors.UserIsBlocked:
                blocked_count += 1
                print(f"[{i}/{total_users}] Blocked: User {user['user_id']} has blocked the bot.")
            except errors.RPCError as e:
                failed_count += 1
                print(f"[{i}/{total_users}] Failed: Could not send message to user {user['user_id']} due to error: {e}")

            # Update admin with progress every 10 users or at the end
            if i % 10 == 0 or i == total_users:
                message.reply_text(f"Progress: {i}/{total_users} - Success: {success_count}, Failed: {failed_count}, Blocked: {blocked_count}")
                time.sleep(1)  # Prevent Telegram from limiting requests

        # Final status report
        message.reply_text(
            f"Broadcast completed.\nTotal: {total_users}\n"
            f"Success: {success_count}\nFailed: {failed_count}\nBlocked: {blocked_count}"
        )
        print(f"Broadcast by user {user_id} completed.")

    except PyMongoError as e:
        print(f"Failed to retrieve users from MongoDB: {e}")
        message.reply_text("An error occurred while retrieving the users.")

    except Exception as e:
        print(f"An unexpected error occurred during broadcast: {e}")
        message.reply_text("An unexpected error occurred during the broadcast.")
        
                

@Bot.on_message(filters.command("stats") & filters.private)
def stats_command(client, message):
    try:
        # Check if the user is in the custom admin list
        if message.from_user.id not in custom_admins:
            message.reply_text("You don't have the required permissions to use this command.")
            print(f"User {message.from_user.id} tried to use /stats without permission.")
            return

        # Count the number of users in the MongoDB collection
        user_count = users_collection.count_documents({})
        message.reply_text(f"⚧️ Total Users : {user_count}")
        print(f"Custom admin {message.from_user.id} requested stats: {user_count} users in the database.")

    except errors.RPCError as e:
        print(f"Failed to check user permissions or retrieve stats: {e}")
        message.reply_text("Sorry, an error occurred while retrieving the stats or checking permissions.")

    except PyMongoError as e:
        print(f"Failed to retrieve stats from MongoDB: {e}")
        message.reply_text("Sorry, an error occurred while retrieving the stats.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        message.reply_text("Sorry, an unexpected error occurred.")
        


if __name__ == "__main__":
    Bot.run()
