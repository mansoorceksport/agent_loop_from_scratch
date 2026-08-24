from agent_loop_from_scratch.adapters.repository.balance_dict import BalanceDicRepositoryImpl
from agent_loop_from_scratch.service.balance_service import BalanceServiceImpl
from agent_loop_from_scratch.ports.service.balance import BalanceService
from ollama import ChatResponse
from ollama import Client
import os
import dotenv
from agent_loop_from_scratch.tools import current_time,current_balance,congrats_on_balance
from agent_loop_from_scratch.adapters.repository.balance_mongo import BalanceMongoRepositoryImpl
from pymongo import MongoClient
import sys
import time

MODEL_NAME = "gemma4"

def load_balance_service(balance_service:BalanceService, functions:dict)-> dict:
    """
    add function to the available functions
    """
    functions["get_balance_by_date"]= balance_service.get_balance_by_date
    return functions


SYSTEM_PROMPT = {
        "role": "system",
        "content": """You are a helpful assistant. 
        Use the tools provided to answer the user's questions.
        After you get the response from the tools, you must respond to the user.
        when calling tool get_balance_by_date the format must be YYYY-MM-DD. always confirm year, month and date if missing with user. do not invent date.
        If the agent_rules say something, you must follow it.
        If the agent_rules says to call another tool, you must call it.
        If the agent_rules says to respond to the user, you must respond to the user.
        Always respond in the same language as the user.
        """
    }


def chat(client, tools:dict, messages:list) -> ChatResponse:
    print(f"calling {MODEL_NAME}")
    start = time.perf_counter()
    response = client.chat(model=MODEL_NAME, messages=messages, think=False, tools=tools.values())
    end = time.perf_counter()
    print(f"gemma4 time taken: {end - start}")
    return response

def _messages_tool_call(messages:list, content:str, tool_name:str):
    messages.append({
        "role": "tool",
        "tool_name": tool_name,
        "content": content
    })

def tool_call_func(client, available_functions, messages, tool_calls):
    for call in tool_calls:
        print("tool call: ", call.function.name)
        print("tool arguments: ", call.function.arguments)
        
        fn = available_functions[call.function.name]
        tool_call_result = fn(**call.function.arguments)
        
        _messages_tool_call(messages, str(tool_call_result), call.function.name)
    
    tool_call_response = chat(client, available_functions, messages)
    messages.append(tool_call_response.message)
    return tool_call_response

def load_env_variables():
    """
    load environment variables
    """
    dotenv.load_dotenv()
    mongodb_uri = os.getenv("MONGO_DB_URI")
    if mongodb_uri is None:
        raise ValueError("MONGO_DB_URI is not set")
    ollama_api_key = os.getenv('OLLAMA_API_KEY')
    if ollama_api_key is None:
        raise ValueError("OLLAMA_API_KEY is not set")
    
    return mongodb_uri, ollama_api_key
    

def main():
    try:
        mongodb_uri, ollama_api_key = load_env_variables()
    except ValueError as e:
        # print the error and exit
        print(e)
        sys.exit(1)
                
    available_functions = {
        "current_time": current_time,
        "current_balance": current_balance,
        "congrats_on_balance": congrats_on_balance,
    }

    client = Client(
        host='https://ollama.com',
        headers={'Authorization': 'Bearer ' + ollama_api_key},
    )
    
    
    # Requires the PyMongo package.
    # https://api.mongodb.com/python/current
    balance_repo = BalanceMongoRepositoryImpl(MongoClient(mongodb_uri))
    # balance_repo = BalanceDicRepositoryImpl()
    balance_service = BalanceServiceImpl(balance_repo)

    available_functions = load_balance_service(balance_service,available_functions)

    messages = [SYSTEM_PROMPT]

    # what is my balance for aug 20
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

        response = chat(client, available_functions, messages)
    
        messages.append(response.message)
    
        while response.message.tool_calls:
            response = tool_call_func(client, available_functions, messages, response.message.tool_calls)
            

        print("agent response: ",response.message.content, " | role: " ,response.message.role)


if __name__ == "__main__":
    main()
