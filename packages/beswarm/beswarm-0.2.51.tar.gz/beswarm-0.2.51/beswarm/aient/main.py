import os

from aient.utils import prompt
from aient.models import chatgpt
GPT_ENGINE = os.environ.get('MODEL')

API = os.environ.get('API_KEY')
API_URL = os.environ.get('BASE_URL', None)

message = "hi"
systemprompt = os.environ.get('SYSTEMPROMPT', prompt.chatgpt_system_prompt)

bot = chatgpt(api_key=API, api_url=API_URL , engine=GPT_ENGINE, system_prompt=systemprompt)
for text in bot.ask_stream(message):
    print(text, end="")