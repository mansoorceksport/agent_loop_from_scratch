from datetime import datetime, date
from zoneinfo import ZoneInfo


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
},
{
    "type": "function",
    "function":{
        "name": "get_balance_by_date",
        "description": "call this function when the user asks for balance for certain date. ",
        "parameters": {
            "type": "object",
            "properties": {
                "date_string": {
                    "type": "string",
                    "description": "the date must be in this format YYYY-MM-DD"
                }
            },
            "required": ["date_string"]
        }
    }
}
]
