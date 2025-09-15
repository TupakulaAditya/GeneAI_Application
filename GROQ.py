from groq import Groq
import os
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()  # this loads .env values into os.environ

class GroqClient:
    def __init__(self, model, prompt):
        self.model = model
        self.prompt = prompt
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    
    def generate_text(self, messages=None):
        try:
            params = {
                "model": self.model,
                "messages": messages if messages is not None else [{"role": "user", "content": self.prompt}],
                "temperature": 0.7,
                "max_completion_tokens": 4096,
                "stream": True
            }
            
            completion = self.client.chat.completions.create(**params)
            response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    response += chunk.choices[0].delta.content
            
            return self.clean_response(response)
        except Exception as e:
            print(f"Error: {e}")
            # Try without streaming for deepseek or when messages provided
            if "deepseek" in self.model.lower() or messages is not None:
                try:
                    fallback_params = {
                        "model": self.model,
                        "messages": messages if messages is not None else [{"role": "user", "content": self.prompt}],
                        "temperature": 0.7,
                        "max_completion_tokens": 2048,
                        "stream": False
                    }
                    completion = self.client.chat.completions.create(**fallback_params)
                    response = completion.choices[0].message.content
                    return self.clean_response(response)
                except Exception as e2:
                    print(f"Deepseek fallback failed: {e2}")
            return None
    
    def clean_response(self, response):
        if not response:
            return response
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        return response.strip()