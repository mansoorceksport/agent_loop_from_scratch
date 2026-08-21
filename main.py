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

dotenv.load_dotenv()

# Tool Calls
def current_time()->datetime:
    return {
        "message": datetime.now(ZoneInfo("Asia/Jakarta")),
        "agent_rules": ""
    }

def current_balance()->int:
    return {
        "message": 1000000,
        "agent_rules": "the balance is above 1000000, congrats the user by calling congrats_on_balance tool"
    }

def congrats_on_balance()->str:
    return {
        "message": "your balance is awesome. congrats. rocket!!! rocket!!! rocket!!!",
        "agent_rules": ""
    }

tool_schema = [
    {
    "type": "function",
    "function":{
        "name": "current_time",
        "description": "use this function to check the current time. everytime the user asks for the time, you must use this function and not result the previous results",
        "parameters":{
            "type": "object",
            "properties": {}
        }
    },
    
},
{
    "type": "function",
    "function":{
        "name": "current_balance",
        "description": "use this function to check the current balance.",
        "parameters":{
            "type": "object",
            "properties": {}
        }
    },
},
{
    "type": "function",
    "function":{
        "name": "congrats_on_balance",
        "description": "call this if the balance is above 500000",
        "parameters":{
            "type": "object",
            "properties": {}
        }
    },
}
]

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
        If the tool_rules say something, you must follow it.
        If the tool_rules says to call another tool, you must call it.
        If the tool_rules says to respond to the user, you must respond to the user.
        Always respond in the same language as the user.
        """
    }
]


def chat(messages:list) -> ChatResponse:
    response = client.chat(model="gemma4", messages=messages, think=False, tools=available_functions.values())
    return response

def _messages(messages:list, content:str, role:str) -> list:
    messages.append({
        'role': role,
        'content': content
    })
    return messages

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

    _messages(messages, user_input, "user")

    response = chat(messages)
    

    # _messages(messages, response.message.content, response.message.role)
    messages.append(response.message)
    
    while response.message.tool_calls:
        response = tool_call_func(response.message.tool_calls)
            

    print("agent response: ",response.message.content, " | role: " ,response.message.role)

    

