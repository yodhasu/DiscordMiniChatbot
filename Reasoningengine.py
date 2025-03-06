import httpx
import json
import os

class Reasoning():
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_R1_API_OPENROUTER")
    
    async def getReasoningwithImage(self, query, image):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": "qwen/qwen2.5-vl-72b-instruct:free",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": query},
                                {"type": "image_url", "image_url": {"url": image}}
                            ]
                        }
                    ]
                },
                timeout=60  # Increase timeout if necessary
            )
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    async def getReasoning(self, query):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": "deepseek/deepseek-r1-distill-llama-70b:free",
                    "messages": [{"role": "user", "content": query}]
                },
                timeout=60
            )
        result = response.json()
        return result["choices"][0]["message"]["content"]

    async def useReasoning(self, query, image):
        if image:
            return await self.getReasoningwithImage(query, image)
        else:
            return await self.getReasoning(query)
