# import discord
# import os
# import json
# import asyncio
# from keep_alive import keep_alive
# from Chatbotclass import Chatbot

# # Initialize Discord client with message content intent.
# intents = discord.Intents.default()
# intents.message_content = True
# client = discord.Client(intents=intents)

# basicChatbot = Chatbot(sys_prompt_dir="system_prompt.txt", usr_prompt_dir="user_prompt.txt")
# chatHistory = []
# processing_messages = set()  # Track messages to avoid duplicate replies

# async def fetch_all_messages(channel, limit=25):
#     """Fetch messages from channel history to build context."""
#     all_msg = []
#     try:
#         all_msg = [message async for message in channel.history(limit=limit)]
#     except Exception as e:
#         print(f"Either Empty channel or error {e}")
#     return all_msg

# @client.event
# async def on_ready():
#     global chatHistory
#     print(f'Logged in as {client.user} (ID: {client.user.id})')
#     print('------')
#     channel_id = 1336699913186185359  # Example channel ID
#     channel = client.get_channel(channel_id)
    
#     if channel:
#         await channel.send("Systems starting, please wait...")
#         chatHistory = [f"{msg.author}: {msg.content}" for msg in await fetch_all_messages(channel)]
#         await channel.send("Systems ready!")

# async def process_reasoning(message, prompt):
#     """Runs the reasoning model while sending periodic updates."""
#     try:
#         thinking_messages = [
#             "Thinking...",
#             "Still thinking...",
#             "Processing your request...",
#             "Almost done...",
#         ]
        
#         # Initial response
#         thinking_msg = await message.reply(thinking_messages[0])
        
#         # Start sending updates every 5 seconds
#         index = 1
#         while index < len(thinking_messages):
#             await asyncio.sleep(10)  # Wait 5 seconds
#             await thinking_msg.edit(content=thinking_messages[index])  # Update message
#             index += 1

#         # Process reasoning in the background
#         botmsg = basicChatbot.tryToThink(query=prompt)

#         # Send final message and delete the "Thinking..." updates
#         await thinking_msg.edit(content=botmsg)  

#     except Exception as e:
#         await message.reply(f"Error process_reasoning: {e}", mention_author=True)

#     finally:
#         processing_messages.discard(message.id)  # Mark message as processed

# @client.event
# async def on_message(message):
#     global chatHistory, processing_messages

#     if message.author.id == client.user.id:
#         return

#     try:
#         get_msg = message.content
#         prompt = f"User: {message.author}\nContent: {get_msg}"
#         print(f"Processing message: {message.id}")

#         if "!reasoning" in get_msg:
#             if message.id in processing_messages:
#                 print(f"Skipping duplicate message: {message.id}")
#                 return  # Avoid double processing

#             processing_messages.add(message.id)
#             asyncio.create_task(process_reasoning(message, prompt))  # Run in parallel
#         else:
#             botmsg = basicChatbot.chatBasic(query=prompt, historyjson=json.dumps(chatHistory))
#             await message.reply(botmsg, mention_author=True)

#     except Exception as e:
#         await message.reply(f"Error on_message: {e}", mention_author=True)

# if __name__ == '__main__':
#     keep_alive()
#     client.run(os.getenv('DISCORD_BOT_TOKEN'))
