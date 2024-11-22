# shared/network_utils.py
import json

def serialize_message(message):
    return json.dumps(message)

def deserialize_message(message_json):
    return json.loads(message_json)
