import os
import asyncio
from AIengine import AIengine
from Reasoningengine import Reasoning
from datetime import datetime

class Chatbot:
    def __init__(self, sys_prompt_dir = None, usr_prompt_dir = None):
        self.chatapi_key = os.getenv("GROQ_API_KEY")
        self.engine = AIengine(self.chatapi_key)
        self.reasoningengine = Reasoning()
        self.master = "Yodha"
        self.masterbio = "Your creator. Male, 5th semester college student, have pretty good knowledge in machine learning and AI. Loves to watch anime and of course a weeb. Discord username: yodhasu"
        self.char = "Z.E.N.I.T.H (Zestful Executive Navigator and Intuitive Task Hostess)"
        self.nickname = "Zen"
        self.systemPromptDir = sys_prompt_dir
        self.userPromptDir = usr_prompt_dir
        self.system_prompt = ""
        self.user_prompt = ""
        
    def getPrompt(self):
        # get system prompt
        try:
            # print(self.system_prompt_from_directory)
            if self.system_prompt == "":
                with open(self.systemPromptDir, "r", encoding="utf-8") as sysprompt:
                    self.system_prompt = sysprompt.read()
        except Exception as e:
            raise(f"Error opening system prompt with error: {e}")
        # get user prompt
        try:
            # print(self.user_prompt_from_directory)
            if self.user_prompt == "":
                with open(self.userPromptDir, "r", encoding="utf-8") as usrprompt:
                    self.user_prompt = usrprompt.read()
        except Exception as e:
            raise(f"Error opening user prompt with error: {e}")
    
    def chatBasic(self, query, historyjson, intention, image):
        self.getPrompt()
        
        local_system_prompt = self.system_prompt
        local_user_prompt = self.user_prompt
        
        local_system_prompt = local_system_prompt.format(
            user = self.master,
            userbio = self.masterbio,
            char = self.char
        )
        
        local_user_prompt=local_user_prompt.format(
            history = historyjson,
            date = str(datetime.now()),
            time = self.get_time_of_day(),
            question = query,
            intent = intention
        )
        
        if image:
            image_result = self.engine.groqVision(query=query, img_path=image)
            return image_result
        else:
            system_response = self.engine.process_query(local_user_prompt, local_system_prompt, query)
            return system_response
    
    def retrieve_history(self, chat_history):
        system = "You are a smart AI that is used to summarize what happend in the last chat using this chat_history in detailed explanation"
        query = "Summarize what happend in the last chat using this chat_history in detailed explanation" + "\n".join(chat_history)
        return self.engine.generate_response(query, system)
    
    async def tryToThink(self, query, historyjson, intention, image=None):
        print("Getting reasoning response")
        local_user_prompt=self.user_prompt.format(
            history = historyjson,
            date = str(datetime.now()),
            time = self.get_time_of_day(),
            question = query,
            intent = intention
        )
        reasoning = await self.reasoningengine.useReasoning(local_user_prompt, image)
        
        local_system_prompt = self.system_prompt
        
        prompt = f"""
        Given the reasoning model response, convert it into a Mini Z.E.N.I.T.H roleplay-style reply based on the system prompt. Keep it short, natural, and to the point while maintaining personality. max char length: 1500

        Reasoning Response: {reasoning}
        Roleplay Response:
        """
        
        # system_response = await self.engine.generate_response(prompt, local_system_prompt, query)
        print("Converting to zenith")
        system_response = await asyncio.to_thread(self.engine.generate_response, prompt, local_system_prompt)
        return system_response

        
    def intentIdentifier(self, current_input, previous_input):
        
        prompt = f"""
        This is the user's current input: {current_input}
        This is the 20 last chat history: {previous_input}
        
        Based on the user's current input and previous input, identify the intention of the user's input in a chat between character and user and provide a detailed explanation of the intention of the user's input.
        Also try to check if the user's input is a question or a statement and is the previous input related to the current input.
        DO NOT USE ANY TOOLS! YOU ARE NOT ALLOWED TO USE ANY TOOLS!
        """
        system_prompt = "You are a smart AI that is used to identify intention of the user's input in a chat between character and user. Answer in paragraph but limit your answer to 20 - 70 token."

        intent = self.engine.process_query(prompt, system_prompt, input=None)
        print(intent)
        return intent
        
    @staticmethod
    def get_time_of_day():
        """Return the current time of day."""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        else:
            return "night"
    
    
# cb = Chatbot(sys_prompt_dir=r"prompts\system_prompt.txt", usr_prompt_dir=r"prompts\user_prompt.txt")