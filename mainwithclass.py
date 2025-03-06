import discord
import os
import json
import asyncio
from keep_alive import keep_alive
from Chatbotclass import Chatbot

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.basicChatbot = Chatbot(sys_prompt_dir="system_prompt.txt", usr_prompt_dir="user_prompt.txt")
        self.chatHistory = []
        self.processing_messages = set()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        channel_id = 1336699913186185359  # Example channel ID
        channel = self.get_channel(channel_id)
        
        if channel:
            await channel.send("Systems starting, please wait...")
            self.chatHistory = [f"{msg.author}: {msg.content}" for msg in await self.fetch_all_messages(channel)]
            await channel.send("Systems ready!")
    
    async def fetch_all_messages(self, channel, limit=25):
        """Fetch messages from channel history to build context."""
        try:
            return [message async for message in channel.history(limit=limit)]
        except Exception as e:
            print(f"Either Empty channel or error {e}")
            return []
    
    async def process_reasoning(self, message, prompt, history, intention, img = None):
        """Runs the reasoning model while sending periodic updates."""
        try:
            thinking_messages = [
                "Thinking...", "Still thinking...", "Processing your request...", "Almost done..."
            ]
            thinking_msg = await message.reply(thinking_messages[0])
            
            for index in range(1, len(thinking_messages)):
                await asyncio.sleep(10)
                await thinking_msg.edit(content=thinking_messages[index])
            
            botmsg = await self.basicChatbot.tryToThink(query=prompt.replace("!reasoning", ""), historyjson=history, intention=intention, image=img)
            await thinking_msg.edit(content=botmsg)
        
        except Exception as e:
            await message.reply(f"Error on process_reasoning: {e}", mention_author=True)
        
        finally:
            self.processing_messages.discard(message.id)
    
    async def on_message(self, message):
        if message.author.id == self.user.id:
            return
        
        bot_mention = f"<@{self.user.id}>"

        if not message.content.startswith(bot_mention):  # Only respond if the message starts with the bot's tag
            return
        
        if self.user not in message.mentions:  # Only respond if the bot is tagged
            return
        
        if message.id in self.processing_messages:
            print(f"Skipping duplicate message: {message.id}")
            return
        
        self.processing_messages.add(message.id)
        print(self.user in message.mentions)
        
        if self.user in message.mentions:
            try:
                get_msg = message.content
                get_att_url = None
                get_att_type = None

                if message.attachments:
                    get_att_url = message.attachments[0].url
                    get_att_type = message.attachments[0].content_type

                input_img = get_att_url if get_att_type and "image" in get_att_type else None
                prompt = f"User: {message.author}\nContent: {get_msg}"
                print(f"Processing message: {message.id}")
                intention = self.basicChatbot.intentIdentifier(prompt, self.chatHistory[:2])  
                print(f"Identified intention: {intention}")
                
                if "!reasoning" in get_msg:
                    print("Reasoning is used")
                    asyncio.create_task(self.process_reasoning(message, prompt, history=json.dumps(self.chatHistory), intention=intention, img=input_img))
                else:
                    print("Regular is used")
                    botmsg = self.basicChatbot.chatBasic(query=prompt, historyjson=json.dumps(self.chatHistory), intention=intention, image=input_img)
                    await message.reply(botmsg.replace(f"{self.user}", ""), mention_author=True)
            
            except Exception as e:
                await message.reply(f"Error on_message: {e}", mention_author=True)

if __name__ == '__main__':
    intents = discord.Intents.default()
    intents.message_content = True
    
    client = MyClient(intents=intents)
    keep_alive()
    client.run(os.getenv('DISCORD_BOT_TOKEN'))
