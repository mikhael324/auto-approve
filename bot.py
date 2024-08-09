from pyrogram import Client, filters

app = Client("my_bot", bot_token="6111248503:AAGaXvVz8MlSB8uwc63m_pIRuxxLNV5ctis")  # Replace "my_bot" with your bot session name

# Automatically approve all join requests
@app.on_message(filters.chat_join_request)
def approve_all_requests(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Approve the join request
    client.approve_chat_join_request(chat_id, user_id)
    print(f"Approved join request for user {user_id}")

if __name__ == "__main__":
    app.run()
