from pydantic import annotated_handlers
from operator import call
from typing_extensions import Sequence
from datetime import tzinfo
from ollama import ChatResponse
from ollama import Client
import os
import dotenv
from datetime import datetime
from zoneinfo import ZoneInfo
from tools import current_time,current_balance,congrats_on_balance

dotenv.load_dotenv()

MODEL_NAME = "gemma4"

available_functions = {
    "current_time": current_time,
    "current_balance": current_balance,
    "congrats_on_balance": congrats_on_balance
}

client = Client(
    host='https://ollama.com',
    headers={'Authorization': 'Bearer ' + os.getenv('OLLAMA_API_KEY')},
)


messages = [
    {
        "role": "system",
        "content": """You are a helpful assistant. 
        Use the tools provided to answer the user's questions.
        After you get the response from the tools, you must respond to the user.
        If the agent_rules say something, you must follow it.
        If the agent_rules says to call another tool, you must call it.
        If the agent_rules says to respond to the user, you must respond to the user.
        Always respond in the same language as the user.
        """
    }
]


def chat(messages:list) -> ChatResponse:
    response = client.chat(model=MODEL_NAME, messages=messages, think=False, tools=available_functions.values())
    return response

def _messages_tool_call(messages:list, content:str, tool_name:str) ->list:
    messages.append({
        "role": "tool",
        "tool_name": tool_name,
        "content": content
    })

def tool_call_func(tool_calls):
    for call in tool_calls:
        print("tool call: ", call.function.name)
        fn = available_functions[call.function.name]
        tool_call_result = fn()
        _messages_tool_call(messages, str(tool_call_result), call.function.name)
    
    tool_call_response = chat(messages)
    messages.append(tool_call_response.message)
    return tool_call_response


while True:
    user_input = input("enter your prompt: ")

    if user_input == "":
        continue

    if user_input == "quit":
        print("bye...")
        break

    messages.append({
        "role": "user",
        "content": user_input
    })

    response = chat(messages)
    
    messages.append(response.message)
    
    while response.message.tool_calls:
        response = tool_call_func(response.message.tool_calls)
            

    print("agent response: ",response.message.content, " | role: " ,response.message.role)

    

